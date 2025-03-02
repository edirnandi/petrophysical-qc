import numpy as np

def minimum_curvature(md1, inc1, azi1, md2, inc2, azi2):
    """
    Calculate position using the Minimum Curvature Method.
    
    Parameters:
    md1, md2: Measured Depths (ft)
    inc1, inc2: Inclinations (degrees)
    azi1, azi2: Azimuths (degrees)
    
    Returns:
    dN, dE, dTVD: North, East, and True Vertical Depth (ft)
    """
    # Convert degrees to radians
    inc1, inc2 = np.radians(inc1), np.radians(inc2)
    azi1, azi2 = np.radians(azi1), np.radians(azi2)
    
    # Dogleg Severity (β)
    beta = np.arccos(np.cos(inc2 - inc1) - np.sin(inc1) * np.sin(inc2) * (1 - np.cos(azi2 - azi1)))
    
    # Radius Factor (RF)
    if beta == 0:
        RF = 1
    else:
        RF = 2 / beta * np.tan(beta / 2)
    
    # Delta MD
    delta_MD = md2 - md1
    
    # Calculate North, East, and TVD
    dN = (delta_MD / 2) * (np.sin(inc1) * np.cos(azi1) + np.sin(inc2) * np.cos(azi2)) * RF
    dE = (delta_MD / 2) * (np.sin(inc1) * np.sin(azi1) + np.sin(inc2) * np.sin(azi2)) * RF
    dTVD = (delta_MD / 2) * (np.cos(inc1) + np.cos(inc2)) * RF
    
    return dN, dE, dTVD

# Example usage:
md1, inc1, azi1 = 1000, 28, 54
md2, inc2, azi2 = 1100, 32, 57
dN, dE, dTVD = minimum_curvature(md1, inc1, azi1, md2, inc2, azi2)
print(f"North: {dN:.6f} ft, East: {dE:.6f} ft, TVD: {dTVD:.6f} ft")
