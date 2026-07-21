import numpy as np
import matplotlib.pyplot as plt
import numba as nb
import math

# Left active for your environment!
from fig_settings import *
plt.rcParams.update(tex_fonts)

@nb.njit(fastmath=True)
def target_distribution_fast(x):
    return math.exp(-0.5 * x**2) + math.exp(-0.5 * (x + 2)**2)

@nb.njit(parallel=True, fastmath=True)
def adaptive_parallel_mh_logspaced(total_steps, save_points, initial_sample, seeds):
    n_paths = len(seeds)
    num_saved = len(save_points)
    all_samples = np.zeros((n_paths, num_saved))
    
    target_acceptance = 0.234
    
    for p in nb.prange(n_paths):
        np.random.seed(seeds[p])
        
        current_sample = initial_sample
        current_prob = target_distribution_fast(current_sample)
        
        proposal_std = 1.0 
        accepted_count = 0
        
        save_idx = 0
        for i in range(total_steps):
            gamma = 1.0 / math.sqrt(i + 1)
            
            proposed_sample = current_sample + (np.random.randn() * proposal_std)
            proposed_prob = target_distribution_fast(proposed_sample)
            
            if np.random.rand() < (proposed_prob / current_prob):
                current_sample = proposed_sample
                current_prob = proposed_prob
                accepted_count += 1
            
            if (i + 1) % 100 == 0:
                actual_acceptance = accepted_count / 100
                diff = actual_acceptance - target_acceptance
                proposal_std *= math.exp(gamma * diff)
                accepted_count = 0
                
            if save_idx < num_saved and i == save_points[save_idx]:
                all_samples[p, save_idx] = current_sample
                save_idx += 1
                    
    return all_samples

# --- Execution ---
total_steps = 1_000_000
burn_in = 0  
n_paths = 100
seeds = np.random.randint(0, 10000, size=n_paths)

num_plot_points = 2000
save_points = np.logspace(0, np.log10(total_steps - 1), num=num_plot_points)
save_points = np.unique(save_points.astype(np.int64))

print("Running MCMC...")
samples = adaptive_parallel_mh_logspaced(total_steps, save_points, 0.0, seeds)
print("Done!")


# =========================================================================
# FIGURE 1: Trace Paths (Scale 0.5)
# =========================================================================
plt.figure(figsize=set_size('thesis', 0.5))
x_axis = np.log10(np.maximum(save_points, 1))

for i in range(n_paths):
    plt.plot(x_axis, samples[i], color='blue', alpha=0.3, linewidth=0.1)

plt.xlabel('$\log_{10}(\\mathrm{Iteration})$')
plt.ylabel('$X_i$')
plt.grid(True, linestyle="--", alpha=0.6)
plt.xlim(x_axis[0], x_axis[-1])
plt.savefig('mcmc_trace_paths.pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# FIGURE 2: Stationary Distribution Histogram (Scale 0.5)
# =========================================================================
plt.figure(figsize=set_size('thesis', 0.5))

# Filter transient steps out for accurate stationary distribution mapping
post_burnin_mask = save_points > 10_000
un_burnin_mask = save_points <= 100
converged_samples = samples[:, post_burnin_mask].flatten()

# Plot empirical density bars
plt.hist(converged_samples, bins=80, density=True, alpha=0.5, color='blue', label='MCMC Samples')

# Analytical Target Line Construction
x_range = np.linspace(-6, 4, 500)
y_target = np.array([target_distribution_fast(x) for x in x_range])

# Direct integral normalization
dx = x_range[1] - x_range[0]
y_target_normalized = y_target / (np.sum(y_target) * dx)

plt.plot(x_range, y_target_normalized, color='red', linewidth=1.5, label='Target PDF')
plt.xlabel('$X$')
plt.ylabel('Density')
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig('mcmc_stationary_distribution.pdf', bbox_inches='tight')
plt.close()