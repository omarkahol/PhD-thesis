import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from scipy.special import expit  # Numerically stable sigmoid
from fig_settings import *
plt.rcParams.update(tex_fonts)

# ==========================================
# 1. Core Functions
# ==========================================

def true_function(x):
    return np.sin(2*np.pi*x)

def compute_expected_error(y_true, mu_pred, sigma_pred):
    """
    Computes the expected squared error over the predictive distribution:
    E[(y_true - y_pred)^2] = (y_true - mu)^2 + sigma^2
    """
    return np.mean((y_true - mu_pred)**2 + sigma_pred**2)

def fit_and_predict(X_train, y_train, X_test):
    """Initializes and fits a GP with a small nugget, returning predictions."""
    # RBF kernel with bounds suited for the domain [-1, 1]
    kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
    # alpha=1e-5 adds the small nugget for regularization without noise
    gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-5, n_restarts_optimizer=5)
    gp.fit(X_train, y_train)
    return gp.predict(X_test, return_std=True)

# ==========================================
# 2. Experiment & Plot 1: GP Realizations
# ==========================================

# Set parameters for the single realization plot
n_obs_demo = 30
beta_demo = 5

# Generate Demo Data
X_demo = np.linspace(-1, 1, n_obs_demo).reshape(-1, 1)
y_demo = true_function(X_demo).ravel()

# Split data
mask_left = (X_demo < 0).ravel()
X_left, y_left = X_demo[mask_left], y_demo[mask_left]
X_right, y_right = X_demo[~mask_left], y_demo[~mask_left]

# High-resolution test set
X_test = np.linspace(-1, 1, 1000).reshape(-1, 1)
y_test = true_function(X_test).ravel()

# 1. Global GP Prediction
mu_global, std_global = fit_and_predict(X_demo, y_demo, X_test)

# 2. Clustered GP Predictions
mu_L, std_L = fit_and_predict(X_left, y_left, X_test)
mu_R, std_R = fit_and_predict(X_right, y_right, X_test)

# 3. Blend them using the sigmoid
# p(x) represents the probability/weight for the right cluster
p_right = expit(beta_demo * X_test).ravel()
p_left = 1 - p_right

mu_clustered = p_left * mu_L + p_right * mu_R
var_clustered = (p_left**2) * (std_L**2) + (p_right**2) * (std_R**2)
std_clustered = np.sqrt(var_clustered)

# --- Plotting Realizations ---
fig, ax1 = plt.subplots(figsize=set_size('thesis', fraction=0.5))

# Plot truth and points
ax1.plot(X_test, y_test, 'k--', label="True Function", alpha=0.7)
ax1.scatter(X_left, y_left, color='blue', zorder=5, label="Left Data (x < 0)")
ax1.scatter(X_right, y_right, color='red', zorder=5, label="Right Data (x > 0)")

# Plot Global GP
ax1.plot(X_test, mu_global, 'gray', label="Global GP Mean", alpha=0.8)

ax1.set_xlabel('$x$')
ax1.set_ylabel('$f(x)$')

# Secondary axis for the classifier probability
ax2 = ax1.twinx()
ax2.plot(X_test, p_right, 'g:', linewidth=2)
ax2.set_ylabel('p$(x)$', color='g')
ax2.tick_params(axis='y', labelcolor='g')

plt.tight_layout()
plt.savefig("gp_realizations_demo.pdf", bbox_inches='tight')

# ==========================================
# 3. Grid Search & Plot 2: Error Fraction Heatmap
# ==========================================

print("Running grid search. This may take a moment...")
n_obs_grid = np.hstack([np.arange(4, 151, 4)])  # 10 to 150 points
beta_grid = np.logspace(0, 3, 30)    # Beta from 1 to 100 (log scale)

fraction_matrix = np.zeros((len(beta_grid), len(n_obs_grid)))

for j, n_obs in enumerate(n_obs_grid):
    # Generate dataset
    X_train = np.linspace(-1, 1, n_obs).reshape(-1, 1)
    y_train = true_function(X_train).ravel()
    
    # Split
    mask = (X_train < 0).ravel()
    X_L, y_L = X_train[mask], y_train[mask]
    X_R, y_R = X_train[~mask], y_train[~mask]
    
    # Global GP
    mu_G, std_G = fit_and_predict(X_train, y_train, X_test)
    err_global = compute_expected_error(y_test, mu_G, std_G)
    
    # Clustered GPs
    # Check if we have enough points to fit (requires > 0)
    if len(X_L) > 0 and len(X_R) > 0:
        mu_L, std_L = fit_and_predict(X_L, y_L, X_test)
        mu_R, std_R = fit_and_predict(X_R, y_R, X_test)
    else:
        # Failsafe if grid generates a highly asymmetric split
        continue 
        
    for i, beta in enumerate(beta_grid):
        p_R = expit(beta * X_test).ravel()
        p_L = 1 - p_R
        
        mu_C = p_L * mu_L + p_R * mu_R
        var_C = (p_L**2) * (std_L**2) + (p_R**2) * (std_R**2)
        std_C = np.sqrt(var_C)
        
        err_clustered = compute_expected_error(y_test, mu_C, std_C)
        
        # Calculate ratio
        fraction_matrix[i, j] = err_clustered / err_global

# --- Plotting the Heatmap ---
fig, ax = plt.subplots(figsize=set_size('thesis', fraction=0.5))

N_mesh, B_mesh = np.meshgrid(n_obs_grid, beta_grid)
# Using contourf to display the error fraction
cp = ax.contourf(N_mesh, B_mesh, np.log10(fraction_matrix), levels=20, cmap='coolwarm')
cbar = fig.colorbar(cp)
cbar.set_label('$\\log_{10}(\\frac{\\mathcal{E}_{\\mathrm{clustered}}}{\\mathcal{E}_{\\mathrm{global}}})$')

ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlabel('$N_{\\mathrm{obs}}$')
ax.set_ylabel('$\\gamma$')

plt.tight_layout()
plt.savefig("error_fraction_heatmap.pdf", bbox_inches='tight')