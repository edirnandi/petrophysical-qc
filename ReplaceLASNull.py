# -------------------------------------------------------------------------------------
# Python script to replace LAS Null values in multiple LAS files  e.g. -9999 into -999.25
# take input CWLS LAS format from "curr_dir" and save the edited in the "output_dir"  
#--------------------------------------------------------------------------------------
import glob
import os
import ntpath
import tkinter as tk
from tkinter import filedialog
import re  # Import the regular expression module

# Set up Tkinter root window (it won't appear because we use the dialog box)
root = tk.Tk()
root.withdraw()  # Hide the main Tkinter window

# Prompt user to select the input directory (curr_dir)
curr_dir = filedialog.askdirectory(title="Select the Input Directory with LAS files")
if not curr_dir:
    print("No input directory selected. Exiting.")
    exit()

# Prompt user to select the output directory (output_dir)
output_dir = filedialog.askdirectory(title="Select the Output Directory to Save Edited LAS files")
if not output_dir:
    print("No output directory selected. Exiting.")
    exit()

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Regular expression pattern to match various forms of '-9999' and its decimal variants
pattern = r"-9999(\.0+)?(\.000+)?(\.0000+)?"

# Process each LAS file in the directory
for f in glob.glob(os.path.join(curr_dir, "*.las")):
    with open(f, 'r') as inputfile:
        # Create output file with the same name in the output directory
        output_file_path = os.path.join(output_dir, ntpath.basename(f))
        with open(output_file_path, 'w') as outputfile:
            is_data_section = False  # Flag to track the data section
            
            for line in inputfile:
                # If we encounter the data section (~A), we mark it
                if line.startswith("~A"):
                    is_data_section = True
                # If we encounter another section (~), we exit the data section
                elif line.startswith("~") and is_data_section:
                    is_data_section = False

                # Replace matching values for all occurrences of '-9999' (in header or data section)
                # Use regular expression to replace all versions of '-9999' with '-999.25'
                line = re.sub(pattern, "-999.25", line)

                # Write the (possibly modified) line to the output file
                outputfile.write(line)

print("Processing complete. Edited files saved in:", output_dir)
