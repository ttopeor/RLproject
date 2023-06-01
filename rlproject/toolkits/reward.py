import numpy as np

def cal_reward(state, goal):

    camera_center = [-0.237, -0.095]
    cube_threshold = 0.02
    goal_threshold = 0.02
    
    #extract data from the input param
    xrob, yrob, yaw, xc, yc = state 
    # print("state: ", state)
    goal_x, goal_y = goal
    # print("goal: ", goal)

    dist_robot2cube = np.sqrt((camera_center[0] - xc)**2 + (camera_center[1] - yc)**2)
    dist_robot2goal = np.sqrt((goal_x - xrob)**2 + (goal_y - yrob)**2)
    
    # Check if the robot arm is 'touching' the cube
    touching_cube = dist_robot2cube <= cube_threshold
    
    # Stage 1: Move to the cube
    if not touching_cube:
        reward = 1/dist_robot2cube
        
    # Stage 2: Move the cube to the goal
    else:
        if dist_robot2goal <= goal_threshold:
            reward = 1000  # Big reward for reaching the goal
        else:
            reward = 1/dist_robot2goal

    if xc == 10 or yc == 10: #if the cube is out of the camera view
        reward = -1000
        
    #print("reward: ", reward)
    return reward