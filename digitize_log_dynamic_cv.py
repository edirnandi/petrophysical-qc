# "Computer Vision-Based Well Log Digitization"
# An Open-Source Python Utility for Converting Raster Well Logs into LAS 2.0 Format. The initiative explores opportunities to improve the accessibility and reusability of historical well log data through practical automation.
#
# MIT License. 
# Acknowledgment (Developed through the practical application of subsurface domain knowledge, Python programming, computer vision techniques, data accessibility, and learning. The project is shared with the subsurface community in the spirit of open-source collaboration, continuous learning, and knowledge sharing.)
#
# Disclaimer
# This software is provided "AS IS", without warranty of any kind, express or implied. Users are responsible for validating the accuracy and suitability of the generated data for their intended applications.
# Author: Edy Irnandi Sudjana
# Project: Computer Vision-Based Well Log Digitization
# Initial Release: Version 1.0
#License: MIT

import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import cv2
import lasio
import numpy as np
from scipy.signal import savgol_filter


# ---------------------------------------------------------
# 0. Native File Picker Dialog (tkinter)
# ---------------------------------------------------------
def select_image_file() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select Raster Well-Log Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp"),
            ("All Files", "*.*"),
        ],
    )
    root.destroy()

    if not file_path:
        raise SystemExit("No file selected. Exiting script.")

    return file_path


# ---------------------------------------------------------
# 1. Petrophysical Track & Mode Configuration Dialog
# ---------------------------------------------------------
def get_petrophysical_parameters() -> dict:
    params = {}
    root = tk.Tk()
    root.title("Petrophysical Track & Mode Calibration")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    # Window geometry
    root.geometry("400x420")
    pad = {"padx": 12, "pady": 6}

    tk.Label(root, text="Curve Scan Mode:", anchor="w", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", **pad)
    mode_var = tk.StringVar(value="color")
    mode_frame = tk.Frame(root)
    mode_frame.grid(row=0, column=1, sticky="w", **pad)
    tk.Radiobutton(mode_frame, text="Color (e.g. Red RHOB)", variable=mode_var, value="color").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="B&W / Grayscale Scan", variable=mode_var, value="grayscale").pack(anchor="w")

    tk.Label(root, text="Curve Mnemonic:", anchor="w").grid(row=1, column=0, sticky="w", **pad)
    mnemonic_var = tk.StringVar(value="RHOB")
    tk.Entry(root, textvariable=mnemonic_var, width=18).grid(row=1, column=1, **pad)

    tk.Label(root, text="Curve Unit:", anchor="w").grid(row=2, column=0, sticky="w", **pad)
    unit_var = tk.StringVar(value="G/CC")
    tk.Entry(root, textvariable=unit_var, width=18).grid(row=2, column=1, **pad)

    tk.Label(root, text="Left Scale Value:", anchor="w").grid(row=3, column=0, sticky="w", **pad)
    left_scale_var = tk.StringVar(value="1.95")
    tk.Entry(root, textvariable=left_scale_var, width=18).grid(row=3, column=1, **pad)

    tk.Label(root, text="Right Scale Value:", anchor="w").grid(row=4, column=0, sticky="w", **pad)
    right_scale_var = tk.StringVar(value="2.95")
    tk.Entry(root, textvariable=right_scale_var, width=18).grid(row=4, column=1, **pad)

    tk.Label(root, text="Track Scale Type:", anchor="w").grid(row=5, column=0, sticky="w", **pad)
    scale_type_var = tk.StringVar(value="linear")
    scale_frame = tk.Frame(root)
    scale_frame.grid(row=5, column=1, sticky="w", padx=4, pady=2)
    tk.Radiobutton(scale_frame, text="Linear", variable=scale_type_var, value="linear").pack(side="left")
    tk.Radiobutton(scale_frame, text="Log", variable=scale_type_var, value="log").pack(side="left")

    tk.Label(root, text="Depth Unit (FT / M):", anchor="w").grid(row=6, column=0, sticky="w", **pad)
    depth_unit_var = tk.StringVar(value="FT")
    tk.Entry(root, textvariable=depth_unit_var, width=18).grid(row=6, column=1, **pad)

    tk.Label(root, text="Sampling Step:", anchor="w").grid(row=7, column=0, sticky="w", **pad)
    step_var = tk.StringVar(value="0.5")
    tk.Entry(root, textvariable=step_var, width=18).grid(row=7, column=1, **pad)

    def on_submit():
        try:
            l_val = float(left_scale_var.get().strip())
            r_val = float(right_scale_var.get().strip())
            s_val = float(step_var.get().strip())
            sc_type = scale_type_var.get().strip().lower()

            if sc_type == "log" and (l_val <= 0 or r_val <= 0):
                messagebox.showerror("Invalid Scale", "Logarithmic scales require positive Left and Right values (> 0).")
                return
            if s_val <= 0:
                messagebox.showerror("Invalid Step", "Sampling step must be greater than 0.")
                return

            params["curve_mode"] = mode_var.get().strip().lower()
            params["mnemonic"] = mnemonic_var.get().strip().upper() or "CURVE"
            params["unit"] = unit_var.get().strip().upper() or "UNIT"
            params["left_scale"] = l_val
            params["right_scale"] = r_val
            params["scale_type"] = sc_type
            params["depth_unit"] = depth_unit_var.get().strip().upper() or "FT"
            params["step"] = s_val
            root.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Left Scale, Right Scale, and Step must be valid numbers.")

    tk.Button(
        root,
        text="Confirm & Start 4-Click Calibration",
        command=on_submit,
        bg="#1f6aa5",
        fg="white",
        font=("Arial", 10, "bold"),
        pady=5,
    ).grid(row=8, column=0, columnspan=2, pady=15)

    root.mainloop()

    if not params:
        raise SystemExit("Configuration window closed. Exiting script.")

    return params


# ---------------------------------------------------------
# 2. Dynamic 4-Point Calibration + Depth Prompt
# ---------------------------------------------------------
def prompt_depth_value(title: str, prompt_text: str, default_val: float) -> float:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    val = simpledialog.askfloat(title, prompt_text, initialvalue=default_val, parent=root)
    root.destroy()
    if val is None:
        raise SystemExit("Depth entry cancelled. Exiting script.")
    return float(val)


def calibrate_track_dynamic(image_path: str, depth_unit: str):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")

    display_scale = 2.0 if img.shape[1] < 250 else 1.0
    vis = cv2.resize(img, (0, 0), fx=display_scale, fy=display_scale)

    step_prompts = [
        "1/4: Click INNER LEFT track border",
        "2/4: Click INNER RIGHT track border",
        "3/4: Click TOP depth tick mark",
        "4/4: Click BOTTOM depth tick mark",
    ]
    clicks = []
    pending_depth_prompt = [None]

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 4 and pending_depth_prompt[0] is None:
            orig_x = int(round(x / display_scale))
            orig_y = int(round(y / display_scale))
            clicks.append((orig_x, orig_y))

            cv2.circle(vis, (x, y), 5, (255, 0, 0), -1)
            if len(clicks) in (3, 4):
                cv2.line(vis, (0, y), (vis.shape[1], y), (255, 0, 0), 1)
                pending_depth_prompt[0] = len(clicks)

    window_name = "Dynamic Track Calibration"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    top_depth = None
    bottom_depth = None

    while len(clicks) < 4 or pending_depth_prompt[0] is not None:
        temp = vis.copy()
        idx = min(len(clicks), 3)
        cv2.putText(
            temp,
            step_prompts[idx],
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 0, 0),
            2,
        )
        cv2.imshow(window_name, temp)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("Calibration cancelled by user.")

        if pending_depth_prompt[0] == 3:
            top_depth = prompt_depth_value(
                "Top Depth Anchor",
                f"Enter Top Depth ({depth_unit}) at Click 3:",
                default_val=11750.0,
            )
            pending_depth_prompt[0] = None

        elif pending_depth_prompt[0] == 4:
            default_bot = (top_depth + 100.0) if top_depth is not None else 11850.0
            bottom_depth = prompt_depth_value(
                "Bottom Depth Anchor",
                f"Enter Bottom Depth ({depth_unit}) at Click 4:",
                default_val=default_bot,
            )
            pending_depth_prompt[0] = None

    cv2.destroyAllWindows()

    y_click_3, y_click_4 = clicks[2][1], clicks[3][1]
    if y_click_3 <= y_click_4:
        y_top, y_bottom = y_click_3, y_click_4
    else:
        y_top, y_bottom = y_click_4, y_click_3
        top_depth, bottom_depth = bottom_depth, top_depth

    x_left = min(clicks[0][0], clicks[1][0])
    x_right = max(clicks[0][0], clicks[1][0])

    return img, x_left, x_right, y_top, y_bottom, top_depth, bottom_depth


# ---------------------------------------------------------
# 3. Curve Extraction (Color vs B&W Grayscale + Grid Removal)
# ---------------------------------------------------------
def extract_log_curve(
    img_bgr: np.ndarray,
    x1: int,
    x2: int,
    y1: int,
    y2: int,
    top_depth: float,
    bottom_depth: float,
    params: dict,
    qc_out_path: str,
):
    roi_bgr = img_bgr[y1:y2, x1:x2]
    roi_h, roi_w, _ = roi_bgr.shape

    if roi_h < 5 or roi_w < 5:
        raise ValueError("Selected track crop is too small. Please re-calibrate.")

    curve_mode = params.get("curve_mode", "color")

    if curve_mode == "color":
        roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(roi_hsv, np.array([0, 90, 70]), np.array([12, 255, 255]))
        mask2 = cv2.inRange(roi_hsv, np.array([165, 90, 70]), np.array([180, 255, 255]))
        mask = cv2.bitwise_or(mask1, mask2)

        b, g, r = cv2.split(roi_bgr.astype(np.float32))
        signal = r - np.maximum(g, b)
    else:
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        inv = 255.0 - gray.astype(np.float32)

        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, roi_h // 15)))
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(15, roi_w // 4), 1))
        vert_grid = cv2.morphologyEx(inv, cv2.MORPH_OPEN, v_kernel)
        horiz_grid = cv2.morphologyEx(inv, cv2.MORPH_OPEN, h_kernel)

        cleaned = np.clip(inv - 0.85 * vert_grid - 0.85 * horiz_grid, 0, 255).astype(np.uint8)
        _, mask = cv2.threshold(cleaned, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        signal = cleaned.astype(np.float32)

    raw_x = np.full(roi_h, np.nan)
    prev_x = None
    max_jump = max(12.0, roi_w * 0.15)

    for row in range(roi_h):
        cols = np.where(mask[row, :] > 0)[0]
        if len(cols) > 0:
            if prev_x is not None:
                near = cols[np.abs(cols - prev_x) <= max_jump]
                if len(near) > 0:
                    cols = near
            weights = np.maximum(signal[row, cols], 1.0)
            cx = float(np.average(cols, weights=weights))
            raw_x[row] = cx
            prev_x = cx

    valid = ~np.isnan(raw_x)
    if np.sum(valid) < 5:
        raise RuntimeError("Insufficient curve pixels detected. Check Curve Mode or crop bounds.")

    rows = np.arange(roi_h)
    interp_x = np.interp(rows, rows[valid], raw_x[valid])

    win = min(7, roi_h if roi_h % 2 == 1 else roi_h - 1)
    if win >= 5:
        interp_x = savgol_filter(interp_x, window_length=win, polyorder=2)

    u = np.clip(interp_x / float(roi_w - 1), 0.0, 1.0)
    left_scale = params["left_scale"]
    right_scale = params["right_scale"]
    scale_type = params["scale_type"]

    if scale_type == "linear":
        raw_values = left_scale + u * (right_scale - left_scale)
    elif scale_type in ("log", "logarithmic"):
        log_min = np.log10(left_scale)
        log_max = np.log10(right_scale)
        raw_values = 10 ** (log_min + u * (log_max - log_min))
    else:
        raise ValueError(f"Unsupported scale_type: {scale_type}")

    step = params["step"]
    raw_depths = np.linspace(top_depth, bottom_depth, roi_h)
    target_depths = np.arange(top_depth, bottom_depth + (step * 0.5), step)
    target_values = np.interp(target_depths, raw_depths, raw_values)

    qc_img = roi_bgr.copy()
    trace_color = (0, 0, 255) if curve_mode == "grayscale" else (255, 0, 0)
    for r_idx, x_val in enumerate(interp_x):
        cv2.circle(qc_img, (int(round(x_val)), r_idx), 1, trace_color, -1)
    cv2.imwrite(qc_out_path, qc_img)

    return target_depths, target_values


# ---------------------------------------------------------
# 4. Export LAS 2.0
# ---------------------------------------------------------
def save_las2(depths: np.ndarray, values: np.ndarray, params: dict, filename: str):
    las = lasio.LASFile()
    las.well.STRT.value = float(depths[0])
    las.well.STOP.value = float(depths[-1])
    las.well.STEP.value = float(params["step"])
    las.well.NULL.value = -999.25
    las.well.WELL.value = "LOCAL_TEST_WELL"

    las.append_curve("DEPT", depths, unit=params["depth_unit"], descr="Measured Depth")
    las.append_curve(
        params["mnemonic"],
        np.round(values, 4),
        unit=params["unit"],
        descr=f"Digitized {params['mnemonic']} ({params['scale_type'].upper()} scale)",
    )
    las.write(filename, version=2.0)


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    selected_image = select_image_file()
    print(f"Selected file: {selected_image}")

    petro_params = get_petrophysical_parameters()
    print(f"Configured Parameters: {petro_params}")

    img, x1, x2, y1, y2, top_d, bot_d = calibrate_track_dynamic(
        selected_image, depth_unit=petro_params["depth_unit"]
    )
    print(f"Calibrated Interval: {top_d} to {bot_d} {petro_params['depth_unit']}")

    folder = os.path.dirname(selected_image)
    base_name = os.path.splitext(os.path.basename(selected_image))[0]
    mnemonic = petro_params["mnemonic"]
    d_tag = f"{int(round(top_d))}_{int(round(bot_d))}"

    las_output_path = os.path.join(folder, f"{base_name}_{mnemonic}_{d_tag}.las")
    qc_output_path = os.path.join(folder, f"{base_name}_{mnemonic}_{d_tag}_QC.png")

    depths, curve_vals = extract_log_curve(
        img, x1, x2, y1, y2, top_d, bot_d, petro_params, qc_out_path=qc_output_path
    )
    save_las2(depths, curve_vals, petro_params, las_output_path)

    print(f"\n[DONE] Saved LAS 2.0: {las_output_path}")
    print(f"[DONE] Saved QC image: {qc_output_path}")
