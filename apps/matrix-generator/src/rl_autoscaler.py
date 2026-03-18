import numpy as np
import os
import random
import yaml
from . import utils

class RLAutoscaler:
    def __init__(self, workers, slo, max_tenants, base, learning_rate=0.01, gamma=0.95, epsilon=0.2):
        self.workers = workers
        self.slo = float(slo)
        self.max_tenants = int(max_tenants)
        self.base = int(base)
        self.num_worker_types = len(workers)
        self.num_actions = self.base ** self.num_worker_types
        
        # Mapping for in-place support (to be updated by server/generator)
        self.worker_inplace_support = [False] * self.num_worker_types
        self.current_actual_resources = [None] * self.num_worker_types

        # State: [tenants / max_tenants, prev_conf_index / num_actions, completion_time / slo]
        self.state_dim = 3
        self.hidden_dim = 64
        
        # Simple MLP weights (initialized randomly)
        self.W1 = np.random.randn(self.state_dim, self.hidden_dim) * 0.1
        self.b1 = np.zeros((1, self.hidden_dim))
        self.W2 = np.random.randn(self.hidden_dim, self.num_actions) * 0.1
        self.b2 = np.zeros((1, self.num_actions))
        
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        
        self.memory = []
        self.memory_size = 1000
        self.batch_size = 32
        
        self.weights_path = 'Results/rl_weights.npz'
        self.load_weights()

    def load_weights(self):
        if os.path.exists(self.weights_path):
            data = np.load(self.weights_path)
            self.W1 = data['W1']
            self.b1 = data['b1']
            self.W2 = data['W2']
            self.b2 = data['b2']
            print("Loaded RL weights from", self.weights_path)

    def save_weights(self):
        np.savez(self.weights_path, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2)

    def forward(self, state):
        z1 = np.dot(state, self.W1) + self.b1
        a1 = np.maximum(0, z1) # ReLU
        z2 = np.dot(a1, self.W2) + self.b2
        return z2, a1

    def get_action(self, state_vec):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        q_values, _ = self.forward(state_vec)
        return np.argmax(q_values)

    def train(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state in batch:
            # Current Q-values
            q_values, a1 = self.forward(state)
            
            # Target Q-values
            next_q_values, _ = self.forward(next_state)
            target = reward + self.gamma * np.max(next_q_values)
            
            # Gradient descent
            error = q_values[0, action] - target
            
            # Backprop
            # d_z2 = error (only for the chosen action)
            d_z2 = np.zeros((1, self.num_actions))
            d_z2[0, action] = error
            
            d_W2 = np.dot(a1.T, d_z2)
            d_b2 = d_z2
            
            d_a1 = np.dot(d_z2, self.W2.T)
            d_z1 = d_a1 * (a1 > 0)
            
            d_W1 = np.dot(state.T, d_z1)
            d_b1 = d_z1
            
            # Update weights
            self.W2 -= self.lr * d_W2
            self.b2 -= self.lr * d_b2
            self.W1 -= self.lr * d_W1
            self.b1 -= self.lr * d_b1

    def remember(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

    def get_conf_from_index(self, index):
        digits = utils.number_to_base(index, self.base)
        # Pad with zeros
        while len(digits) < self.num_worker_types:
            digits.insert(0, 0)
        return digits

    def calculate_cost(self, conf):
        total_cost = 0
        for i, replicas in enumerate(conf):
            # Cost = replicas * (cpu_cost * cpu_req + mem_cost * mem_req)
            w = self.workers[i]
            cost = replicas * (w.costs['cpu'] * w.resources['cpu'] + w.costs['memory'] * w.resources['memory'])
            total_cost += cost
        return total_cost

    def get_reward(self, completion_time, conf, prev_conf, prev_resources):
        cost = self.calculate_cost(conf)
        
        # SLO Violation penalty
        violation = max(0, float(completion_time) - self.slo)
        slo_penalty = 100 * (violation / self.slo) if violation > 0 else 0
        
        # Transition penalty
        total_transition_penalty = 0
        for i in range(len(conf)):
            if conf[i] > 0 and prev_conf[i] > 0:
                # Check if resources changed (Vertical Scaling)
                res_changed = False
                if prev_resources and prev_resources[i]:
                     # Compare with current intended resources for this worker type
                     if str(self.workers[i].resources['cpu']) != str(prev_resources[i]['cpu']) or \
                        str(self.workers[i].resources['memory']) != str(prev_resources[i]['memory']):
                         res_changed = True
                
                if res_changed:
                    if self.worker_inplace_support[i]:
                        # In-place scaling: Low penalty (Formalism: \Upsilon^k)
                        total_transition_penalty += 2 * conf[i] 
                    else:
                        # Standard scaling: High penalty (Formalism: \Phi^k)
                        total_transition_penalty += 50 * conf[i]
                
                # Horizontal changes (Adding/Removing replicas)
                replica_diff = abs(conf[i] - prev_conf[i])
                total_transition_penalty += 5 * replica_diff
            elif conf[i] > 0 and prev_conf[i] == 0:
                # Cold start penalty for new worker types
                total_transition_penalty += 30 * conf[i]
        
        return -(cost + slo_penalty + total_transition_penalty)

    def decide_and_learn(self, tenants, completion_time, prev_conf_array, prev_actual_resources=None):
        # Update ground truth if provided
        if prev_actual_resources:
            self.current_actual_resources = prev_actual_resources

        # Prepare state
        if not prev_conf_array:
            prev_conf_array = [0] * self.num_worker_types
            prev_conf_index = 0
        else:
            # Convert prev_conf_array to index
            prev_conf_index = 0
            for i, val in enumerate(reversed(prev_conf_array)):
                prev_conf_index += val * (self.base ** i)

        state = np.array([[float(tenants) / self.max_tenants, 
                           float(prev_conf_index) / self.num_actions,
                           float(completion_time) / self.slo]])
        
        # If we have previous experience, learn from it
        if hasattr(self, 'last_state'):
            reward = self.get_reward(completion_time, prev_conf_array, self.last_prev_conf, self.last_prev_resources)
            self.remember(self.last_state, self.last_action, reward, state)
            self.train()
            if random.random() < 0.01: # Periodically save
                self.save_weights()

        # Decide next action
        action = self.get_action(state)
        next_conf = self.get_conf_from_index(action)
        
        # Store for next iteration
        self.last_state = state
        self.last_action = action
        self.last_prev_conf = prev_conf_array
        self.last_prev_resources = prev_actual_resources
        
        return next_conf
