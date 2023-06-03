import numpy as np

lost_cube_prev = 1


def cal_reward(state, goal):
    
    #extract data from the input param
    xrob, yrob, yaw, xc, yc = state
    
    goal_x, goal_y = goal
    
    dist_robot2goal = np.sqrt((goal_x - xrob)**2 + (goal_y - yrob)**2)
    
    reward = 1/dist_robot2goal
    
    return reward

# def cal_reward(state, goal):
    
#     # corner_pos = [[0.15, 0.28], [0.15, 0.15], [-0.15, 0.15], [-0.15, 0.28]]
#     # center_pos = [0, 0.215]

#     # camera_center = [-0.237, -0.095]
#     cube_threshold = 0.02
#     goal_threshold = 0.02
    
#     #extract data from the input param
#     xrob, yrob, yaw, xc, yc = state 
#     # print("state: ", state)
#     goal_x, goal_y = goal
#     # print("goal: ", goal)

#     # dist_robot2cube = np.sqrt((camera_center[0] - xc)**2 + (camera_center[1] - yc)**2)
#     dist_robot2goal = np.sqrt((goal_x - xrob)**2 + (goal_y - yrob)**2)
#     # dist_robot2center = np.sqrt((center_pos[0] - xrob)**2 + (center_pos[1] - yrob)**2)
    
#     # Check if the robot arm is 'touching' the cube
#     # touching_cube = dist_robot2cube <= cube_threshold
#     # loss_the_cube = np.abs(xc) >= 100 or np.abs(yc) >= 100 #if the cube is out of the camera view
    
#     #initial value
#     global lost_cube_prev
#     global total_reward
#     # reward = 1/dist_robot2center * 0.01
#     reward = 0

#     # Stage 1: Find the cube
#     #Use cumulative reward to encourage the robot to find the cube
#     if loss_the_cube:  

#         #if the previous state is not lost the cube, then reset the total reward for cumulative reward
#         if lost_cube_prev == 0:
#             total_reward = 0

#         lost_cube_prev = 1    
#         reward -= 10

#         if xrob > 0.14 or xrob < -0.14 or yrob > 0.27 or yrob < 0.16: #if the cube is out of the frame
#             reward -= 10

#         #prevent saving too many trevial data
#         # if action
#         total_reward += reward
#         return total_reward
        

#     # Stage 2: Move to the cube
#     #use immediate reward to encourage the robot to move to the cube
#     else:
#         # #reset the total reward
#         # total_reward = 0
#         lost_cube_prev = 0
#         if not touching_cube:
#             reward = 1/dist_robot2cube
#         else:
#             reward = 1000 # Big reward for reaching the cube 
#             print("reach the cube")

#         #make total reward equal to the immediate reward
#         total_reward = reward
        
#         return total_reward
    
#     # # Check if the robot arm is 'touching' the cube
#     # touching_cube = dist_robot2cube <= cube_threshold
    
#     # # Stage 1: Move to the cube
#     # if not touching_cube:
#     #     reward = 1/dist_robot2cube
        
#     # # Stage 2: Move the cube to the goal
#     # else:
#     #     if dist_robot2goal <= goal_threshold:
#     #         reward = 1000  # Big reward for reaching the goal
#     #     else:
#     #         reward = 1/dist_robot2goal
        
#     #print("reward: ", reward)
