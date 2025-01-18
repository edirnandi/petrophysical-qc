This Python code processes .las files in the current directory to extract and save only the header part of each file, discarding the data part. 

What the script does:
It processes each .las file in the directory, extracting and saving only the header part of each file.
The data part (everything after the line containing ~A) is skipped, and it’s not written to the new .header file.


1. Run the Script:
Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux).
Navigate to the directory where both the script and .las files are stored. For example, if the files are in Documents/las_files, run:
cd ~/Documents/las_files

or on Windows:
cd C:\path\to\las_files
Run the script by typing:
> python extract_las_header.py

2. Check the Output and verify the result:
- After running the script, it will create new .header files for each .las file in the same directory.
For example, if you have a file named example.las, the script will create example.las.header containing only the header part of the .las file.
- Verify:
Open the .las.header file (e.g., example.las.header) in any text editor to verify that it contains only the header (and not the data part). The data part is skipped, and the file should end just before the line containing the ~A marker.