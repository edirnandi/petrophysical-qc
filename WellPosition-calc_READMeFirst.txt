
WellPosition-calc, a Python routine to read an Excel file containing Wellname, MD, Inclination, and Azimuth (the 3 parameters)
,then compute Northing, Easting, and TVD using the Minimum Curvature method. 
------------------------------------------------------------------------------------------------------------------------------

1) Input File Requirements:
The input file must be an Excel file (.xlsx or .xls) containing the following columns:

Wellname: Name of the well (string).
MD (ft): Measured depth in feet (numeric).
Inclination (degree): Wellbore inclination in degrees (numeric).
Azimuth (degree): Wellbore azimuth in degrees (numeric).
The data should be sorted by Wellname and MD (ft) for correct calculations.

2) Processing Steps:
- File Selection: A dialog box opens to select the input Excel file.
- Data Validation: Checks if the required columns exist in the selected file.
- Sorting: The data is sorted by Wellname and MD (ft).
- Minimum Curvature Calculation: Computes Northing (ft), Easting (ft), and TVD (ft) using the Minimum Curvature Method. The first row of each well is initialized at (0,0,0).
- Output File Selection:

3) Saving Output:
A dialog box prompts the user to choose the location and name of the output Excel (.xlsx) file. The final DataFrame (including computed Northing, Easting, and TVD) is saved to the chosen Excel file.
