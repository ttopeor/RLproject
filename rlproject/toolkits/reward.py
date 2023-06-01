import numpy as np

def cal_reward(state, goal):

    camera_center = [-0.237, -0.095]
    
    #extract data from the input param
    xrob, yrob, yaw, xc, yc = state 
    # print("state: ", state)
    goal_x, goal_y = goal
    # print("goal: ", goal)
    
    if xc == None or yc == None:
        reward = -10000
        return reward

    dist_robot2cube = np.sqrt((camera_center[0] - xc)**2 + (camera_center[1] - yc)**2)
    dist_rob2goal = np.sqrt((goal_x - xrob)**2 + (goal_y - yrob)**2)
    
    weight = 0
    reward = 0
    
    if dist_robot2cube <= 0.02:
        weight = 1
    else:
        weight = -dist_robot2cube
    
    if dist_rob2goal <= 0.02:
        reward = 100
    else:
        reward = 1/dist_rob2goal
        
    reward = reward * weight

    

    #print("reward: ", reward)

    return reward
    