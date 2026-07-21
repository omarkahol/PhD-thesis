import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Set random seed for exact reproducibility
torch.manual_seed(42)
np.random.seed(42)

# -----------------------------------------------------------
# 1. Physics-Informed DeepONet Architecture
# -----------------------------------------------------------
class PIDeepONet(nn.Module):
    def __init__(self, num_sensors, latent_dim=40):
        super().__init__()
        
        # Branch Network (Processes continuous function values at sensor positions)
        self.branch = nn.Sequential(
            nn.Linear(num_sensors, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, latent_dim)
        )
        
        # Trunk Network (Processes domain evaluation coordinates)
        self.trunk = nn.Sequential(
            nn.Linear(1, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, latent_dim)
        )
        
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, x_branch, x_trunk):
        b_out = self.branch(x_branch).unsqueeze(1) 
        t_out = self.trunk(x_trunk)                
        
        raw_output = torch.sum(b_out * t_out, dim=-1) + self.bias
        
        # HARD CONSTRAINT: Multiply by y * (1 - y). 
        # This guarantees u(0) = 0 and u(1) = 0 absolutely perfectly.
        # x_trunk shape is (batch, num_points, 1), so we squeeze the last dim
        y_dist = x_trunk.squeeze(-1)
        constrained_output = y_dist * (1.0 - y_dist) * raw_output
        
        return constrained_output


# -----------------------------------------------------------
# 2. Mathematical Training Data Generator
# -----------------------------------------------------------
def generate_fourier_data(num_samples, num_sensors, num_colloc, nu=0.01):
    """
    Generates high-fidelity paired data using exact analytical solutions 
    of the 1D Poisson equation via synthetic Fourier coefficients.
    """
    y_sensors = np.linspace(0, 1, num_sensors)
    
    f_sensors = np.zeros((num_samples, num_sensors))
    y_colloc = np.zeros((num_samples, num_colloc, 1))
    f_colloc = np.zeros((num_samples, num_colloc))
    u_true = np.zeros((num_samples, num_colloc))
    
    for i in range(num_samples):
        # Generate random coefficients for modes k = 1, 2, 3
        a = np.random.uniform(-2.5, 2.5, 5)
        y_c = np.random.uniform(0, 1, num_colloc)
        y_colloc[i, :, 0] = y_c
        
        for k_idx, a_k in enumerate(a):
            k = k_idx + 1
            omega = k * np.pi
            
            # f(y) = sum( a_k * sin(k * pi * y) )
            f_sensors[i, :] += a_k * np.sin(omega * y_sensors)
            f_colloc[i, :] += a_k * np.sin(omega * y_c)
            
            # Analytical solution: u(y) = sum( a_k / (nu * omega^2) * sin(omega * y) )
            u_true[i, :] += a_k / (nu * (omega**2)) * np.sin(omega * y_c)
            
    return (torch.tensor(f_sensors, dtype=torch.float32),
            torch.tensor(y_colloc, dtype=torch.float32),
            torch.tensor(f_colloc, dtype=torch.float32),
            torch.tensor(u_true, dtype=torch.float32))


# -----------------------------------------------------------
# 3. Hybrid Loss Computation (Data + Physics Residual)
# -----------------------------------------------------------
def compute_hybrid_loss(model, f_b, y_t, f_c, u_t, nu=0.01):
    # Clone and enable gradient tracking on the trunk evaluation points
    y_t_grad = y_t.clone().detach().requires_grad_(True)
    
    # Forward pass
    u_pred = model(f_b, y_t_grad)
    
    # Term 1: Supervised Data Loss
    loss_data = torch.mean((u_pred - u_t) ** 2)
    
    # Term 2: Physics Loss via Automatic Differentiation
    # First derivative: du/dy
    du_dy = torch.autograd.grad(
        outputs=u_pred,
        inputs=y_t_grad,
        grad_outputs=torch.ones_like(u_pred),
        create_graph=True,
        retain_graph=True
    )[0]
    
    # Second derivative: d^2u/dy^2
    d2u_dy2 = torch.autograd.grad(
        outputs=du_dy,
        inputs=y_t_grad,
        grad_outputs=torch.ones_like(du_dy),
        create_graph=True,
        retain_graph=True
    )[0]
    
    # PDE residual evaluation: -nu * u''(y) - f(y) = 0
    pde_residual = -nu * d2u_dy2.squeeze(-1) - f_c
    loss_pde = torch.mean(pde_residual ** 2)
    
    return loss_data, loss_pde


# -----------------------------------------------------------
# 4. Training Execution Loop
# -----------------------------------------------------------
# Execution parameters
num_sensors = 50
num_colloc = 100
nu_value = 0.01
epochs = 1500
lr = 2e-3

# Generate training arrays
f_sensors_tr, y_colloc_tr, f_colloc_tr, u_true_tr = generate_fourier_data(
    num_samples=800, num_sensors=num_sensors, num_colloc=num_colloc, nu=nu_value
)

# Initialize network configuration
model = PIDeepONet(num_sensors=num_sensors, latent_dim=40)
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

print("Beginning Physics-Informed Training Loop...")
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    
    l_data, l_pde = compute_hybrid_loss(
        model, f_sensors_tr, y_colloc_tr, f_colloc_tr, u_true_tr, nu=nu_value
    )
    
    # Hybrid loss assembly
    total_loss = l_data + 0.1 * l_pde
    
    total_loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 200 == 0 or epoch == 0:
        print(f"Epoch {epoch+1:04d} | Data MSE: {l_data.item():.6f} | PDE Residual MSE: {l_pde.item():.6f}")


# -----------------------------------------------------------
# 5. Out-of-Distribution Testing & Verification
# -----------------------------------------------------------
# Define an entirely unseen target forcing function containing a higher frequency (mode k=4)
f_test_function = lambda y: 2.0 * np.sin(4 * np.pi * y) - 1.0 * np.sin(1 * np.pi * y)
u_test_analytical = lambda y: (2.0 / (nu_value * (4 * np.pi)**2)) * np.sin(4 * np.pi * y) - (1.0 / (nu_value * (1 * np.pi)**2)) * np.sin(1 * np.pi * y)

# Sample the new function at the standard branch sensor grid
y_sensor_grid = np.linspace(0, 1, num_sensors)
f_test_at_sensors = f_test_function(y_sensor_grid)

# Define a high-density, mesh-free grid for continuous output evaluation
y_dense_eval = np.linspace(0, 1, 300)
u_exact_dense = u_test_analytical(y_dense_eval)

# Structure tensors for network forward pass (Injecting batch dimensions)
f_test_tensor = torch.tensor(f_test_at_sensors, dtype=torch.float32).unsqueeze(0) 
y_test_tensor = torch.tensor(y_dense_eval, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

# Model Inference
model.eval()
with torch.no_grad():
    u_predicted_dense = model(f_test_tensor, y_test_tensor).squeeze(0).numpy()

# Calculate Normalized Root Mean Squared Error (NRMSE)
nrmse = np.sqrt(np.mean((u_predicted_dense - u_exact_dense)**2)) / (np.max(u_exact_dense) - np.min(u_exact_dense))
print(f"\nEvaluation Complete. Prediction NRMSE against exact solution: {nrmse:.4%}")


# -----------------------------------------------------------
# 6. Comparative Visual Validation Plot
# -----------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Unseen Input Function Space
ax[0].plot(y_sensor_grid, f_test_at_sensors, 'ro-', label='Sensor Inputs $f(y)$', markersize=4)
ax[0].set_title("Unseen Test Forcing Profile $f(y)$")
ax[0].set_xlabel("Channel Position $y$")
ax[0].set_ylabel("Force Amplitude")
ax[0].grid(True, linestyle="--", alpha=0.6)
ax[0].legend()

# Plot 2: Operator Field Output Comparison
ax[1].plot(y_dense_eval, u_exact_dense, 'k-', linewidth=2.5, label='Exact Analytical Solution')
ax[1].plot(y_dense_eval, u_predicted_dense, 'c--', linewidth=2.5, label='PI-DeepONet Prediction')
ax[1].set_title("Velocity Field Comparison $u(y)$")
ax[1].set_xlabel("Channel Position $y$")
ax[1].set_ylabel("Velocity $u$")
ax[1].grid(True, linestyle="--", alpha=0.6)
ax[1].legend()

plt.tight_layout()
plt.show()