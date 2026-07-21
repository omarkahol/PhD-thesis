import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit  # Numerically stable sigmoid
from fig_settings import *
plt.rcParams.update(tex_fonts)

# Generate Data
x = np.linspace(-1, 1, 20)
def function(x):
    return np.where(x < 0, -np.cos(2 * np.pi * x), np.cos(2 * np.pi * x))
y = function(x)

jitter = 1e-6
y += jitter * np.random.randn(*y.shape)  # Add small noise for numerical stability

# Create a softer sigmoid so we can see the mixture uncertainty at x=0
beta_sigmoid = 40
def sigmoid(x):
    return expit(beta_sigmoid * x)

# Evaluate distance in the warped space
def cov(x1, x2, s, l):
    return s**2 * np.exp(-0.5 * (x1 - x2)**2 / l**2)

def mean(x, mu):
    return np.full_like(x, mu, dtype=float)

# FIX 1: We explicitly align mu2 with the sigmoid (x > 0)
def mu_piecewise(x, mu1, mu2):
    return mean(x, mu2) * sigmoid(x) + mean(x, mu1) * (1 - sigmoid(x))

# FIX 2: This kernel ONLY handles the smooth latent covariance
def cov_piecewise_latent(x1, x2, s1, l1, s2, l2):
    w2_x1, w2_x2 = sigmoid(x1), sigmoid(x2)
    w1_x1, w1_x2 = 1 - w2_x1, 1 - w2_x2
    
    return (
        w1_x1 * w1_x2 * cov(x1, x2, s1, l1) + 
        w2_x1 * w2_x2 * cov(x1, x2, s2, l2)
    )

# Set parameters
mu1, mu2 = 0, 0
s1, l1 = 1, .2
s2, l2 = 1, .2

# 1. Build Training Matrix
cov_matrix = np.zeros((len(x), len(x)))
for i in range(len(x)):
    for j in range(len(x)):
        cov_matrix[i, j] = cov_piecewise_latent(x[i], x[j], s1, l1, s2, l2)

cov_matrix += jitter * np.eye(len(x))  # Add small noise for numerical stability
mean_vector = mu_piecewise(x, mu1, mu2)

# 2. Build Test Matrices (Latent function only, no noise added)
x_samples = np.linspace(-1, 1, 1000)
cov_matrix_samples = np.zeros((len(x_samples), len(x_samples)))
for i in range(len(x_samples)):
    for j in range(len(x_samples)):
        cov_matrix_samples[i, j] = cov_piecewise_latent(x_samples[i], x_samples[j], s1, l1, s2, l2)

cov_matrix_samples += jitter * np.eye(len(x_samples))  # Add small noise for numerical stability  
mean_vector_samples = mu_piecewise(x_samples, mu1, mu2)

# 3. Build Cross Covariance (Latent relationship between test and train)
cov_cross = np.zeros((len(x_samples), len(x)))
for i in range(len(x_samples)):
    for j in range(len(x)):
        cov_cross[i, j] = cov_piecewise_latent(x_samples[i], x[j], s1, l1, s2, l2)

# Condition the GP on the observed data
alpha = np.linalg.solve(cov_matrix, y - mean_vector)
v = np.linalg.solve(cov_matrix, cov_cross.T)
mu_post = mean_vector_samples + cov_cross @ alpha
cov_post = cov_matrix_samples - cov_cross @ v

from scipy.stats import multivariate_normal
n_samples = 10
samples = multivariate_normal.rvs(mean=mu_post, cov=cov_post, size=n_samples)

# Plot the results
plt.figure(figsize=set_size('thesis',0.5))
plt.plot(x, y, 'kx', markersize=8, label='Observed data')
plt.plot(x_samples, 2 * (sigmoid(x_samples) - 0.5), 'r--', label='Sigmoid Weight')
plt.plot(x_samples, function(x_samples), 'g-', lw=1, label='Posterior Mean')
for i in range(n_samples):
    plt.plot(x_samples, samples[i], 'b-', alpha=0.3,lw=0.5)
    
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.savefig('realizations.pdf',bbox_inches='tight')