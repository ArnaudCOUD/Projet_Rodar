from agent_2 import Agent
from game_lidar import Carte, RobotAI
#from utils import plot_learning_curve
import numpy as np
from os import listdir

CD_MODEL = "C:/Users/myria/arnaud_coudert_robot_ia/model"

def get_state(robot, carte):
        danger = robot.indicateur()
        angle_obj = round(abs((carte.get_angle_obj_robot()/180)-1),3)
        distance_obj = carte.get_distance_obj_robot()
        angle_rotation_robot = robot.angle_print()/360
        sur_obj = int(robot.sur_objectif())
        #print(angle_obj)
        state = [
            danger[0], # 0°
            danger[1], # 45°
            danger[2], # 90°
            danger[3], # 135°
            danger[4], # 180°
            danger[5], # 225°
            danger[6], # 270°
            danger[7], # 315°

            angle_obj, # ° de différence entre robot et objectif
            distance_obj, # distance du robot à l'objectif

            angle_rotation_robot, # angle de rotation du robot
            sur_obj # sur objectif ?
            ]

        return state



if __name__ == '__main__':

    agent = Agent(gamma=0.99,epsilon=1.0, batch_size=64,n_actions=6,
                  eps_end=0.01,input_dims=[12],lr=0.0001)

    scores , eps_history = [], []
    n_games = 50000
    carte = Carte()
    robot = RobotAI()
    robot.deroulement([0,0,0,0,0,0])
    carte.impression_carte(robot.angle_print())

    for i in range(n_games):
        score = 0
        game_over = False
        robot.reset()
        observation = get_state(robot,carte)

        while not game_over :
            action = agent.choose_action(observation)
            liste_action = [0,0,0,0,0,0]
            liste_action[action]=1
            reward, game_over, distance_initiale, distance_objectif = robot.deroulement(liste_action)
            observation_ = get_state(robot,carte)
            score += reward
            agent.store_transition(observation,action,reward,observation_,game_over)
            agent.learn()
            observation = observation_
        scores.append(score)
        eps_history.append(agent.epsilon)

        avg_score = np.mean(scores[-100:])

        print("episode" , i, "score %.2f" % score,
              'average score %.2f' % avg_score,
              'epsilon %.2f' %agent.epsilon)

    x = [i+1 for i in range(n_games)]

    #plot_learning

