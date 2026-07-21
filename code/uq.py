import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import warnings
from sklearn.exceptions import ConvergenceWarning
from fig_settings import *
plt.rcParams.update(tex_fonts)

# Ignore convergence warnings for very small clusters (e.g., 1 or 2 points)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# ==========================================
# 1. Core Functions
# ==========================================

def true_function(x):
    return np.sin(2 * np.pi * x)

# ==========================================
# 2. MLL Experiment & Plotting (Averaged)
# ==========================================

print("Running MLL grid search with multiple runs. This may take a moment...")

n_obs = 20
n_runs = 5  # Number of independent runs to average over

# Potential numbers of clusters to test
possible_Ks = np.array([1, 2, 4, 6, 8, 10, 20])

# 2D array to store results: rows = runs, cols = K values
all_mll_results = np.zeros((n_runs, len(possible_Ks)))

plt.figure(figsize=(10, 6))

for run in range(n_runs):
    # 1. Generate Random Data
    # Random uniform sampling instead of linspace creates variation between runs
    X_train = np.random.uniform(-1, 1, n_obs)
    # MUST sort so array_split creates contiguous spatial clusters
    X_train = np.sort(X_train).reshape(-1, 1) 
    
    # Optional: Add a tiny bit of Gaussian noise to y to simulate real data
    # y_train = true_function(X_train).ravel() + np.random.normal(0, 0.05, n_obs)
    y_train = true_function(X_train).ravel()
    
    for i, K in enumerate(possible_Ks):
        # Split data into K contiguous clusters
        X_clusters = np.array_split(X_train, K)
        y_clusters = np.array_split(y_train, K)
        
        total_mll = 0.0
        
        for X_c, y_c in zip(X_clusters, y_clusters):
            if len(X_c) == 0:
                continue
            
            # Re-initialize kernel and GP for each cluster
            kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
            gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-5, n_restarts_optimizer=2, normalize_y=True)
            
            try:
                gp.fit(X_c, y_c)
                # Retrieve the log-marginal likelihood of the optimized kernel
                total_mll += gp.log_marginal_likelihood()
            except Exception:
                # Failsafe: occasionally a very weird random split on 1-2 points 
                # might cause a hard failure in the optimizer. We pass safely.
                pass
            
        # Normalize by total number of observations and store
        all_mll_results[run, i] = total_mll

# Calculate the mean and standard deviation across all runs
mean_mll = np.mean(all_mll_results, axis=0)
std_mll = np.std(all_mll_results, axis=0)

# --- Formatting the Graph ---
fig = plt.figure(figsize=set_size('thesis', fraction=0.5))
plt.plot(possible_Ks, mean_mll, marker='o', color='blue', label=f'Mean ($N_{{obs}}={n_obs}$)')

# Add a shaded region for the standard deviation
plt.fill_between(possible_Ks, 
                 mean_mll - std_mll, 
                 mean_mll + std_mll, 
                 color='blue', alpha=0.2, label='$\pm 1$ Std Dev')

plt.xlabel('$L$')
plt.ylabel('$S_{\\mathrm{global}}$')

# Ensure x-axis only shows integer ticks
plt.xticks(possible_Ks)

plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save and show
plt.savefig("mll_vs_clusters_averaged.pdf", bbox_inches='tight')

print("Experiment complete. Graph saved to 'mll_vs_clusters_averaged.pdf'.")