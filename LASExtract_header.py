# This Python code use to cut data part from LAS file and leave header only
# Loop over all LAS files in the current directory, and the pattern \176A would therefore match the sequence ~A in LAS file
import os

for filename in os.listdir('.'):
    if filename.lower().endswith('.las'):
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Open a new file to write the header
        with open(f"{filename}.header", 'w') as header_file:
            for line in lines:
                if '\176A' in line:  # Check for the marker \176A
                    break  # Stop when the data part starts
                header_file.write(line)