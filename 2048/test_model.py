import torch
import torch.nn as nn
from utilities import *
from generate_lookup_table import generate_lookup_tables_dict
import os


def load_checkpoint_for_testing(checkpoint_path, layer_size=128):
    """
    Load a saved checkpoint and return the Q-network.
    
    Parameters:
        checkpoint_path: Path to the .pth checkpoint file
        layer_size: Size of the hidden layers
        
    Returns:
        Loaded Q-network
    """
    qnet = nn.Sequential(
        nn.Linear(16, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, layer_size),
        nn.ReLU(),
        nn.Linear(layer_size, 4)
    )
    
    checkpoint = torch.load(checkpoint_path)
    qnet.load_state_dict(checkpoint['qnet_state'])
    qnet.eval()  # Set to evaluation mode
    print(f"Model loaded from {checkpoint_path}\n")
    return qnet


def play_game_with_visualization(qnet, lut):
    """
    Play a game of 2048 with the trained model, printing board and Q values at each step.
    
    Parameters:
        qnet: Trained Q-network
        lut: Lookup tables dictionary
    """
    state = split_state(add_random_tile_state(0))
    done = False
    step = 0
    total_reward = 0
    move_names = ["LEFT", "RIGHT", "UP", "DOWN"]
    
    print("\n" + "="*60)
    print("STARTING NEW GAME - OBSERVING MODEL BEHAVIOR")
    print("="*60 + "\n")
    
    while not done:
        print(f"{'─'*60}")
        print(f"STEP {step}")
        print(f"{'─'*60}")
        
        combined_state = combine_state(state)
        print("Board state:")
        print_state(combined_state)
        
        with torch.no_grad():
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            q_values = qnet(state_tensor).squeeze(0)  # (4,)
        
        can_left = lut["can_left"]
        can_right = lut["can_right"]
        valid_moves = check_valid(combined_state, can_left, can_right)
        
        print("Q-values by action:")
        for i, q in enumerate(q_values):
            valid_str = "✓ VALID" if i in valid_moves else "✗ INVALID"
            print(f"  {move_names[i]:6} -> Q = {q:8.4f}  [{valid_str}]")
        
        print()
        
        q_masked = q_values.clone()
        for i in range(4):
            if i not in valid_moves:
                q_masked[i] = float('-inf')
        
        best_action = int(torch.argmax(q_masked).item())
        print(f"Action selected: {move_names[best_action]} (Q = {q_values[best_action]:.4f})")
        
        next_state, reward, done = take_step(state, best_action, lut)
        state = next_state
        total_reward += reward
        step += 1
        
        print(f"Reward for this step: {reward}")
        print()
        
        if not done:
            # input("Press Enter to continue to next step...")
            print()
    
    print("\n" + "="*60)
    print("GAME OVER")
    print("="*60)
    print("\nFinal board state:")
    print_state(combine_state(state))
    
    final_tile_value = max_tile(combine_state(state))
    print(f"Total steps: {step}")
    print(f"Total reward accumulated: {total_reward}")
    print(f"Max tile reached: {2**final_tile_value if final_tile_value > 0 else 0}")
    print("="*60 + "\n")


if __name__ == "__main__":
    lut = generate_lookup_tables_dict()
    
    checkpoint_path = input("Enter path to checkpoint file: ").strip()
    
    if not checkpoint_path:
        print("No checkpoint path provided. Exiting.")
        exit()
    
    if not os.path.exists(checkpoint_path):
        print(f"File '{checkpoint_path}' not found!")
        exit()
    
    qnet = load_checkpoint_for_testing(checkpoint_path)
    
    play_game_with_visualization(qnet, lut)
