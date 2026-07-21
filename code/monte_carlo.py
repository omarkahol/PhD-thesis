import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

# Optional: Keep your custom imports if you have them locally
from fig_settings import *
plt.rcParams.update(tex_fonts)

def f(x):
    return np.power(x, 2)

n_samples = 10_000
I_curves = []
n_curves = 50

# Correlation parameters
names = ['uncorr', 'corr']
for i, L in enumerate([1e-5, 10]):
    rho = np.exp(-1/L)

    for _ in range(n_curves):
        # 1. Generate the white noise with variance (1 - rho^2)
        noise = np.random.normal(0, np.sqrt(1 - rho**2), n_samples)
        # Initialize the first element to a standard normal to start the sequence properly
        noise[0] = np.random.normal(0, 1) 

        # 2. Apply the AR(1) filter to create correlated samples
        # This natively maintains a standard normal distribution N(0,1)
        correlated_samples = signal.lfilter([1], [1, -rho], noise)
        
        # 3. Calculate the function and the cumulative mean
        f_samples = f(correlated_samples)
        I_curves.append(np.cumsum(f_samples) / np.arange(1, n_samples + 1))

    # --- Plotting the convergence of the Monte Carlo estimate ---
    min_size = 1
    # plt.figure(figsize=set_size('thesis',0.5)) # Use standard if fig_settings is missing
    plt.figure(figsize=set_size('thesis',0.5))
    for I_estimate in I_curves:
        plt.plot(I_estimate[min_size:], color='blue', alpha=0.5, linewidth=0.5)

    # Central limit theorem curves
    ax_samples = np.arange(min_size, n_samples + 1)
    plt.plot(ax_samples, 1.0 + 2*np.sqrt(2.0/ax_samples), color='black', linestyle='--', linewidth=0.8)
    plt.plot(ax_samples, 1.0 - 2*np.sqrt(2.0/ax_samples), color='black', linestyle='--', linewidth=0.8)

    plt.xscale('log')
    plt.xlim(min_size, 10_000)

    plt.axhline(y=1, color='red', linestyle='-', linewidth=0.8)
    plt.xlabel('Number of Samples')
    plt.ylabel('Estimate of Integral')
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.savefig(f'monte_carlo_integration_{names[i]}.pdf', bbox_inches='tight')


# --- Theoretical Distributions ---
def normalpdf(x, mu=0, sigma=1):
    return (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu)/sigma)**2)

# Because we are integrating x^2, the correlation of the squared samples is rho^2
rho_squared = rho**2
factor = np.sqrt((1 - rho_squared)/(1 + rho_squared))
print(f"Effective number of samples factor: {factor:.4f} (rho_squared={rho_squared:.4f})")

I_curves = np.array(I_curves)

# Plot for N_samples = 10
# plt.figure(figsize=set_size('thesis',0.5))
plt.figure(figsize=set_size('thesis',0.5))
I_samples_10 = I_curves[:, 9]  # 10th sample (index 9)
plt.hist(I_samples_10, bins=30, density=True, alpha=0.5, color='blue', label='MC Estimates (N=10)')

mean = 1.0
std_dev_10 = np.sqrt(2 / 10) / factor  # Variance of f(x)
x = np.linspace(mean - 4*std_dev_10, mean + 4*std_dev_10, 100)
plt.plot(x, normalpdf(x, mu=mean, sigma=std_dev_10), color='red', label='CLT Theoretical PDF (N=10)', linewidth=2)
plt.xlabel('Estimate of Integral')
plt.ylabel('Density')
plt.savefig('monte_carlo_distribution_N10.pdf', bbox_inches='tight')

# Plot for N_samples = 10_000
# plt.figure(figsize=set_size('thesis',0.5))
plt.figure(figsize=set_size('thesis',0.5))
I_samples_10k = I_curves[:, -1]  # Last sample (index -1)
plt.hist(I_samples_10k, bins=50, density=True, alpha=0.5, color='blue', label='MC Estimates (N=10,000)')

mean = 1.0
std_dev_10k = np.sqrt(2 / 10_000) / factor  # Variance of f(x)
x = np.linspace(mean - 4*std_dev_10k, mean + 4*std_dev_10k, 100)
plt.plot(x, normalpdf(x, mu=mean, sigma=std_dev_10k), color='red', label='CLT Theoretical PDF (N=10,000)', linewidth=2)
plt.xlabel('Estimate of Integral')
plt.ylabel('Density')
plt.savefig('monte_carlo_distribution_N10000.pdf', bbox_inches='tight')