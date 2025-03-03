import numpy as np
import pandas as pd
from tkinter import Tk, filedialog

def minimum_curvature(md1, inc1, azi1, md2, inc2, azi2):
    """
    Calculate position using the Minimum Curvature Method.
    
    Parameters:
    md1, md2: Measured Depths (ft)
    inc1, inc2: Inclinations (degrees)
    azi1, azi2: Azimuths (degrees)
    
    Returns:
    dN, dE, dTVD: North, East, and True Vertical Depth (ft)
    """
    # Convert degrees to radians
    inc1, inc2 = np.radians(inc1), np.radians(inc2)
    azi1, azi2 = np.radians(azi1), np.radians(azi2)
    
    # Dogleg Severity (β)
    beta = np.arccos(np.cos(inc2 - inc1) - np.sin(inc1) * np.sin(inc2) * (1 - np.cos(azi2 - azi1)))
    
    # Radius Factor (RF)
    if beta == 0:
        RF = 1
    else:
        RF = 2 / beta * np.tan(beta / 2)
    
    # Delta MD
    delta_MD = md2 - md1
    
    # Calculate North, East, and TVD
    dN = (delta_MD / 2) * (np.sin(inc1) * np.cos(azi1) + np.sin(inc2) * np.cos(azi2)) * RF
    dE = (delta_MD / 2) * (np.sin(inc1) * np.sin(azi1) + np.sin(inc2) * np.sin(azi2)) * RF
    dTVD = (delta_MD / 2) * (np.cos(inc1) + np.cos(inc2)) * RF
    
    return dN, dE, dTVD

def process_well_survey():
    # Open file dialog to select Excel file
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Select Well Survey Excel File", filetypes=[("Excel files", "*.xlsx;*.xls")])
    
    if not file_path:
        print("No file selected.")
        return
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Ensure necessary columns exist
    required_columns = {"Wellname", "MD (ft)", "Inclination (degree)", "Azimuth (degree)"}
    if not required_columns.issubset(df.columns):
        print("Missing required columns in the Excel file.")
        return
    
    # Sort by Wellname and MD
    df = df.sort_values(by=["Wellname", "MD (ft)"])
    
    # Initialize output lists
    northing, easting, tvd = [0], [0], [0]
    
    for i in range(1, len(df)):
        if df.iloc[i]["Wellname"] == df.iloc[i-1]["Wellname"]:
            dN, dE, dTVD = minimum_curvature(
                df.iloc[i-1]["MD (ft)"], df.iloc[i-1]["Inclination (degree)"], df.iloc[i-1]["Azimuth (degree)"],
                df.iloc[i]["MD (ft)"], df.iloc[i]["Inclination (degree)"], df.iloc[i]["Azimuth (degree)"]
            )
            northing.append(northing[-1] + dN)
            easting.append(easting[-1] + dE)
            tvd.append(tvd[-1] + dTVD)
        else:
            northing.append(0)
            easting.append(0)
            tvd.append(0)
    
    # Add computed values to DataFrame
    df["Northing (ft)"] = northing
    df["Easting (ft)"] = easting
    df["TVD (ft)"] = tvd
    
    # Save to Excel
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Save Output File")
    if output_path:
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"File saved: {output_path}")
    else:
        print("File not saved.")

if __name__ == "__main__":
    process_well_survey()
