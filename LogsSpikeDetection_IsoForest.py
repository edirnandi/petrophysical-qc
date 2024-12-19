import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import lasio
from tkinter import Tk, filedialog

# Function to load LAS files interactively
def load_las_files():
    Tk().withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(
        title="Select LAS File(s)",
        filetypes=[("LAS Files", "*.las")]
    )
    return file_paths

# Process each LAS file
def process_las_file(file_path, curve_name):
    las = lasio.read(file_path)
    if curve_name not in las.curves:
        raise ValueError(f"Curve '{curve_name}' not found in {file_path}")

    # Extract depth and specified curve
    depth = las["DEPT"]  # Assuming 'DEPT' is the depth curve name
    curve_data = las[curve_name]

    # Create a DataFrame
    data = pd.DataFrame({'Depth': depth, curve_name: curve_data})

    # Detect spikes using Isolation Forest
    iso_forest = IsolationForest(contamination=0.01, random_state=42)
    data['Anomaly_Score'] = iso_forest.fit_predict(data[[curve_name]])
    data['Anomaly'] = data['Anomaly_Score'] == -1

    # Plot the curve with anomalies highlighted
    plt.figure(figsize=(10, 6))
    plt.plot(data['Depth'], data[curve_name], label=curve_name, color='blue')
    plt.scatter(data['Depth'][data['Anomaly']], data[curve_name][data['Anomaly']], 
                color='red', label='Detected Spikes', zorder=5)
    plt.xlabel('Depth (m)')
    plt.ylabel(f'{curve_name} (API)')
    plt.title(f'{curve_name} Log with Detected Spikes in {file_path}')
    plt.legend()
    plt.show()

# Main script
if __name__ == "__main__":
    print("Select LAS file(s) for processing...")
    las_files = load_las_files()

    if not las_files:
        print("No files selected. Exiting.")
    else:
        curve_name = input("Enter the curve name to process (e.g., GR for Gamma Ray): ").strip()
        for file_path in las_files:
            try:
                print(f"Processing file: {file_path}")
                process_las_file(file_path, curve_name)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
