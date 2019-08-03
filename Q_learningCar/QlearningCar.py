import Game
import brain

env = Game.Game()

RL = brain.DeepQNetwork(n_actions=3,
                  n_features=3,
                  learning_rate=0.01, e_greedy=0.9,
                  replace_target_iter=100, memory_size=2000,
                  e_greedy_increment=0.001,)




first = True
ep_r = 0
ep_i = 1
totale_steps = 0
#env.show_sonar = False
while not env.exit :

	env.render()
	if first:
		action = 0
	else:
		action = RL.choose_action2(observation)

	observation_, reward, done= env.step(action)
	ep_r += reward
	if first :
		first  = False
	else:
		RL.store_transition(observation, action, reward, observation_)

	if totale_steps > 100 :
		RL.learn()
	if done:
		print('episode: ', ep_i,'ep_r: ', round(ep_r, 2),' epsilon: ', round(RL.epsilon, 2))
		ep_i += 1
		ep_r = 0

	observation = observation_
	totale_steps+=1

#RL.save()
#print('brain saved')
