# experiments.py
from simulator import BuildingSimulator
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_once(sim, floor):
    rec = sim.recommend(request_floor=floor)
    best_id = rec['best']['id']
    best_eta = rec['best']['eta']
    # nearest heuristic
    operational = [e for e in sim.elevators if e.state=='operational']
    if not operational:
        nearest = None
        nearest_dist = None
    else:
        nearest = min(operational, key=lambda e: abs(e.current_floor - floor)).id
        nearest_dist = min(operational, key=lambda e: abs(e.current_floor - floor)).current_floor
    return {'floor': floor, 'best_id': best_id, 'best_eta': best_eta, 'nearest_id': nearest}

def run_experiments(n=1000, seed=0):
    random.seed(seed)
    sim = BuildingSimulator(n_elevators=4, top_floor=20, seed=seed)
    rows = []
    for _ in range(n):
        floor = random.randint(0, sim.top_floor)
        rows.append(run_once(sim, floor))
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = run_experiments(500)
    print(df.head())
    # how often recommend == nearest
    match = (df['best_id'] == df['nearest_id']).mean()
    print("Proportion recommended == nearest:", match)
    df['best_eta_numeric'] = df['best_eta'].apply(lambda x: 999 if x is None else x)
    plt.hist(df['best_eta_numeric'], bins=30)
    plt.title('Distribution of recommended ETAs')
    plt.xlabel('ETA (ticks)')
    plt.ylabel('Count')
    plt.savefig('eta_histogram.png')
    print("Saved eta_histogram.png")
