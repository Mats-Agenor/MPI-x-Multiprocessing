import math
import time
import os
import sys

import numpy as np
from scipy.integrate import quad

import matplotlib as mpl
import matplotlib.pyplot as plt


### Plot Settings ###
plt.rcParams["axes.labelsize"] = 16
plt.rcParams["xtick.labelsize"] = 16
plt.rcParams["ytick.labelsize"] = 16
plt.rcParams['font.size'] = 16
plt.rc('font', **{'family': 'serif', 'serif': ['Times']})
mpl.rcParams['figure.dpi'] = 100
mpl.rcParams['text.usetex'] = True 
mpl.rcParams['legend.frameon'] = False
mpl.rcParams['font.family'] = 'STIXGeneral'
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['xtick.direction'] = 'in' 
mpl.rcParams['ytick.direction'] = 'in' 
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.right'] = True
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['xtick.minor.size'] = 3
mpl.rcParams['ytick.major.size'] = 5
mpl.rcParams['ytick.minor.size'] = 3
mpl.rcParams['xtick.major.width'] = 0.79
mpl.rcParams['xtick.minor.width'] = 0.79
mpl.rcParams['ytick.major.width'] = 0.79
mpl.rcParams['ytick.minor.width'] = 0.79


# This part detects if the MPI environment is available
try:
    from mpi4py import MPI
    mpi_enabled = True
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
except ImportError:
    mpi_enabled = False
    rank = 0
    size = 1

# Function
def f(x):
    return math.sin(x)

# Integration parameters
a = 0.0
b = math.pi
N = int(1e9)
dx = (b - a) / N

# Files to save execution time
file_mpi = "time_mpi.txt"
file_mp = "time_mp.txt"

# MPI Mode
if mpi_enabled and size > 1:
    comm.Barrier()
    t0 = MPI.Wtime()

    local_sum = 0.0
    for i in range(rank, N, size):
        x = a + i * dx
        local_sum += f(x)

    local_area = local_sum * dx
    total_riemann_area = comm.reduce(local_area, op=MPI.SUM, root=0)

    comm.Barrier()
    t1 = MPI.Wtime()

    if rank == 0:
        exact_integral, _ = quad(f, a, b)
        print("====== MPI ======")
        print(f"Exact integral      : {exact_integral:.10f}")
        print(f"Riemann sum         : {total_riemann_area:.10f}")
        print(f"Error               : {abs(exact_integral - total_riemann_area):.2e}")
        print(f"Runtime      : {t1 - t0:.4f} seconds")
        with open(file_mpi, "a") as fmpi:
            fmpi.write(f"{size} {t1 - t0:.6f}\n")

# Multiprocessing Mode
elif rank == 0:
    from multiprocessing import Pool, cpu_count

    def local_sum(args):
        start, end = args
        total = 0.0
        for i in range(start, end):
            x = a + i * dx
            total += f(x)
        return total

    print("====== Multiprocessing ======")
    proc_range = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    for num_procs in proc_range:
        if num_procs > cpu_count():
            continue
        chunk_size = N // num_procs
        chunks = [(i * chunk_size,
                   (i + 1) * chunk_size if i < num_procs - 1 else N)
                  for i in range(num_procs)]
        t0 = time.time()
        with Pool(processes=num_procs) as pool:
            results = pool.map(local_sum, chunks)
        t1 = time.time()
        total_riemann_area = sum(results) * dx
        exact_integral, _ = quad(f, a, b)
        print(f"{num_procs} processes:")
        print(f"  Riemann sum       : {total_riemann_area:.10f}")
        print(f"  Error             : {abs(exact_integral - total_riemann_area):.2e}")
        print(f"  Runtime    : {t1 - t0:.4f} seconds")
        with open(file_mp, "a") as fmp:
            fmp.write(f"{num_procs} {t1 - t0:.6f}\n")

# Plotting results
if rank == 0 and os.path.exists(file_mpi) and os.path.exists(file_mp):
    def load_times(path):
        with open(path) as f:
            lines = f.readlines()
        return zip(*[(int(p), float(t)) for p, t in (line.split() for line in lines)])

    mpi_procs, mpi_times = load_times(file_mpi)
    mp_procs, mp_times = load_times(file_mp)

    plt.figure(figsize=(8, 5))
    plt.plot(mp_procs, mp_times, marker='o', label="Multiprocessing")
    plt.plot(mpi_procs, mpi_times, marker='s', label="MPI (mpi4py)")
    plt.xlabel("Number of Processes")
    plt.ylabel("Runtime (s)")

    plt.legend()

    plt.tight_layout()
    plt.savefig("comparison_1e9.png")
    plt.close()

