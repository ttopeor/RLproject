import numpy as np
import random

#define the goal and goal threshold
goal_1 = [1.0,1.0]
goal_2 = [10.0,10.0]
threshold = 0.5

previous_stage = None #initially none


def dist_cube_to_goal(xc, yc, goal):
    goal_x = goal[0]
    goal_y = goal[1]
    dist = np.sqrt((xc - goal_x)**2 + (yc - goal_y)**2)
    return dist


def stage_update(state):
    print("state: ", state)

    #check if the state is None
    if any(element is None for element in state):
        print("error from stage.py - No state yet")
        print("using fake random state ")
        state = np.array([random.random() for _ in range(5)])

    #get the cube location from the state data
    xc = state[3]
    yc = state[4]

    #make the previous_stage global variable so that it can memorize
    global previous_stage

    if previous_stage == None:
        current_goal = goal_1
        current_stage = 1

    if previous_stage is not None:
        if previous_stage == 1: # the cube is moving toward goal_1
            #check if goal
            if dist_cube_to_goal(xc, yc, goal_1) <= threshold: #goaled
                current_goal = goal_2
                #flip the stage
                current_stage = 2

            else: #not yet goal
                current_goal = goal_1
                current_stage = 1

        elif previous_stage == 2: # the cube is moving toward goal_2
            if dist_cube_to_goal(xc, yc, goal_2) <= threshold: #goaled
                current_goal = goal_1
                #flip the stage
                current_stage = 1

            else: #not yet goal
                current_goal = goal_2
                current_stage = 2

        else: # stage is nither 1 nor 2
            print("error from stage.py - stage is nither 1 nor 2")
            pass

    # else:
    #     current_stage = 1 #set the stage to 1 initially

    #update the global variable
    previous_stage = current_stage
    
    return state, current_goal, current_stage


