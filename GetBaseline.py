import os
import sys
import collections
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pickle

def plotCDF(x, y, filename):
    plt.plot(x, y, '.-')
    plt.xlabel(f"Number of wins (out of {num_iter})")
    plt.ylabel("Probability")
    plt.title("CDF of Wins by Random Algorithm")
    plt.savefig(f'{filename}.jpg')

def load_CDF(filename):
    (x,y) = pickle.load(open(f"{filename}.pickle", 'rb+'))
    plotCDF(x,y, filename)

def CDF(x, filename):
    x = sorted(x)
    y = np.asarray(x)
    y = y/np.sum(y)
    y = list(np.cumsum(y))
    dec = 0
    for i in range(1, len(x)):
        i -= dec
        if x[i] == x[i-1]:
            x.pop(i)
            y.pop(i)
            dec += 1
    pickle.dump((x, y), open(f'{filename}.pickle', 'wb+'))
    plotCDF(x,y, filename)

num_trials = 100
num_iter = 10
pids = []
totals = []
for trial in range(num_trials):
    print(f"Beginning trial {trial}")
    totals.append(collections.defaultdict(int))
    processes = []
    for i in range(num_iter):
        print(f"    Trial {trial}: Starting game {i}")
        p = subprocess.Popen(["python", "Hearts.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(p)
    for p in processes:
        stdout, _ = p.communicate()
        last_line = stdout.splitlines()[-1]
        totals[trial][str(last_line).split()[0][2:]] += 1
random_boi_scores = [x['Dani'] for x in totals]
print("Plotting CDF")
CDF(random_boi_scores, 'random_boi_cdf')
#load_CDF('random_boi_cdf')
