"Computer Vision-Based Well Log Digitization"
 An Open-Source Python Utility for Converting Raster Well Logs into LAS 2.0 Format. The initiative explores opportunities to improve the accessibility and reusability of historical well log data through practical automation.

1.Overview

This Python utility uses computer vision and image processing techniques to digitize conventional raster well-log images and convert extracted curves into LAS 2.0 format.

2.Key Features

- Input: Raster well log images: PNG, JPG, TIFF.
- Petrophysical settings: define curve mnemonic, unit, track scale, linear/log scale, and sampling interval.
- Four-Point Calibration: set track boundaries and top/bottom depth references.
- Computer Vision & Signal Processing: apply separate processing approaches for color and grayscale images to extract and process the log curve.
- Output: LAS 2.0 file and QC image for visual verification.

Users can configure petrophysical parameters: curve mnemonic, unit, scale values, color or grayscale scan mode, scale type, depth unit, and sampling step, and calibrate the image interactively. The initial default configuration uses RHOB Density, but the utility is not limited to this curve.

3. Installation

Python 3 is required.
Install the dependencies: pip install opencv-python numpy scipy lasio 

Tkinter is also required for the graphical dialogs and is included with many standard Python installations.

4. Usage

Run the script:
python digitize_log_dynamic_cv.py

Follow the on-screen dialogs and calibration instructions.

5. Output Files

The utility generates two files in the same directory as the input image:
- LAS 2.0: Contains the DEPT curve and the user-configured petrophysical curve.
- QC Overlay PNG: Provides a visual representation of the extracted curve for quality checking.

Output filenames follow this pattern:
<image_name>_<mnemonic>_<top_depth>_<bottom_depth>.las
<image_name>_<mnemonic>_<top_depth>_<bottom_depth>_QC.png

Quality Control and Limitations 

Digitized curves reconstructed from raster images should be treated as recovered data requiring technical validation.

Extraction accuracy may depend on:
- Original image resolution and quality.
- Log-track layout and curve complexity.
- Depth and measurement scales.
- Grid lines, annotations, and overlapping curves.
- Image distortion and scanning quality.


6. Technology Stack

Python libraries dependencies: 
OpenCV
NumPy
SciPy
lasio
Tkinter

7. Important Note, Quality Control and Limitations 

This utility is based on classical computer vision and image-processing techniques, not AI machine learning or deep learning. Digitized curves should be visually inspected and validated against the original log image before being used for technical interpretation or engineering applications. This utility is intended to assist subsurface data recovery and should not replace professional petrophysical judgment or established quality-control procedures.


8. License

This project is released under the MIT License, allowing free use, modification, distribution, and commercial application, subject to the license conditions. The intention is to make practical Python-based tools more accessible to the wider subsurface community and encourage further learning, collaboration, and development.

Acknowledgment
Developed through the practical application of subsurface domain knowledge, Python programming, computer vision techniques, data accessibility, and learning. The project is shared with the subsurface community in the spirit of open-source collaboration, continuous learning, and knowledge sharing.

Disclaimer

This software is provided "AS IS", without warranty of any kind, express or implied. Users are responsible for validating the accuracy and suitability of the generated data for their intended applications.

Author: Edy Irnandi Sudjana
Project: Computer Vision-Based Well Log Digitization
Initial Release: Version 1.0 
Release Date: November 2026
License: MIT


