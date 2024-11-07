import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Sample Petrophysical data (Gamma Ray curve)
# This is a mock dataset; in practice, you would load your actual log curves data
np.random.seed(42)  # For reproducibility
depth = np.linspace(1000, 2000, 1000)  # Depth from 1000m to 2000m
gamma_ray = np.random.normal(loc=60, scale=10, size=1000)  # Normal GR values around 60 API

# Introduce synthetic spikes in the Gamma Ray curve
#gamma_ray[100] = 150  # Example spike
gamma_ray[400] = 200  # Another spike

# Create a DataFrame to hold the log data
data = pd.DataFrame({'Depth': depth, 'GammaRay': gamma_ray})

# Fit Isolation Forest to detect anomalies (spikes)
iso_forest = IsolationForest(contamination=0.01, random_state=42)  # 1% contamination for spikes
data['Anomaly_Score'] = iso_forest.fit_predict(data[['GammaRay']])

# Anomalies are labeled as -1, normal points as 1
data['Anomaly'] = data['Anomaly_Score'] == -1

# Plot the Gamma Ray log with anomalies highlighted
plt.figure(figsize=(10, 6))
plt.plot(data['Depth'], data['GammaRay'], label='Gamma Ray', color='blue')
plt.scatter(data['Depth'][data['Anomaly']], data['GammaRay'][data['Anomaly']], 
            color='red', label='Detected Spikes', zorder=5)
plt.xlabel('Depth (m)')
plt.ylabel('Gamma Ray (API)')
plt.title('Gamma Ray Log with Detected Spikes')
plt.legend()
plt.show()
