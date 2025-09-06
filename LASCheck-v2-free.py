import pandas as pd
import os
import lasio
from tkinter import Tk, filedialog
from datetime import datetime

# Step 1: Verify LAS 2.0 Conformity
def verify_las_file(las_file, tolerance=1e-3):
    try:
        las = lasio.read(las_file, ignore_header_errors=True)
        sections = [section.upper() for section in las.sections.keys()]
        errors = []

        # Check mandatory sections
        required_sections = ['VERSION', 'WELL', 'CURVES']
        for req in required_sections:
            if req not in sections:
                errors.append(f"Missing section: {req}")

        # Check version
        try:
            version = float(str(las.version['VERS'].value).strip())
            if version != 2.0:
                errors.append(f"Invalid version: {version} (Expected 2.0)")
        except Exception:
            errors.append("Missing or invalid VERSION information")

        # Check WRAP mode
        try:
            wrap_mode = str(las.version['WRAP'].value).strip().upper()
            if wrap_mode not in ['YES', 'NO']:
                errors.append(f"Invalid WRAP mode: {wrap_mode}")
        except Exception:
            errors.append("Missing WRAP mode in VERSION section")

        # Check first curve is DEPT, DEPTH, TIME, or INDEX
        try:
            first_curve = las.curves[0].mnemonic.strip().upper()
            if first_curve not in ['DEPT', 'DEPTH', 'TIME', 'INDEX']:
                errors.append(f"Invalid index curve: {first_curve}")
        except Exception:
            errors.append("Missing or invalid CURVE information")

        # Check NULL values
        if 'NULL' not in las.well:
            errors.append("Missing NULL value in WELL section")

        # Check WELL ID is present (UWI or WELL only)
        well_id_present = any(mnemonic.upper() in ['UWI', 'WELL'] for mnemonic in las.well.keys())
        if not well_id_present:
            errors.append("Missing Well ID in WELL section (UWI or WELL)")

        # Check START and STOP consistency with tolerance
        try:
            # Possible keys to look for
            start_keys = ['STRT', 'START', 'STRT.M', 'START.M', 'STRT.F', 'START.F']
            stop_keys  = ['STOP', 'STOP.M', 'STOP.F']

            # Find actual keys present in LAS well section
            well_keys = {k.upper(): k for k in las.well.keys()}

            found_pairs = []
            for sk in start_keys:
                for ek in stop_keys:
                    # Match STRT with STOP (same suffix if present)
                    if sk.replace("START", "STOP") == ek or sk.replace("STRT", "STOP") == ek:
                        if sk in well_keys and ek in well_keys:
                            found_pairs.append((well_keys[sk], well_keys[ek]))

            if not found_pairs:
                errors.append("Missing START/STOP pair in WELL section")
            else:
                data_start = float(las.index[0])
                data_stop = float(las.index[-1])

                for sk, ek in found_pairs:
                    header_start = float(str(las.well[sk].value).strip())
                    header_stop = float(str(las.well[ek].value).strip())

                    if abs(header_start - data_start) > tolerance:
                        errors.append(
                            f"Mismatch START ({sk}): Header={header_start}, Data={data_start} "
                            f"(Diff={abs(header_start - data_start):.6f} > Tolerance={tolerance})"
                        )
                    if abs(header_stop - data_stop) > tolerance:
                        errors.append(
                            f"Mismatch STOP ({ek}): Header={header_stop}, Data={data_stop} "
                            f"(Diff={abs(header_stop - data_stop):.6f} > Tolerance={tolerance})"
                        )
        except Exception:
            errors.append("Error validating START/STOP consistency in WELL section or data")

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
    
    # Save results to timestamped CSV
    output_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"las_verification_results_{timestamp}.csv"
    output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
