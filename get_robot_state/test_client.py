"""
Goal: send out a request, and reveive two distance
distance1 = the distance of cube center and the first goal
distance2 = the distance of cube center and the second goal

"""

import asyncio
import websockets
import cv2
import numpy as np


async def request_distances():
    # Connect to the WebSocket server
    async with websockets.connect("ws://localhost:8765") as websocket:
        # Send a request to the server for distances
        await websocket.send("distance")

        # Wait for the response from the server
        response = await websocket.recv()
        distance1, distance2, cube_location = response.split(",")

        # Process the distances as needed
        print("Distance 1:", distance1)
        print("Distance 2:", distance2)
        print("Cube location:", cube_location)

       


# Make a request for distances from the server
asyncio.run(request_distances())
