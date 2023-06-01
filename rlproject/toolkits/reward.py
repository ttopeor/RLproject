import numpy as np

def cal_reward(state, goal):
    
    corner_pos = [[0.15, 0.28], [0.15, 0.15], [-0.15, 0.15], [-0.15, 0.28]]
    

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
    loss_the_cube = np.abs(xc) >= 100 or np.abs(yc) >= 100 #if the cube is out of the camera view
    
    # Stage 1: Find the cube
    if loss_the_cube:
        reward = -1000
        if xc > 0.14 or xc < -0.14 or yc > 0.27 or yc < 0.14: #if the cube is out of the frame
            reward -= 1000
    # Stage 2: Move to the cube
    else:
        if not touching_cube:
            reward = 1/dist_robot2cube
        else:
            reward = 10000 # Big reward for reaching the cube 
        print("reach the cube")
    
    # # Check if the robot arm is 'touching' the cube
    # touching_cube = dist_robot2cube <= cube_threshold
    
    # # Stage 1: Move to the cube
    # if not touching_cube:
    #     reward = 1/dist_robot2cube
        
    # # Stage 2: Move the cube to the goal
    # else:
    #     if dist_robot2goal <= goal_threshold:
    #         reward = 1000  # Big reward for reaching the goal
    #     else:
    #         reward = 1/dist_robot2goal
        
    #print("reward: ", reward)
    return reward