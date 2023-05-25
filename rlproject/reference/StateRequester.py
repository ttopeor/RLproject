"""
Goal: 
request the robot state from the arm and cube state from the validation camera.
send out a request, and reveive two distance and the cube location
send the cube state to the reward() to canculate the reward
return three variable: robot_state, cube_state, and reward




"""

import asyncio
import websocket
import websockets
import cv2
import numpy as np
import json
import threading
import time


class StateRequester:
    def __init__(self):
        #create variable for cube state
        self.cube_loc = [0.0,0.0,0.0]
        self.distance1 = 0.0
        self.distance2 = 0.0

        

        #create variable for robot state
        self.cur = {
            'x': 0,
            'y': 0.150,
            'z': 70,
            'roll': 180,
            'pitch': 0,
            'yaw': -90
        }
        self.des = {
            'x': 0,
            'y': 0,
            'z': 0.070,
            'roll': 180,
            'pitch': 0,
            'yaw': 0
        }

        self.ws_open = False
        self.last_pos = self.cur
        self.count = 0

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.z_vel = 0.0

        #start a thread that keep listen to the robot server
        ws_url = "ws://localhost:8080/api/ws"
        # create a WebSocket object
        self.ws = websocket.WebSocketApp(ws_url, on_message=self.on_message)
        # create and start the WebSocket thread         
        self.server_stop_event = threading.Event() # Create a threading.Event object for stopping the server
        self.ws_thread = threading.Thread(target=self.run_websocket, args=(self.ws,))
        self.ws_thread.start()
        last_print_time = time.time()  # add a timestamp for the last time cur was printed
        time.sleep(1)
        self.des = self.cur
        if_first_second = 0

    #for validation camera
    async def request_cube_state(self):
        # Connect to the valid_cam_server
        async with websockets.connect("ws://localhost:8765") as websocket:
            # print("create websocket")
            # Send a request to the server for distances
            await websocket.send("cube_state")
            # print("sent request")

            # Wait for the response from the server
            response = await websocket.recv()
            distance1, distance2, cube_location = response.split(",")

            # # Process the distances as needed
            # print("Distance 1:", distance1)
            # print("Distance 2:", distance2)
            # print("Cube location:", cube_location)

            #update the cube state
            self.cube_loc = cube_location
            self.distance1 = distance1
            self.distance2 = distance2

            # Process the distances as needed
            print("Distance 1:", self.distance1)
            print("Distance 2:", self.distance2)
            print("Cube location:", self.cube_loc)

            #create a cube state for return
            cube_state = {
                "cube_loc_x" : self.cube_loc[0],
                "cube_loc_y" : self.cube_loc[1],
                "cube_loc_z" : self.cube_loc[2],
                "distance1" : self.distance1,
                "distance2" : self.distance2
            }

            return


    # Add the stop_server method
    def stop_server(self):
        print("stop_server is called")
        self.server_stop_event.set()
        # Close the WebSocket connection
        self.ws.close()

    # Add the join_server method
    def join_server(self):
        print("join_server is called")
        self.ws_thread.join()
        # Close the WebSocket connection
        self.ws.close()

    #steal some function from communication
    def on_message(self, ws, message):
        # global cur
        msg = json.loads(message)
        if msg['event'] == 'StatusUpdate':
            self.cur = msg['payload']['jointState']['cartesianPosition']

    def on_open(self, ws):
        # global ws_open
        self.ws_open = True
        msg = {
            'action': 'SetTask',
            'payload': {
                'type': 'ExternalPositionControlTask',
            }
        }
        ws.send(json.dumps(msg))

    def on_close(self, ws):
        # global ws_open
        self.ws_open = False

    def run_websocket(self, ws):
        # ws.run_forever()
        while not self.server_stop_event.is_set():
            ws.run_forever()
        ws.close()

    def print_robot_states(self, time = 1):
        # global last_pos
        # global cur
        # global count
        
        x = round(self.cur["x"]*1000,1)
        y = round(self.cur["y"]*1000,1)
        z = round(self.cur["yaw"]+90,1)
        if (self.cur["yaw"]+90>180):
            z = round(self.cur["yaw"]+90-360,1)
            
        x_vel =  round(((self.cur["x"]-self.last_pos["x"])/time)*1000,1)
        y_vel =  round(((self.cur["y"]-self.last_pos["y"])/time)*1000,1)
        z_vel =  round(((self.cur["yaw"]-self.last_pos["yaw"])/time),1)
        print(" Px: ",x,"mm"," Py: ",y,"mm"," Pz: ",z,"deg")
        print(" Vx: ",x_vel,"mm/s"," Vy: ",y_vel,"mm/s"," Vz: ",z_vel,"deg/s")
        print("Freq:",self.count/time)
        self.last_pos = self.cur
        self.count = 0
        print("create state")
        state = {
            "x": x,
            "y": y,
            "z": z,
            "x_vel": x_vel,
            "y_vel": y_vel,
            "z_vel": z_vel,
            "freq": self.count/time
        }

    def get_robot_states(self, time = 1):
        # global last_pos
        # global cur
        # global count
        
        x = round(self.cur["x"]*1000,1)
        y = round(self.cur["y"]*1000,1)
        z = round(self.cur["yaw"]+90,1)
        if (self.cur["yaw"]+90>180):
            z = round(self.cur["yaw"]+90-360,1)
            
        x_vel =  round(((self.cur["x"]-self.last_pos["x"])/time)*1000,1)
        y_vel =  round(((self.cur["y"]-self.last_pos["y"])/time)*1000,1)
        z_vel =  round(((self.cur["yaw"]-self.last_pos["yaw"])/time),1)
        self.last_pos = self.cur
        self.count = 0
        print("create state")
        state = {
            "x": x,
            "y": y,
            "z": z,
            "x_vel": x_vel,
            "y_vel": y_vel,
            "z_vel": z_vel,
        }
        return state

    def get_observation(self):
        observation = {}
        robot_state = self.get_robot_states()
        cube_state = await self.request_cube_state()
        observation["robot_state"] = robot_state
        observation["cube_state"] = cube_state

        return observation

    













    # async def request_robot_state(self):
    #     # Connect to the robot arm server
    #     # async with websockets.connect("ws://localhost:8080") as websocket: #check which one works
    #     # async with websockets.connect("ws://localhost:8080/api/ws") as websocket:

    #     #copy the code from Communication.py
    #     ws_url = "ws://localhost:8080/api/ws"
    #     print("create receive websocket")
    #     ws = websocket.WebSocketApp(ws_url, on_message=self.on_message, on_open=self.on_open, on_close=self.on_close)
    #     self.des = self.cur
    #     self.print_states(1)


    













# #for robot state


# # async def receive_message():
# #     async with websockets.connect('ws://localhost:8087') as websocket: # replace with the appropriate websocket URL
# #         while True:
# #             received = await websocket.recv()
# #             state = json.loads(received)
# #             print(f"Received state update: {state}")

# async def receive_state(websocket, path):
#     try:
#         while True:
#             # Receive the state update message from the client
#             message = await websocket.recv()
#             print(f"Received state update: {message}")
            
#             # Process the state update message as needed
#             # ...

#     except websockets.exceptions.ConnectionClosedError:
#         print("Client connection closed.")
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")
#     finally:
#         # Clean up and close the WebSocket connection
#         await websocket.close()

# # Start the WebSocket server
# start_server = websockets.serve(receive_state, "localhost", 8087)

# # Run the server within the event loop
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()