import numpy as np

def cal_reward(x, y, yaw, xc, yc, gaol_x, goal_y):
    # x, y, yaw, xc, yc = state 
    
    dist_robot2cube = np.sqrt((x - xc)**2 + (y - yc)**2)
    dist_cube2goal = np.sqrt((xc - gaol_x)**2 + (yc - goal_y)**2)
    
    reward = 0
    
    if dist_robot2cube <= 0.2:
        reward = 1000
    else:
        reward = - dist_robot2cube * 10
    
    if dist_cube2goal <= 0.2:
        reward += 1000
    else:
        reward -= dist_cube2goal * 10
    
    return reward
    