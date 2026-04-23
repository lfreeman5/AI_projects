import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from collections import deque
from utilities import *
from generate_lookup_table import generate_lookup_tables_dict

layer_size = 128
epsilon = 1.0
batch_size = 64
min_buffer = 2000
buffer = deque(maxlen=100000)


def store(state, action,reward,new_state,done):
    buffer.append((state, action, reward, new_state, done))

def sample(batch_size):
    batch = random.sample(buffer, batch_size)
    states, actions, rewards, next_states, dones = zip(*batch)
    return states, actions, rewards, next_states, dones



if __name__ == "__main__":

    lut = generate_lookup_tables_dict()

    qnet = nn.Sequential(
        nn.Linear(16, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, 4)
    )

    target_net = nn.Sequential(
        nn.Linear(16, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, 4)
    )

    target_net.load_state_dict(qnet.state_dict())

    optimizer = torch.optim.Adam(qnet.parameters(), lr=1e-3)

    def select_action(state, epsilon, lut):
        can_left = lut["can_left"]
        can_right = lut["can_right"]
        valid = check_valid(combine_state(state), can_left, can_right)
        if(random.random() < epsilon):
            return random.choice(valid)
        
        with torch.no_grad():
            s = torch.tensor(state, dtype=torch.float32).unsqueeze(0)  # (1,16)
            q = qnet(s).squeeze(0)  # (4,)
            mask = torch.full((4,), float("-inf"))
            mask[valid] = 0.0
            q_masked = q + mask
            return int(torch.argmax(q_masked).item())

    def training_step(batch, gamma=0.99):
        states, actions, rewards, next_states, dones = batch
        states      = torch.tensor(states, dtype=torch.float32)      # (B,16)
        next_states = torch.tensor(next_states, dtype=torch.float32) # (B,16)
        actions     = torch.tensor(actions, dtype=torch.int64)        # (B,)
        rewards     = torch.tensor(rewards, dtype=torch.float32)     # (B,)
        dones       = torch.tensor(dones, dtype=torch.float32)       # (B,)
        # Predict with the training network
        q_vals = qnet(states)                          # (B,4)
        q_sa   = q_vals.gather(1, actions.unsqueeze(1)).squeeze(1)  # (B,)
        # Predict with the target network
        with torch.no_grad():
            max_next_q = target_net(next_states).max(1)[0] # We know the next state and we use this information to update the net
            target = rewards + gamma * max_next_q * (1-dones)

        loss = F.mse_loss(q_sa, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    for episode in range(10000):
        state = split_state(add_random_tile_state(0))
        done = False
        total_reward = 0

        while not done:
            # Choose action
            action = select_action(state, epsilon, lut)
            # step environment
            next_state, reward, done = take_step(state, action, lut)
            # print_state(combine_state(next_state))
            # print(f"reward, done {reward}  {done}")
            # store in buffer
            store(state, action, reward, next_state, done)
            # update
            state = next_state
            total_reward += reward
            # start learning
            if len(buffer) > min_buffer:
                batch = sample(batch_size)
                training_step(batch)

        # decay exploration
        epsilon = max(0.05, epsilon*0.995)

        print(f"Episode #: {episode}  Total Reward: {total_reward}  Buffer Size: {len(buffer)}")
