import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import lasio
from tkinter import Tk, filedialog

# Step 1: Verify LAS 2.0 Conformity
def verify_las_file(las_file):
    try:
        las = lasio.read(las_file, ignore_header_errors=True)
        
        sections = [section.upper() for section in las.sections.keys()]
        #print(f"Sections read from {os.path.basename(las_file)}: {sections}")
        
        errors = []
        
        # Check mandatory sections
        required_sections = ['VERSION', 'WELL', 'CURVES']
        for req in required_sections:
            if req not in sections:
                errors.append(f"Missing section: {req}")  
        
        # Return results
        return "Valid" if not errors else ", ".join(errors)
        
        # Check version
        try:
            version = las.version[0].value
            if version != 2.0:
                errors.append(f"Invalid version: {version} (Expected 2.0)")
        except Exception:
            errors.append("Missing or invalid VERSION information")
        
        # Check WRAP mode
        try:
            wrap_mode = las.version['WRAP'].value.upper()
            if wrap_mode not in ['YES', 'NO']:
                errors.append(f"Invalid WRAP mode: {wrap_mode}")
        except Exception:
            errors.append("Missing WRAP mode in VERSION section")
        
        # Check first curve is DEPT, DEPTH, TIME, or INDEX
        try:
            first_curve = las.curves[0].mnemonic.upper()
            if first_curve not in ['DEPT', 'DEPTH', 'TIME', 'INDEX']:
                errors.append(f"Invalid index curve: {first_curve}")
        except Exception:
            errors.append("Missing or invalid CURVE information")
        
        # Check NULL values
        if 'NULL' not in las.well: 
            errors.append("Missing NULL value in WELL section")
        
        # Check WELL ID is present
        well_id_present = any(mnemonic.upper() in ['UWI', 'WELL'] for mnemonic in las.well.keys())
        if not well_id_present:
            errors.append("Missing Well ID in WELL section (UWI or WELL)")
        
        # Return results
        return "Valid" if not errors else ", ".join(errors)
    except Exception as e:
        return f"Error reading file: {e}"


# Step 2: Interactive File Selection and Verification
def main():
    # Initialize file dialog
    Tk().withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select LAS Files", filetypes=[("LAS files", "*.las")])
    
    if not file_paths:
        print("No files selected.")
        return
    
    # Verify each file
    results = []
    for file in file_paths:
        status = verify_las_file(file)
        results.append({"File": os.path.basename(file), "Status": status})
        print(f"{os.path.basename(file)}: {status}")
    
    # Save results to CSV
    output_df = pd.DataFrame(results)
    output_file = "las_verification_results.csv"
    output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
