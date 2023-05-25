import json
import math
import time
import threading
import keyboard
import websockets
import asyncio

# Define the WebSocket server URL
ws_server_url = "ws://localhost:8080/api/ws"
hz = 80
spd = 50  # mm/s
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

async def on_message(ws, message):
    global cur
    msg = json.loads(message)
    if msg['event'] == 'StatusUpdate':
        cur = msg['payload']['jointState']['cartesianPosition']

async def on_open(ws):
    global ws_open
    ws_open = True
    msg = {
        'action': 'SetTask',
        'payload': {
            'type': 'ExternalPositionControlTask',
        }
    }
    await ws.send(json.dumps(msg))

async def on_close(ws):
    global ws_open
    ws_open = False

async def on_action(ws, des):
    await ws.send(json.dumps({
        'action': 'ExternalPositionControl',
        'payload': des
    }))

async def run_websocket(ws):
    async with ws:
        await on_open(ws)
        while ws_open:
            message = await ws.recv()
            await on_message(ws, message)

def stop_websocket():
    global stop_event
    stop_event.set()

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
        if des["yaw"] <= 40:
            des["yaw"] += roll_size
    if keyboard.is_pressed("a"):
        if des["yaw"] >= -220:
            des["yaw"] -= roll_size

    des["z"] = 0.070
    des["roll"] = 180
    des["pitch"] = 0

async def print_states(websocket, path):
    global last_pos
    global cur
    global count

    x = round(cur["x"] * 1000, 1)
    y = round(cur["y"] * 1000, 1)
    z = round(cur["yaw"] + 90, 1)
    if (cur["yaw"] + 90 > 180):
        z = round(cur["yaw"] + 90 - 360, 1)

    x_vel = round(((cur["x"] - last_pos["x"]) / hz) * 1000, 1)
    y_vel = round(((cur["y"] - last_pos["y"]) / hz) * 1000, 1)
    z_vel = round(((cur["yaw"] - last_pos["yaw"]) / hz), 1)

    state_data = {
        "x": x,
        "y": y,
        "z": z,
        "x_vel": x_vel,
        "y_vel": y_vel,
        "z_vel": z_vel
    }

    await websocket.send(json.dumps(state_data))

    last_pos = cur
    count += 1

async def start_server():
    server = await websockets.serve(print_states, "localhost", 8087)
    await server.wait_closed()

# Main thread
async def async_main(ws):
    ws_open = True
    asyncio.create_task(run_websocket(ws))
    last_print_time = time.time()
    time.sleep(1)
    des = cur
    if_first_second = 0

    try:
        threading.Thread(target=asyncio.run, args=(start_server(),)).start()
        while not stop_event.is_set():
            start_time = time.time()

            if ws_open:
                process_key_events()
                await on_action(ws, des)
                current_time = time.time()
                if current_time - last_print_time >= 1:
                    if if_first_second == 0:
                        if_first_second = 1
                        last_pos = cur
                    else:
                        await print_states()
                        last_print_time = current_time

            elapsed_time = time.time() - start_time
            remaining_time = (1 / hz) - elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)
            count += 1

    except KeyboardInterrupt:
        print("Stopping...")
        stop_websocket()
    finally:
        print("Stopped")

if __name__ == "__main__":
    ws = websockets.connect(ws_server_url)
    asyncio.run(async_main(ws))
