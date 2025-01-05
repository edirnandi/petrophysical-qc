import os
import pandas as pd
from tkinter import Tk, filedialog
from dlisio import dlis
from pathlib import Path

def validate_dlis_file(dlis_file):
    """
    Validate a DLIS file for conformity to the DLIS/API RP66 standard using both physical and logical file checks.

    Parameters:
    dlis_file (str): The file path of the DLIS file to be validated.
    Returns:
    str: A message indicating the validation result.
    """
    try:
        # Ensure the file exists
        if not os.path.isfile(dlis_file):
            return f"Error: {dlis_file} is not a valid file or does not exist."

        # Load the DLIS file
        physical_file = dlis.load(dlis_file)
        if not physical_file:
            return "File is empty or not a valid DLIS file."

        # Describe the physical file
        description = physical_file.describe()
        print(description)

        # Logical file validation
        logical_file_issues = []
        for logical_file in physical_file:
            # Check logical file metadata
            if not logical_file.origins:
                logical_file_issues.append("Logical file missing origin metadata.")
            
            # Validate channels
            for channel in logical_file.channels:
                if not channel.name:
                    logical_file_issues.append("Channel with missing name found.")
            
            # Validate frames
            for frame in logical_file.frames:
                if not frame.name:
                    logical_file_issues.append("Frame with missing name found.")
              
        if logical_file_issues:
            return "Logical file issues detected: " + "; ".join(logical_file_issues)

        return "DLIS file conforms to the standard."

    except dlis.DlisError as e:
        return f"DLIS-specific error: {e}"
    except Exception as e:
        return f"Error processing file: {e}"

def main():
    # Initialize Tkinter window (hidden)
    Tk().withdraw()

    # Select a folder containing DLIS files
    folder_path = filedialog.askdirectory(title="Select Folder Containing DLIS Files")
    
    if not folder_path:
        print("No folder selected.")
        return
    
    folder_path = Path(folder_path).resolve()
    dlist_files = [str(folder_path / f) for f in os.listdir(folder_path) if f.lower().endswith('.dlis')]
    
    if not dlist_files:
        print("No DLIS files found in the selected folder.")
        return

    # Verify each DLIS file
    results = []
    for file in dlist_files:
        status = validate_dlis_file(file)
        results.append({"File": os.path.basename(file), "Status": status})
        print(f"{os.path.basename(file)}: {status}")
    
    # Save results to CSV
    output_df = pd.DataFrame(results)
    output_file = "dlis_verification_results.csv"
    output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
