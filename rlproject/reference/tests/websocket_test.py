import websocket
import json
import time
import threading

# define the WebSocket URL
ws_url = "ws://localhost:8080/api/ws"

cur = {
    'x': 0,
    'y': 0,
    'z': 0,
    'roll': 0,
    'pitch': 0,
    'yaw': 0
}

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
    print(des)

def run_websocket(ws):
    ws.run_forever()

def stop_websocket(ws):
    msg = {
        'action': 'Stop',
    }
    ws.send(json.dumps(msg))
    ws.close()

# create a WebSocket object
ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open, on_close=on_close)

# create and start the WebSocket thread
ws_thread = threading.Thread(target=run_websocket, args=(ws,))
ws_thread.start()

# main thread
try:
    while not stop_event.is_set():
        if ws_open:
            on_action(ws, cur)
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
    stop_event.set()
    stop_websocket(ws)
    ws_thread.join()
