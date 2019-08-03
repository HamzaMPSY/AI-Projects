import SnakeGame as sg
import time, random
import numpy as np
from statistics import mean,median
from collections import Counter
import tflearn
import tensorflow as tf
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression


env = sg.SnakeGame()


goal_steps = 2000
score_requirement = 200
initial_games = 1000

def initial_population():  
	training_data = []
	scores = []
	accepted_scores = []
	for _ in range(initial_games):
		print("Simulation game number :",_ + 1 )
		score = 0
		game_memory = []
		prevs_obs = []
		env.reset()
		first = True
		for _ in range(goal_steps):    
		#while True:
			if first:
				action = 0
				first = False
			else:
				action = env.greedy(action)
			#env.render()
			observation, reward, done,info = env.step(action)
			if len(prevs_obs)>0:
				game_memory.append([prevs_obs, action])
			score +=reward
			prevs_obs = observation
			if done :
				break
		if score >= score_requirement :
			accepted_scores.append(score)
			for data in game_memory:
				output = [0,0,0,0]
				output[data[1]] = 1
				training_data.append([data[0],output])
		env.reset()
		scores.append(score)
	training_data_save = np.array(training_data)
	#np.save("training_data_save.npy",training_data_save) 

	print("Average accepted score:",mean(accepted_scores))
	print("Median accepted score:",median(accepted_scores))
	print(Counter(accepted_scores))
	return training_data

def neural_network_model(input_size):
	network = input_data(shape = [None, input_size, 1], name = 'input')
	network = fully_connected(network, 128, activation = 'relu' )
	network = dropout(network, 0.8)
	network = fully_connected(network, 256, activation = 'relu' )
	network = dropout(network, 0.8)

	network = fully_connected(network, 512, activation = 'relu' )
	network = dropout(network, 0.8)

	network = fully_connected(network, 256, activation = 'relu' )
	network = dropout(network, 0.8)

	network = fully_connected(network, 128, activation = 'relu' )
	network = dropout(network, 0.8)

	network = fully_connected(network, 4, activation = 'softmax' )
	network = regression(network, optimizer = 'adam', learning_rate = 1e-3, loss = 'categorical_crossentropy',name = 'targets')

	model = tflearn.DNN(network,tensorboard_dir = 'log')
	return model


def train_model(training_data, model = False):
    X = np.array([i[0] for i in training_data], dtype=np.float64).reshape(-1,len(training_data[0][0]),1)
    y = np.array([i[1] for i in training_data], dtype=np.float64)
    
    if not model :
    	model = neural_network_model(input_size=len(X[0]))

    model.fit({'input':X},{'targets':y},n_epoch=3,snapshot_step = 500, show_metric=True, run_id = 'openaistuff')
    
    return model



def some_random_games_first():
	realScore = []
	for ep in range(10):
		env.reset()
		score = 0
		first = True
		while True:
			env.render()
			if first :
				action = 0
				first = False
			else:
				action =  env.greedy(action)
			observation,reward, done,info = env.step(action)
			if done :
				realScore.append(info)
				break
			score+=reward
	print("Average accepted score:",mean(realScore))
	print("Median accepted score:",median(realScore))
	print(Counter(realScore))



def main():
	tf.reset_default_graph()
	train_data = initial_population()  
	#train_data = np.load('training_data_save.npy')
	model = train_model(train_data)  
	#model.save('snake-AI.tfl')
	#model.load('snake-AI.tfl')
	scores = []
	choices = []
	realScore = []

	for each_game in range(10):
	    score = 0
	    game_memory = []
	    prevs_obs = []
	    env.reset()
	    for _ in range(goal_steps):
	        env.render()
	        if len(prevs_obs) == 0:
	            action = 0
	        else:
	        	action = np.argmax(model.predict(prevs_obs.reshape(-1,len(prevs_obs),1))[0])
	        
	        choices.append(action)
	        new_observation,reward, done, info = env.step(action)
	        prevs_obs = new_observation
	        game_memory.append([prevs_obs,action])
	        score+=reward
	        if done :
	        	realScore.append(info)
	        	break
	    scores.append(score)
	print("Average accepted score:",mean(realScore))
	print("Median accepted score:",median(realScore))
	print(Counter(realScore))
	
if __name__ == '__main__':
	main()
	#some_random_games_first()
	