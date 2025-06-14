# --- Ascii2las a util to convert ascii based log cuvres into CWLS LAS 2.0 standard format ---
# --- MIT License  ---
# --- https://github.com/edirnandi Date 2025-06-14 ---

import pandas as pd
from tkinter import Tk, filedialog
import os

# --- Constants for LAS 2.0 header (Curve units taken  from SLB curve mnemonic dictionary https://www.apps.slb.com/cmd/) ---
CURVE_INFO = [
    ("DEPT", "M", "Depth (m)"),
    ("GR", "GAPI", "Gamma Ray (API units)"),
    ("RES", "OHM.M", "Resistivity (ohm·m)"),
    ("RHOB", "G/CM3", "Bulk Density (g/cm³)"),
    ("NPHI", "NAPI", "Neutron Porosity (nAPI)"),
    ("DT", "US/FT", "Sonic Transit Time (µs/ft)")
]

# --- File dialog to pick CSV, TXT or Excel file ---
def select_file():
    root = Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a CSV, TXT, or Excel File",
        filetypes=[("Data files", "*.csv *.txt *.xls *.xlsx")]
    )
    return file_path

# --- Read the file into a pandas DataFrame ---
def read_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".txt":
        return pd.read_csv(file_path, sep=None, engine="python")
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format!")

# --- Generate LAS content ---
def generate_las(df, well_name):
    lines = []
    start_depth = df['Depth'].min()
    stop_depth = df['Depth'].max()
    step = df['Depth'].diff().dropna().mode()[0]  # most frequent step
    null_value = -999.25

    lines.append("~Version Information Section")
    lines.append("VERS.                  2.0           : CWLS LOG ASCII STANDARD - VERSION 2.0")
    lines.append("WRAP.                  NO            : One line per depth step\n")

    lines.append("~Well Information Section")
    lines.append("STRT.M                 {:.4f}         : START DEPTH".format(start_depth))
    lines.append("STOP.M                 {:.4f}         : STOP DEPTH".format(stop_depth))
    lines.append("STEP.M                 {:.4f}         : STEP".format(step))
    lines.append("NULL.                 {}           : NULL VALUE".format(null_value))
    lines.append("COMP.                  UNKNOWN        : COMPANY")
    lines.append(f"WELL.                  {well_name}    : WELL NAME")
    lines.append("FLD.                   UNKNOWN        : FIELD")
    lines.append("LOC.                   UNKNOWN        : LOCATION")
    lines.append("PROV.                  UNKNOWN        : PROVINCE")
    lines.append("SRVC.                  UNKNOWN        : SERVICE COMPANY")
    lines.append("DATE.                  2025-06-14     : LOG DATE")
    lines.append("UWI.                   UNKNOWN        : UNIQUE WELL ID\n")

    lines.append("~Curve Information Section")
    lines.append("#MNEM.UNIT              API CODES    CURVE DESCRIPTION")
    for mnemonic, unit, desc in CURVE_INFO:
        lines.append(f"{mnemonic:<6}.{unit:<10}           : {desc}")
    lines.append("")

    lines.append("~ASCII Log Data")
    for _, row in df.iterrows():
        row_vals = [row.get(col, null_value) for col in ['Depth', 'GammaRay', 'Resistivity', 'Density', 'NeutronPorosity', 'SonicDT']]
        row_str = " ".join(f"{val:.4f}" if pd.notnull(val) else f"{null_value:.2f}" for val in row_vals)
        lines.append(row_str)

    return "\n".join(lines)

# --- Save LAS file ---
def save_las_file(content, well_name):
    output_file = f"{well_name}.las"
    with open(output_file, "w") as f:
        f.write(content)
    print(f"LAS file saved as: {output_file}")


# --- Save LAS file to user-selected output folder ---
def save_las_file(content, well_name, output_folder):
    output_path = os.path.join(output_folder, f"{well_name}.las")
    with open(output_path, "w") as f:
        f.write(content)
    print(f"LAS file saved as: {output_path}")

# --- Main Process ---
def main():
    file_path = select_file()
    if not file_path:
        print("No file selected.")
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        print("No output folder selected.")
        return

    df = read_data(file_path)

    # Handle column naming and filtering
    required_columns = ['WellName', 'Depth', 'GammaRay', 'Resistivity', 'Density', 'NeutronPorosity', 'SonicDT']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    for well_name, group_df in df.groupby("WellName"):
        group_df_sorted = group_df.sort_values("Depth")
        las_content = generate_las(group_df_sorted, well_name)
        save_las_file(las_content, well_name, output_folder)

if __name__ == "__main__":
    main()
    
    
    
    
