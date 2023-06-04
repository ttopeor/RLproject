import numpy as np
import random
import os

#define the goal and goal threshold
goal_1 = [-7.11713902e-02, 2.14464929e-01]
goal_2 = [0.07088692, 0.21893148]
camera_center = [-0.237, -0.095]
threshold_goal = 0.02 #threshold for the goal
threshold_cube = 0.02 #threshold for the cube


previous_stage = None #initially none
previous_goal = None #initially none


def dist_robot_to_goal(x, y, goal):
    goal_x = goal[0]
    goal_y = goal[1]
    dist = np.sqrt((x - goal_x)**2 + (y - goal_y)**2)
    return dist

def dist_cube_to_robot(xc, yc):
    dist = np.sqrt((camera_center[0] - xc)**2 + (camera_center[1] - yc)**2)
    return dist

def beep():
    os.system('play -np -t alsa synth {} sine {}'.format(0.1, 442))


def stage_update(state):
    

    #get the cube location from the state data
    xc = state[3]
    yc = state[4]
    x = state[0]
    y = state[1]
    done = False
    if dist_robot_to_goal(x, y, goal_1) <= threshold_goal:
        # if dist_cube_to_robot(xc, yc) <= threshold_cube: #goaled
            print("stage.py - goaled 1")
            
            done = True

    return state, goal_1, 1, done



def stage_update_two_goal(state):
    # print("state: ", state)



    #get the cube location from the state data
    xc = state[3]
    yc = state[4]
    x = state[0]
    y = state[1]

    #make the previous_stage global variable so that it can memorize
    global previous_stage
    global previous_goal

    done = False

    if previous_stage == None:
        current_goal = goal_1
        current_stage = 1
        previous_stage = 1
        previous_goal = goal_1
 

    #check if the state is None
    if any(element is None for element in state):
        # print("stage.py - found no cube")
        # print("using previous state and goal")
        state[3] = 10.0
        state[4] = 10.0
        # print("state(after change): ", state)
        return state, previous_goal, previous_stage

    if previous_stage is not None:
        if previous_stage == 1: # the cube is moving toward goal_1
            #check if goal
            if dist_robot_to_goal(x, y, goal_1) <= threshold_goal:
            # if dist_cube_to_robot(xc, yc) <= threshold_cube: #goaled
                print("stage.py - goaled 1")
               
                #flip the stage
                current_goal = goal_2                    
                current_stage = 2
                done = True
                beep()

            else: #not yet goal
                #goaled
                current_goal = goal_1
                #flip the stage
                current_stage = 1

            # else: #not yet goal
            #     current_goal = goal_1
            #     current_stage = 1

        elif previous_stage == 2: # the cube is moving toward goal_2
            if dist_robot_to_goal(x, y, goal_2) <= threshold_goal: #goaled
                # if dist_cube_to_robot(xc, yc) <= threshold_cube: #goaled
                print("stage.py - goaled 2")
                #flip the stage
                current_goal = goal_1
                current_stage = 1
                done = True
                beep()

            else: #not yet goal
                current_goal = goal_2
                current_stage = 2

            # else: #not yet goal
            #     current_goal = goal_2
            #     current_stage = 2

        else: # stage is nither 1 nor 2
            print("error from stage.py - stage is nither 1 nor 2")
            pass

    # else:
    #     current_stage = 1 #set the stage to 1 initially

    #update the global variable
    previous_stage = current_stage
    previous_goal = current_goal
    #print("current_stage: ", current_stage)
    
    return state, current_goal, current_stage, done


