import numpy as np
import pandas as pd
from tkinter import Tk, filedialog
import sys


def minimum_curvature(md1, inc1, azi1, md2, inc2, azi2):
    """
    Calculate position using the Minimum Curvature Method.
    """

    # Convert to radians
    inc1 = np.radians(inc1)
    inc2 = np.radians(inc2)
    azi1 = np.radians(azi1)
    azi2 = np.radians(azi2)

    # Dogleg angle
    cos_beta = (
        np.cos(inc1) * np.cos(inc2)
        + np.sin(inc1) * np.sin(inc2) * np.cos(azi2 - azi1)
    )

    cos_beta = np.clip(cos_beta, -1.0, 1.0)
    beta = np.arccos(cos_beta)

    if np.isclose(beta, 0.0):
        RF = 1.0
    else:
        RF = (2.0 / beta) * np.tan(beta / 2.0)

    delta_MD = md2 - md1

    dN = (
        delta_MD / 2.0
        * (np.sin(inc1) * np.cos(azi1) + np.sin(inc2) * np.cos(azi2))
        * RF
    )

    dE = (
        delta_MD / 2.0
        * (np.sin(inc1) * np.sin(azi1) + np.sin(inc2) * np.sin(azi2))
        * RF
    )

    dTVD = (
        delta_MD / 2.0
        * (np.cos(inc1) + np.cos(inc2))
        * RF
    )

    return dN, dE, dTVD


def process_well_survey():

    Tk().withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Well Survey Excel File",
        filetypes=[("Excel files", "*.xlsx;*.xls")]
    )

    if not file_path:
        print("No file selected.")
        return

    df = pd.read_excel(file_path)

    required_columns = {
        "Wellname",
        "MD (ft)",
        "Inclination (degree)",
        "Azimuth (degree)"
    }

    if not required_columns.issubset(df.columns):
        print("Missing required columns in the Excel file.")
        return

    df = df.dropna(subset=list(required_columns)).reset_index(drop=True)

    # ======================================= 
    # FIXED: Proper per-well MD validation 
    # ======================================= 

    errors = []

    for well, group in df.groupby("Wellname", sort=False):

        prev_md = None

        for idx, row in group.iterrows():
            md = row["MD (ft)"]

            if prev_md is not None and md <= prev_md:
                errors.append(
                    f"{well} | Row {idx}: MD not increasing ({md} <= {prev_md})"
                )

            prev_md = md

    if errors:
      #  print("\nMD Validation Errors Found:\n")
      #  for e in errors:
      #      print(e)
      #  raise ValueError("\nMD validation failed. Fix input data and retry.")
        print("\nMD validation errors detected:")
        for e in errors:
            print(e)

        print("\nFix data and re-run.")
        sys.exit(0)
    # =========================================================

    northing = [0.0]
    easting = [0.0]
    tvd = [0.0]

    for i in range(1, len(df)):

        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        if curr["Wellname"] == prev["Wellname"]:

            dN, dE, dTVD = minimum_curvature(
                prev["MD (ft)"],
                prev["Inclination (degree)"],
                prev["Azimuth (degree)"],
                curr["MD (ft)"],
                curr["Inclination (degree)"],
                curr["Azimuth (degree)"]
            )

            northing.append(northing[-1] + dN)
            easting.append(easting[-1] + dE)
            tvd.append(tvd[-1] + dTVD)

        else:
            northing.append(0.0)
            easting.append(0.0)
            tvd.append(0.0)

    df["Northing (ft)"] = northing
    df["Easting (ft)"] = easting
    df["TVD (ft)"] = tvd

    output_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save Output File"
    )

    if output_path:
        df.to_excel(output_path, index=False, engine="openpyxl")
        print(f"\nFile successfully saved:\n{output_path}")
    else:
        print("File not saved.")


if __name__ == "__main__":
    process_well_survey()