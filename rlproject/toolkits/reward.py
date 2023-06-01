import numpy as np

def cal_reward(state, goal):

    camera_center = [-0.237, -0.095]
    
    #extract data from the input param
    xrob, yrob, yaw, xc, yc = state 
    # print("state: ", state)
    goal_x, goal_y = goal
    # print("goal: ", goal)
    
    dist_robot2cube = np.sqrt((camera_center[0] - xc)**2 + (camera_center[1] - yc)**2)
    dist_rob2goal = np.sqrt((goal_x - xrob)**2 + (goal_y - yrob)**2)
    
    reward = 100
    
    if dist_robot2cube <= 0.1:
        reward = 100
    else:
        reward /= dist_robot2cube
    
    if dist_rob2goal <= 0.2:
        reward *= 100
    else:
        reward /= dist_rob2goal
        
    if xc and yc == None:
        reward = -10000
    
    return reward
    