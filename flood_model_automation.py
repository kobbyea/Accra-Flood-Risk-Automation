"""
Automated Flood Risk Spatial Model
Location: Accra District, Ghana
Description: This script automates a multi-criteria GIS analysis to identify flood-prone 
zones by evaluating terrain slope and elevation data using ArcPy Map Algebra.
"""

import arcpy
from arcpy.sa import *

# Set standard workspace environment
arcpy.env.workspace = r"C:\Users\USER\Documents\ArcGIS"

# Check out the Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

print("Initializing flood risk model...")

# Define the reclassification matrix for risk levels (1 = Low, 2 = Medium, 3 = High)
# Applied to both Slope (flat = high risk) and Elevation (low = high risk)
risk_remap = RemapValue([[1, 1], [2, 2], [3, 3], ["NODATA", "NODATA"]])

# Build the Weighted Overlay Table
# Factor 1: Elevation (60% Influence)
# Factor 2: Slope (40% Influence)
# Evaluation Scale: 1 to 3 by 1
overlay_matrix = WOTable([
    ["elev_reclass_python.tif", 60, "Value", risk_remap], 
    ["slope_reclass_python.tif", 40, "Value", risk_remap]
    ], [1, 3, 1])

# Execute the Weighted Overlay tool
print("Running weighted overlay analysis...")
final_flood_map = WeightedOverlay(overlay_matrix)

# Save the final output
final_flood_map.save("flood_risk_python.tif")
print("Model complete. Output saved as flood_risk_python.tif")