import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# Define risk events with a likelihood (1=Low,2=Moderate,3=High) and impact (1=Low,2=Moderate,3=High)
risks = [
    ("Cyber-security / PHI exposure",        3.3, 3.3),
    ("Data-integrity & version drift",       1.2, 3.1),
    ("Interoperability & conformance drift", 3, 2.1),
    ("Annotation / workflow mis-alignment",  2.5, 2.8),
    ("Cost & operational complexity",        3, 2.5),
    ("Scalability / innovation bottleneck",  2.2, 2.3),
]

# Split out for plotting
names = [r[0] for r in risks]
likelihoods = [r[1] for r in risks]
impacts = [r[2] for r in risks]

# Create the plot with improved styling
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 8))

# Create a custom colormap for the background (green to yellow to red)
colors = [(0.0, 0.6, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0)]  # green, yellow, red
cmap_name = 'risk_levels'
risk_cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=100)

cmap_soft = LinearSegmentedColormap.from_list("soft_traffic",
                                              [(0.16,0.66,0.27),
                                               (0.99,0.86,0.37),
                                               (0.84,0.19,0.16)], N=256)

# or the CB-safe one
cmap_cb = LinearSegmentedColormap.from_list("cb_safe",
                                            [(0.20,0.71,0.29),
                                             (0.13,0.70,0.85),
                                             (0.99,0.75,0.08),
                                             (0.77,0.28,0.30)], N=256)

# Create a meshgrid for the background
x = np.linspace(0.5, 3.5, 100)
y = np.linspace(0.5, 3.5, 100)
X, Y = np.meshgrid(x, y)
# Calculate risk level as product of likelihood and impact
Z = X * Y

# Plot the heatmap background
c = ax.pcolormesh(X, Y, Z, cmap=cmap_soft, alpha=0.6, shading='auto')

# Add a colorbar to explain risk levels
cbar = plt.colorbar(c, ax=ax)
cbar.set_label('Risk Level (Likelihood × Impact)', fontsize=12, fontweight='bold')
cbar.set_ticks([1, 3, 9])
cbar.set_ticklabels(['Low', 'Medium', 'High'])

# Plot risk points with improved markers
scatter = ax.scatter(likelihoods, impacts, s=150,
                    linewidth=2, zorder=5, alpha=0.9)


# Improved text annotations with better positioning and styling
for name, x, y in risks:
    # Calculate risk level for text color
    # The text color of risk labels is determined by the risk level (likelihood × impact):
    risk_level = x * y
    # - Low risk (≤2): darkgreen
    if risk_level <= 2:
        text_color = 'darkgreen'
    # - Medium risk (>2 and ≤6): darkorange
    elif risk_level <= 6:
        text_color = 'darkorange'
    # - High risk (>6): darkred
    else:
        text_color = 'darkred'

    # Position text with offset based on quadrant
    # The position of risk labels is determined by the likelihood (x) value:
    # - For points on the left side (x < 2): offset to the right with left alignment
    # - For points on the right side (x >= 2): offset to the left with right alignment
    offset_x = 0.08 if x < 2 else -0.08
    offset_y = 0.08 if y < 2 else -0.08
    ha = 'left' if x < 2 else 'right'

    # Add text with a white background for better readability
    # The risk label styling is defined by the following parameters:
    # - bbox: Creates a box around the text
    #   - facecolor='white': Sets the background color of the label to white
    #   - alpha=0.7: Makes the background slightly transparent (70% opaque)
    #   - edgecolor='gray': Sets the border color of the label to gray
    #   - boxstyle='round,pad=0.3': Creates rounded corners with 0.3 units of padding
    text_box = ax.text(x + offset_x, y + offset_y, name, fontsize=14, 
                      fontweight='bold', ha=ha, va='center', color=text_color

                     )

# Formatting axes with improved styling
ax.set_xlim(0.5, 3.5)
ax.set_ylim(0.5, 3.5)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(["Low", "Moderate", "High"], fontsize=12)
ax.set_yticks([1, 2, 3])
ax.set_yticklabels(["Low", "Moderate", "High"], fontsize=12)
ax.set_xlabel("Likelihood", fontsize=14, fontweight='bold')
ax.set_ylabel("Impact", fontsize=14, fontweight='bold')
ax.set_title("DICOM Risk Heat Map for Pathology", fontsize=16, fontweight='bold', pad=20)

# Add grid with improved styling
ax.grid(True, linestyle='--', alpha=0.7)

# Add diagonal risk zones
x_diag = np.array([0.5, 3.5])
# Low-Medium boundary
ax.plot(x_diag, 4/3 - x_diag/3, 'k--', alpha=0.5)
# Medium-High boundary
ax.plot(x_diag, 8/3 - x_diag/3, 'k--', alpha=0.5)

# Tight layout for better spacing
plt.tight_layout()

plt.show()
