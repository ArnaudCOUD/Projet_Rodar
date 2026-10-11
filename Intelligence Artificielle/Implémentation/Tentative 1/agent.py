import torch
import random
import numpy as np
from collections import deque
from game_lidar import RobotAI, Carte
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(22, 256, 6)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game, carte):
        danger = game.indicateur()
        angle_obj = carte.get_angle_obj_robot()/180
        distance_obj = carte.get_distance_obj_robot()

        state = [
            danger[0], # 0°
            danger[1], # 18°
            danger[2], # 36°
            danger[3], # 54°
            danger[4], # 72°
            danger[5], # 90°
            danger[6], # 108°
            danger[7], # 126°
            danger[8], # 144°
            danger[9], # 162°
            danger[10], # 180°
            danger[11], # 198°
            danger[12], # 216°
            danger[13], # 234°
            danger[14], # 252°
            danger[15], # 270°
            danger[16], # 288°
            danger[17], # 306°
            danger[18], # 324°
            danger[19], # 342°

            angle_obj,

            distance_obj

            ]

        return np.array(state, dtype=float)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0,0,0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 6)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    record = 0
    record_distance_sans_victoire = 0
    agent = Agent()
    carte = Carte()
    robot = RobotAI()
    robot.deroulement([0,0,0,0,0,0])
    carte.impression_carte(robot.angle_print())
    while True:
        # get old state
        state_old = agent.get_state(robot,carte)
        print(state_old)
        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward,game_over, temps_jeu,distance_initiale, distance = robot.deroulement(final_move) #reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(robot,carte)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # remember
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory, plot result
            robot.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if distance == 0.0:
                score = distance_initiale/temps_jeu
                if score > record:
                    record = score
                    agent.model.save()
            else:
                score = distance_initiale/distance
                if score > record_distance_sans_victoire:
                    record_distance_sans_victoire = score
                    agent.model.save()


if __name__ == '__main__':
    train()
