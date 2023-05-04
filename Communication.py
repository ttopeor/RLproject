import websocket
import json
import time
import threading
import keyboard
import math
# define the WebSocket URL
ws_url = "ws://localhost:8080/api/ws"
hz = 80
spd = 50 #mm/s
count = 0

cur = {
    'x': 0,
    'y': 0.150,
    'z': 70,
    'roll': 180,
    'pitch': 0,
    'yaw': -90
}
des = {
    'x': 0,
    'y': 0,
    'z': 0.070,
    'roll': 180,
    'pitch': 0,
    'yaw': 0
}
last_pos = cur

ws_open = False
stop_event = threading.Event()

def on_message(ws, message):
    global cur
    msg = json.loads(message)
    if msg['event'] == 'StatusUpdate':
        cur = msg['payload']['jointState']['cartesianPosition']

def on_open(ws):
    global ws_open
    ws_open = True
    msg = {
        'action': 'SetTask',
        'payload': {
            'type': 'ExternalPositionControlTask',
        }
    }
    ws.send(json.dumps(msg))

def on_close(ws):
    global ws_open
    ws_open = False

def on_action(ws, des):
    ws.send(json.dumps({
        'action': 'ExternalPositionControl',
        'payload': des
    }))

def run_websocket(ws):
    ws.run_forever()

def stop_websocket(ws):
    msg = {
        'action': 'Stop',
    }
    ws.send(json.dumps(msg))
    ws.close()

# added function to process key events
def process_key_events():
    global des
    step_size = (1/hz)*(spd/1000)
    roll_size = (1/hz)*(spd)

    def is_within_bounds(x, y):
        return y <= 0.280 and x <= 0.150 and y >= 0.150 and x >= -0.150

    current_x, current_y = des["x"], des["y"]

    if keyboard.is_pressed("w"):
        new_y = current_y + math.sin(((-des["yaw"])/180)*math.pi)*step_size
        new_x = current_x + math.cos(((-des["yaw"])/180)*math.pi)*step_size
        if is_within_bounds(new_x, new_y):
            des["y"], des["x"] = new_y, new_x
    if keyboard.is_pressed("s"):
        new_y = current_y - math.sin(((-des["yaw"])/180)*math.pi)*step_size
        new_x = current_x - math.cos(((-des["yaw"])/180)*math.pi)*step_size
        if is_within_bounds(new_x, new_y):
            des["y"], des["x"] = new_y, new_x
    if keyboard.is_pressed("q"):
        new_y = current_y - math.sin(((-des["yaw"]-90)/180)*math.pi)*step_size
        new_x = current_x - math.cos(((-des["yaw"]-90)/180)*math.pi)*step_size
        if is_within_bounds(new_x, new_y):
            des["y"], des["x"] = new_y, new_x
    if keyboard.is_pressed("e"):
        new_y = current_y + math.sin(((-des["yaw"]-90)/180)*math.pi)*step_size
        new_x = current_x + math.cos(((-des["yaw"]-90)/180)*math.pi)*step_size
        if is_within_bounds(new_x, new_y):
            des["y"], des["x"] = new_y, new_x
    if keyboard.is_pressed("d"):
        if(des["yaw"]<=40):
            des["yaw"] += roll_size
    if keyboard.is_pressed("a"):
        if(des["yaw"]>=-220):
            des["yaw"] -= roll_size

    des["z"] = 0.070
    des["roll"] = 180
    des["pitch"] = 0
    

def print_states(time):
    global last_pos
    global cur
    global count
    
    x = round(cur["x"]*1000,1)
    y = round(cur["y"]*1000,1)
    z = round(cur["yaw"]+90,1)
    if (cur["yaw"]+90>180):
        z = round(cur["yaw"]+90-360,1)
        
    x_vel =  round(((cur["x"]-last_pos["x"])/time)*1000,1)
    y_vel =  round(((cur["y"]-last_pos["y"])/time)*1000,1)
    z_vel =  round(((cur["yaw"]-last_pos["yaw"])/time),1)
    print(" Px: ",x,"mm"," Py: ",y,"mm"," Pz: ",z,"deg")
    print(" Vx: ",x_vel,"mm/s"," Vy: ",y_vel,"mm/s"," Vz: ",z_vel,"deg/s")
    print("Freq:",count/time)
    last_pos = cur
    count = 0
def precise_sleep(delay):
    start = time.perf_counter()
    while time.perf_counter() - start < delay:
        pass
    
# main thread
if __name__ == "__main__":
    # create a WebSocket object
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open, on_close=on_close)

    # create and start the WebSocket thread
    ws_thread = threading.Thread(target=run_websocket, args=(ws,))
    ws_thread.start()
    last_print_time = time.time()  # add a timestamp for the last time cur was printed
    time.sleep(1)
    des = cur
    if_first_second = 0
    
    try:
        while not stop_event.is_set():
            start_time = time.time()

            if ws_open:
                process_key_events()  # call the function to process key events
                on_action(ws, des)
                # check if a second has passed since the last print
                current_time = time.time()
                if current_time - last_print_time >= 1:
                    if(if_first_second==0):
                        if_first_second = 1
                        last_pos = cur
                    else:
                        print_states(1)
                        last_print_time = current_time
                    
            # Calculate remaining time and sleep until next iteration
            elapsed_time = time.time() - start_time
            remaining_time = (1/hz) - elapsed_time
            if remaining_time > 0:
                precise_sleep(remaining_time)
            count = count + 1
            
    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()
    finally:
        stop_websocket(ws)
        ws_thread.join()
        print("Stopped")
 
