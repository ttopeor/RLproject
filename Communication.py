import websocket
import json
import time
import threading
import keyboard

# define the WebSocket URL
ws_url = "ws://localhost:8080/api/ws"
hz = 80
spd = 80 #mm/s
count = 0

cur = {
    'x': 0,
    'y': 0,
    'z': 0,
    'roll': 0,
    'pitch': 0,
    'yaw': 0
}
des = {
    'x': 0,
    'y': 0,
    'z': 0,
    'roll': 180,
    'pitch': 0,
    'yaw': -90
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
    roll_size = (1/hz)*(spd/2)
    if keyboard.is_pressed("w"):
        des["y"] += step_size
    elif keyboard.is_pressed("s"):
        des["y"] -= step_size
    elif keyboard.is_pressed("a"):
        des["x"] -= step_size
    elif keyboard.is_pressed("d"):
        des["x"] += step_size
    elif keyboard.is_pressed("z"):
        des["z"] += step_size
    elif keyboard.is_pressed("c"):
        des["z"] -= step_size
    elif keyboard.is_pressed("q"):
        des["yaw"] += roll_size
    elif keyboard.is_pressed("e"):
        des["yaw"] -= roll_size
    des["roll"] = 180
    des["pitch"] = 0


def print_states(time):
    global last_pos
    global cur
    global count
    
    x = round(cur["x"]*1000,1)
    y = round(cur["y"]*1000,1)
    z = round(cur["z"]*1000,1)
    x_vel =  round(((cur["x"]-last_pos["x"])/time)*1000,1)
    y_vel =  round(((cur["y"]-last_pos["y"])/time)*1000,1)
    z_vel =  round(((cur["z"]-last_pos["z"])/time)*1000,1)
    print(" Px: ",x,"mm"," Py: ",y,"mm"," Pz: ",z,"mm")
    print(" Vx: ",x_vel,"mm/s"," Vy: ",y_vel,"mm/s"," Vz: ",z_vel,"mm/s")
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
    
    try:
        while not stop_event.is_set():
            start_time = time.time()

            if ws_open:
                process_key_events()  # call the function to process key events
                on_action(ws, des)
                # check if a second has passed since the last print
                current_time = time.time()
                if current_time - last_print_time >= 1:
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
 
