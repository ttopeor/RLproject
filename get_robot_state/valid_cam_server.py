"""
Goal: receive a request from the client, and return two distnace.
"""
import asyncio
import websockets
import cv2
import numpy as np
import sys
from utils import ARUCO_DICT
import argparse
import time
import math


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera

    return:-
    frame - The frame with the axis drawn on it
    '''

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 1) #for filtering out the high-freq noise
    cv2.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters()


    #corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters,
    #    cameraMatrix=matrix_coefficients,
    #    distCoeff=distortion_coefficients)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, cv2.aruco_dict, parameters=parameters)

        # If markers are detected
    if len(corners) > 0:
        tvec_list = [[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],\
                     [None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None]]
        for i in range(0, len(ids)):
            # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
                                                                       distortion_coefficients)
            #for j in range(rvec.shape[0]):
                #cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec[j, :, :], tvec[j, :, :], 0.01)
            cv2.aruco.drawDetectedMarkers(frame, corners)
            tvec_list[i]=np.round(tvec[0][0],3)
        # print("ID_0:", tvec_list[0],"ID_1:", tvec_list[1],"ID_2:", tvec_list[2],"ID_3:", tvec_list[3],"ID_4:", tvec_list[4], \
        #       "ID_5:", tvec_list[5],"ID_6:", tvec_list[6],"ID_7:", tvec_list[7],"ID_8:", tvec_list[8],"ID_9:", tvec_list[9])
    # np.savetxt('./corners',corners)
    # print(type(corners))
    #print(corners)
    return frame, tvec_list

#set the parameter for the pose estimation
# aruco_dict_type = ARUCO_DICT[args["type"]]
aruco_dict_type = ARUCO_DICT["DICT_6X6_250"]
k=np.load('calibration_matrix.npy')
d=np.load('distortion_coefficients.npy')

# Define the camera configuration
camera = cv2.VideoCapture(2)  # Adjust the camera index if necessary
time.sleep(2.0)

#prepare the center of the frame
print("calculate the center of the frame")
#TODO calculate the center of the frame based on the four markers on the corners

# Capture an image from the camera
ret, frame = camera.read()

#start to do the pose estimation
output, tvec_list = pose_esitmation(frame, aruco_dict_type, k, d)


async def handle_client(websocket, path):
    # This function handles incoming client requests
    try:
        while True:
            # Wait for a request from the client
            request = await websocket.recv()
            if request == "distance":
                # Capture an image from the camera
                ret, frame = camera.read()
                
                #start to do the pose estimation
                output, tvec_list = pose_esitmation(frame, aruco_dict_type, k, d)

                # ID_0 = tvec_list[0]
                # ID_1 = tvec_list[1]
                # ID_2 = tvec_list[2]
                # ID_3 = tvec_list[3]
                # ID_4 = tvec_list[4]
                # ID_5 = tvec_list[5]
                # ID_6 = tvec_list[6]
                # ID_7 = tvec_list[7]
                # ID_8 = tvec_list[8]
                # ID_9 = tvec_list[9]

                print("ID_0:", tvec_list[0],"ID_1:", tvec_list[1],"ID_2:", tvec_list[2],"ID_3:", tvec_list[3],"ID_4:", tvec_list[4], \
              "ID_5:", tvec_list[5],"ID_6:", tvec_list[6],"ID_7:", tvec_list[7],"ID_8:", tvec_list[8],"ID_9:", tvec_list[9], type(tvec_list))
                
                #define the cube location from tvec_list
                cube_location = tvec_list[0]
                
                #define the goal location:
                goal1 = [-0.367, -0.162,  0.652]
                goal2 = [-0.432, -0.295, 1.154]
                

                # Process the image to determine distances
                # Calculate distances and assign them to variables: distance1, distance2
                distance1 = math.sqrt((cube_location[0] - goal1[0])**2 + (cube_location[1] - goal1[1])**2 + (cube_location[2] - goal1[2])**2)
                distance2 = math.sqrt((cube_location[0] - goal2[0])**2 + (cube_location[1] - goal2[1])**2 + (cube_location[2] - goal2[2])**2)

                # Send the distances to the client
                await websocket.send(f"{distance1},{distance2},{cube_location}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def start_server():
    # Create a WebSocket server on localhost, port 8765
    server = await websockets.serve(handle_client, "localhost", 8765)

    # Keep the server running until interrupted
    print("WebSocket server started")
    await server.wait_closed()

# Start the WebSocket server
asyncio.run(start_server())
