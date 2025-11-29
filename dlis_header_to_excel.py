# ---------------------------------------------------------------------------------------
# dlis_header_to_excel.py
# 
# DLIS header-only extractor (Tkinter + dlisio),generate separate Excel files per DLIS file.
#
# --------------------------------------------------------------------------------------
import os
import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, messagebox
from dlisio import dlis

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def normalize_scalar(val):
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)

def first_attr(obj, names, default=None):
    for n in names:
        if hasattr(obj, n):
            try:
                v = getattr(obj, n)
                return v() if callable(v) else v
            except:
                continue
    return default


# --------------------------------------------------
# Vendor-specific unwrapping
# --------------------------------------------------

def unwrap_vendor_specific(param):
    # Schlumberger
    slb_fields = [
        "value", "v", "val", "scalar", "scalars",
        "data", "elements", "contents",
        "text", "enum", "values"
    ]
    for f in slb_fields:
        if hasattr(param, f):
            try:
                v = getattr(param, f)
                if callable(v): v = v()
                if v not in [None, ""]:
                    return v
            except:
                pass

    # Halliburton
    hal_fields = ["getvalue", "representation_code", "array"]
    for f in hal_fields:
        if hasattr(param, f):
            try:
                v = getattr(param, f)
                v = v() if callable(v) else v
                if v not in [None, ""]:
                    return v
            except:
                pass

    # Baker / INTEQ
    baker_fields = ["data", "values", "elements"]
    for f in baker_fields:
        if hasattr(param, f):
            try:
                v = getattr(param, f)
                v = v() if callable(v) else v
                if v not in [None, ""]:
                    return v
            except:
                pass

    return None


def unwrap_param_value(param):
    try_val = unwrap_vendor_specific(param)
    if try_val not in [None, ""]:
        val = try_val
    else:
        try:
            val = param.getvalue() if hasattr(param, "getvalue") else getattr(param, "value", None)
        except:
            val = None

    # Recursive peeling
    seen = set()
    while True:
        if id(val) in seen:
            break
        seen.add(id(val))

        next_val = None
        if hasattr(val, "getvalue"):
            try: next_val = val.getvalue()
            except: pass
        elif hasattr(val, "value"):
            try: next_val = val.value
            except: pass

        if next_val is None or next_val is val:
            break
        val = next_val

    # data_array → numpy array
    if hasattr(val, "array"):
        try: val = val.array
        except: pass

    # array → CSV string
    if isinstance(val, (np.ndarray, list, tuple)):
        try: return ", ".join(str(v) for v in val)
        except: return str(val)

    return val if val is not None else str(param)


# --------------------------------------------------
# Extraction per file
# --------------------------------------------------

def extract_dlis_header(dlis_file):
    try:
        pf = dlis.load(dlis_file)
    except Exception as e:
        print(f"❌ Cannot load {dlis_file}: {e}")
        return None

    origins, params, tools, channels, frames, chinfo = [], [], [], [], [], []

    for lf_index, lf in enumerate(pf):
        lf_id = lf_index + 1

        # -------- Origins --------
        for o in lf.origins:
            try:
                d = {k: normalize_scalar(v) for k, v in o.describe().items()}
            except:
                d = {"repr": str(o)}
            d["LogicalFile"] = lf_id
            origins.append(d)

        # -------- Parameters --------
        for p in lf.parameters:
            name = first_attr(p, ["objname", "name", "tag", "mnemonic", "id"])
            value = unwrap_param_value(p)
            params.append({
                "LogicalFile": lf_id,
                "Name": normalize_scalar(name),
                "Value": normalize_scalar(value),
                "Raw": str(p)
            })

        # -------- Tools --------
        for t in lf.tools:
            name = first_attr(t, ["objname", "name", "toolname", "id"])
            try:
                d = {k: normalize_scalar(v) for k, v in t.describe().items()}
            except:
                d = {"repr": str(t)}
            tools.append({
                "LogicalFile": lf_id,
                "ToolName": normalize_scalar(name),
                "Description": str(d)
            })

        # -------- Channels & Channel Info --------
        for ch in lf.channels:
            chname = first_attr(ch, ["name", "mnemonic", "objname"])
            channels.append({
                "LogicalFile": lf_id,
                "ChannelName": normalize_scalar(chname),
                "Raw": str(ch)
            })

            # Mnemonic–Unit–Description table
            mnemonic = first_attr(ch, ["mnemonic", "name"])
            unit = first_attr(ch, ["unit", "units"])
            try:
                desc = ch.describe()
                long_name = desc.get("long_name", None)
            except:
                long_name = None

            chinfo.append({
                "LogicalFile": lf_id,
                "Mnemonic": normalize_scalar(mnemonic),
                "Unit": normalize_scalar(unit),
                "Description": normalize_scalar(long_name)
            })

        # -------- Frames --------
        for fr in lf.frames:
            fname = first_attr(fr, ["name", "objname", "tag", "identifier"])
            frames.append({
                "LogicalFile": lf_id,
                "FrameName": normalize_scalar(fname),
                "Raw": str(fr)
            })

    return (
        pd.DataFrame(origins),
        pd.DataFrame(params),
        pd.DataFrame(tools),
        pd.DataFrame(channels),
        pd.DataFrame(frames),
        pd.DataFrame(chinfo)
    )


# --------------------------------------------------
# Tkinter UI
# --------------------------------------------------

def main():
    Tk().withdraw()

    files = filedialog.askopenfilenames(
        title="Select DLIS file(s)",
        filetypes=[("DLIS files", "*.dlis"), ("All files", "*.*")]
    )
    if not files:
        print("No files selected.")
        return

    outdir = "output_dlis_header"
    os.makedirs(outdir, exist_ok=True)

    for f in files:
        print(f"\n→ Processing {f}")
        result = extract_dlis_header(f)
        if result is None:
            continue

        df_o, df_p, df_t, df_c, df_f, df_ci = result

        # Deduplicate ChannelInfo only
        df_ci = df_ci.drop_duplicates(subset=["Mnemonic", "Unit", "Description"])

        # Write individual Excel file
        basename = os.path.splitext(os.path.basename(f))[0]
        excel_path = os.path.join(outdir, f"{basename}_header.xlsx")

        with pd.ExcelWriter(excel_path, engine="openpyxl") as x:
            df_o.to_excel(x, "Origins", index=False)
            df_p.to_excel(x, "Parameters", index=False)
            df_t.to_excel(x, "Tools", index=False)
            df_c.to_excel(x, "Channels", index=False)     # unchanged
            df_f.to_excel(x, "Frames", index=False)
            df_ci.to_excel(x, "ChannelInfo", index=False) # deduped

        print(f"✔ Saved: {excel_path}")

    # Popup when all files are done
    messagebox.showinfo("DLIS Header Extractor", "Finished! Excel files have been generated.")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
