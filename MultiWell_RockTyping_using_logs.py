# --- Multi-Well Rock Typing (Electrofacies Classification using Well Logs) ---
# Objective: Automatically cluster multiple wells' log responses (GR, RHOB, NPHI, DT) into consistent electrofacies.
# Use Case: 

import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

# --- Step 1: Browse & Select Multiple Well Files ---
root = Tk()
root.withdraw()  # Hide main Tkinter window
file_paths = filedialog.askopenfilenames(
    title="Select Well Log CSV Files",
    filetypes=[("CSV files", "*.csv")]
)
root.update()

if not file_paths:
    raise FileNotFoundError("⚠️ No CSV files selected. Please select one or more well log files.")

dataframes = []
for file in file_paths:
    well_name = os.path.splitext(os.path.basename(file))[0].replace("well_logs_", "")
    df = pd.read_csv(file)
    df["Well"] = well_name
    dataframes.append(df)

# Combine all selected wells
df_all = pd.concat(dataframes, ignore_index=True)
print(f"✅ Loaded {len(file_paths)} wells, total samples: {len(df_all)}")

# --- Step 2: Feature Selection & Scaling ---
features = ["GR", "RHOB", "NPHI", "DT"]
df_all = df_all.dropna(subset=features)  # Remove rows with missing key logs

X_scaled = StandardScaler().fit_transform(df_all[features])

# --- Step 3: K-Means Clustering (Global Model) ---
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df_all["Electrofacies"] = kmeans.fit_predict(X_scaled)

# --- Step 4: Facies Labeling (Based on Mean GR) ---
cluster_summary = df_all.groupby("Electrofacies")[["GR", "RHOB", "NPHI"]].mean()
print("\nCluster Summary (All Wells):\n", cluster_summary)

facies_map = {}
gr_means = cluster_summary["GR"].sort_values()
for cluster in gr_means.index:
    if gr_means[cluster] < 80:
        facies_map[cluster] = "Sandstone"
    elif gr_means[cluster] < 100:
        facies_map[cluster] = "Siltstone"
    else:
        facies_map[cluster] = "Shale"

df_all["Facies_Label"] = df_all["Electrofacies"].map(facies_map)

# --- Step 5: Visualization Example (One Well) ---
plt.figure(figsize=(6, 5))
subset = df_all[df_all["Well"] == df_all["Well"].unique()[0]]
for label in subset["Facies_Label"].unique():
    part = subset[subset["Facies_Label"] == label]
    plt.scatter(part["GR"], part["RHOB"], label=label, s=40)
plt.xlabel("Gamma Ray (API)")
plt.ylabel("Bulk Density (g/cc)")
plt.title(f"Electrofacies Crossplot (Example Well: {subset['Well'].iloc[0]})")
plt.legend()
plt.show()

# --- Step 6: Depth Track Visualization per Well ---
facies_colors = {"Sandstone": "gold", "Siltstone": "green", "Shale": "gray"}
for well in df_all["Well"].unique():
    wdf = df_all[df_all["Well"] == well]
    plt.figure(figsize=(3, 8))
    plt.scatter(wdf["Facies_Label"], wdf["Depth"], c=wdf["Facies_Label"].map(facies_colors), s=25)
    plt.gca().invert_yaxis()
    plt.xlabel("Facies")
    plt.ylabel("Depth (m)")
    plt.title(f"Facies vs Depth Track: {well}")
    plt.show()

# --- Step 7: Save Combined Techlog-Ready Output ---
output_cols = ["Well", "Depth", "Electrofacies", "Facies_Label"]
output_file = "field_electrofacies_combined.csv"
df_all[output_cols].to_csv(output_file, index=False)

print(f"\n✅ Combined Techlog-ready electrofacies file saved as: {output_file}")
print(f"Includes {len(df_all)} total samples from {len(file_paths)} wells.")
