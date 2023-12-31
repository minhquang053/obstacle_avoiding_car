import numpy as np
import sys
import random
import gym
import warnings
import pickle
import register_env as register_env
from rl_car_env import RlCarEnv

def initialize_q_table(state_space, action_space):
    Qtable = np.zeros((state_space + [action_space])) 
    return Qtable

def epsilon_greedy_policy(Qtable, state, epsilon):
    random_int = random.uniform(0, 1)
    if random_int > epsilon:
        action = np.argmax(Qtable[tuple(state)]) # exploit
    else:
        action = env.action_space.sample() # explore
    return action

def greedy_policy(Qtable, state):
    status = Qtable[tuple(state)]
    if all([s == 0 for s in status]):
        action = env.action_space.sample()
    else:
        action = np.argmax(Qtable[tuple(state)])
    return action

def train(n_training_episodes, min_epsilon, max_epsilon, decay_rate, env, max_steps, Qtable):
    for episode in range(n_training_episodes):
        epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_rate*episode)
        #Reset the environment
        state = env.reset()
        terminated = False

        # repeat
        for step in range(max_steps):
            print(f"Episode {episode}/{n_training_episodes} step {step}")
            action = epsilon_greedy_policy(Qtable, state, epsilon)
            new_state, reward, terminated, _, _ = env.step(action) # Terminated, Truncated, Info are not needed
            env.render()

            # custom indexing for state and action 
            state_action = tuple(np.append(state, action))
            new_state_action = tuple(np.append(new_state, action))

            Qtable[state_action] = Qtable[state_action] + learning_rate * (reward + gamma * np.max(Qtable[new_state_action]) - Qtable[state_action])
            
            if terminated:
                break
            
            state = new_state
            
    env.close()
    return Qtable

def evaluate_agent(env, max_steps, n_eval_episodes, Q):
    episode_rewards = []
    for episode in range(n_eval_episodes):
        state = env.reset()
        total_rewards_ep = 0
    
        for step in range(max_steps):
            env.render()
            # Take the action (index) that have the maximum reward
            print(f"Episode {episode}/{n_eval_episodes} step {step}")
            action = greedy_policy(Q, state)
            new_state, reward, terminated, _, _= env.step(action)
            
            if terminated:
                break
            
            state = new_state
            total_rewards_ep += reward
        
        episode_rewards.append(total_rewards_ep)
    env.close()
    mean_reward = np.mean(episode_rewards)
    std_reward = np.std(episode_rewards)

    return mean_reward, std_reward

warnings.filterwarnings("ignore", category=UserWarning, module="gym")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="gym")

env = gym.make("RlCar-v0")

print("Observation Space:", env.observation_space)
print("Sample observation:", env.observation_space.sample())

print("Action Space Shape:", env.action_space.n)
print("Action Space Sample:", env.action_space.sample())

state_space = env.state_space
action_space = env.action_space.n

# Training parameters
n_training_episodes = 15
learning_rate = 0.5

# Evaluation parameters
n_eval_episodes = 100      

# Environment parameters
env_id = "RlCar-v0"   
max_steps = 600
gamma = 0.9               
eval_seed = []             

# Exploration parameters
max_epsilon = 0.95           
min_epsilon = 0.05           
decay_rate = 0.0005

if len(sys.argv) == 1:
    print("**** Error ****[!]\nRun \'python3 q_learning.py train\' \nor \'python3 q_learning.py evaluate\'")
    sys.exit()
proc = sys.argv[1]

if proc == "train":
    try:    
        with open('q_table.pkl', 'rb') as f:
            Qtable_rlcar = pickle.load(f) 
    except FileNotFoundError:
        print("[!] No existing q-table found. Initializing a new one")
        Qtable_rlcar = initialize_q_table(state_space, action_space)
    
    # Start training
    Qtable_rlcar = train(n_training_episodes, min_epsilon, max_epsilon, decay_rate, env, max_steps, Qtable_rlcar)
    print(Qtable_rlcar)

    with open('q_table.pkl', 'wb') as f:
        pickle.dump(Qtable_rlcar, f)
elif proc == "evaluate":
    with open('q_table.pkl', 'rb') as f:
        Qtable_rlcar = pickle.load(f)

    # Evaluate our Agent
    mean_reward, std_reward = evaluate_agent(env, max_steps, n_eval_episodes, Qtable_rlcar)
    print(f"Mean_reward={mean_reward:.2f} +/- {std_reward:.2f}")
elif proc == "check":
    with open('q_table.pkl', 'rb') as f:
        Qtable_rlcar = pickle.load(f)
    
    state_space = env.state_space
    action_space = env.action_space.n
    
    # Print the Q-table in the specified format
    header = ["Straight", "Left", "Right", "RZ", "LZ", "RS", "LS"]
    header_str = "{:^8}" * env.action_space.n + " | " + "{:^4}" * len(state_space)
    print(header_str.format(*header))

    for i in range(state_space[0]):
        for j in range(state_space[1]):
            for k in range(state_space[2]):
                for l in range(state_space[3]):
                    row_values = Qtable_rlcar[i, j, k, l, :]
                    state_values = [i, j, k, l]
                    row_str = "{:^8.2f}" * len(row_values) + " | " + "{:^4}" * len(state_values)
                    print(row_str.format(*row_values, *state_values))
    
else:
    print("**** Error ****[!]\nRun \'python3 q_learning.py train\' \nor \'python3 q_learning.py evaluate\'")

