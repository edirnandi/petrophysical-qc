Python script to interactively verify multiple LAS files for conformity with the CWLS LAS 2.0 specification and output the results as a CSV file:

Key Steps:
Interactive File Input: Prompt the user to select multiple LAS files.
Verification Process: Check LAS file headers, sections (~V, ~W, ~C, ~A), and format requirements.
Output Results: Save the verification status of each file as a CSV.

Key Features:
LAS File Verification:

Checks for mandatory sections (~VERSION, ~WELL, ~CURVE, ~ASCII).
Validates LAS version (must be 2.0).
Ensures the index curve is one of DEPT, DEPTH, TIME, or INDEX.
Verifies the presence of NULL values.
Verifies the presence of  WELL (UWI, WELL, API)
Interactive File Selection:

Allows users to select multiple LAS files using a graphical file dialog.
Output:

Results are saved to las_verification_results.csv, listing each file and its verification status.



Required Libraries:
lasio pandas numpy matplotlib 
