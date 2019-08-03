import SnakeGame as sg
from brain import DeepQNetwork

env = sg.SnakeGame()

RL = DeepQNetwork(n_actions=4,
                  n_features=24,
                  learning_rate=0.01, e_greedy=0.9,
                  replace_target_iter=100, memory_size=2000,
                  e_greedy_increment=0.001,)

total_steps = 0


for i_episode in range(2000):
    env.reset()
    ep_r = 0
    first = True
    while True:
        env.render()
        if first:
        	action = 0
        else:
        	action = RL.choose_action2(observation)

        observation_, reward, done, info = env.step(action)
        if done:
        	reward = -10
        if first :
        	first = False
        else:
        	RL.store_transition(observation, action, reward, observation_)
        ep_r += reward
        if total_steps > 100:
            RL.learn()

        if done:
            print('episode: ', i_episode,'ep_r: ', round(ep_r, 2),' epsilon: ', round(RL.epsilon, 2))
            break

        observation = observation_
        total_steps += 1

