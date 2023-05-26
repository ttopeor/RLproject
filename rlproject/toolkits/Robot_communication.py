import websocket
import json
import time
import threading
import math
import numpy as np
# define the WebSocket URL
ws_url = "ws://localhost:8080/api/ws"
hz = 80
ws = None

cur = {
    'x': 0,
    'y': 0.221,
    'z': 0.070,
    'roll': 180,
    'pitch': 0,
    'yaw': -90
}
des = {
    'x': 0,
    'y': 0.221,
    'z': 0.070,
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


def action(x_speed, y_speed, yaw_speed):
    global des
    step_size = (1/hz)*(1/1000)
    roll_size = (1/hz)*(1)

    def is_within_bounds(value, lower_bound, upper_bound, direction):
        if direction == 1:  # moving towards upper_bound
            return value <= upper_bound
        else:  # moving towards lower_bound
            return value >= lower_bound

    current_x, current_y = des["x"], des["y"]

    new_y = current_y + y_speed * step_size
    y_direction = np.sign(y_speed)
    if is_within_bounds(new_y, 0.150, 0.280, y_direction):
        des["y"] = new_y

    new_x = current_x + x_speed * step_size
    x_direction = np.sign(x_speed)
    if is_within_bounds(new_x, -0.150, 0.150, x_direction):
        des["x"] = new_x

    if yaw_speed != 0:
        new_yaw = des["yaw"] + yaw_speed * roll_size
        if new_yaw <= 40 and new_yaw >= -220:
            des["yaw"] = new_yaw

    des["z"] = 0.070
    des["roll"] = 180
    des["pitch"] = 0


def precise_sleep(delay):
    start = time.perf_counter()
    while time.perf_counter() - start < delay:
        pass


# main thread
if __name__ == "__main__":
    # create a WebSocket object
    ws = websocket.WebSocketApp(
        ws_url, on_message=on_message, on_open=on_open, on_close=on_close)

    # create and start the WebSocket thread
    ws_thread = threading.Thread(target=run_websocket, args=(ws,))
    ws_thread.start()

    time.sleep(1)
    des = cur

    try:
        while not stop_event.is_set():
            start_time = time.time()
            if ws_open:
                action(10, 0, 0)  # call the function to process key events
                on_action(ws, des)
            # Calculate remaining time and sleep until next iteration
            elapsed_time = time.time() - start_time
            remaining_time = (1/hz) - elapsed_time
            if remaining_time > 0:
                precise_sleep(remaining_time)

    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()
    finally:
        stop_websocket(ws)
        ws_thread.join()
        print("Stopped")
