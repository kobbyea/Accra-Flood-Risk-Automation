"""
Automated Flood Risk Spatial Model
Location: Accra Metropolitan Area, Ghana

Description:
Automates the full multi-criteria GIS workflow for flood risk mapping:
  1. Derives Slope from a source DEM
  2. Reclassifies Elevation and Slope into a common 1-3 risk scale
  3. Combines both factors via Weighted Overlay (Elevation 60% / Slope 40%)
  4. Outputs a categorized flood risk raster

This replaces the original version, which assumed pre-reclassified inputs
already existed and only automated the final overlay step. This version
runs the entire pipeline end-to-end from a raw DEM.

Requirements:
  - ArcGIS Desktop/Pro Python environment with a Spatial Analyst license
  - A DEM covering the study area

Usage:
  python flood_model_automation.py --workspace "C:\\path\\to\\project" --dem "dem.tif"
"""

import argparse
import os
import sys

import arcpy
from arcpy.sa import *


def build_flood_risk_model(workspace, dem_name,
                            elevation_weight=60, slope_weight=40,
                            output_name="flood_risk_python.tif"):
    """
    Runs the full flood risk weighted overlay pipeline.

    Parameters
    ----------
    workspace : str
        Path to the ArcGIS workspace/geodatabase containing the DEM.
    dem_name : str
        Filename (or feature name) of the source DEM within the workspace.
    elevation_weight : int
        Percent influence of the elevation factor (default 60).
    slope_weight : int
        Percent influence of the slope factor (default 40).
    output_name : str
        Filename for the final output raster.
    """
    if elevation_weight + slope_weight != 100:
        raise ValueError(
            f"Elevation and slope weights must sum to 100 "
            f"(got {elevation_weight} + {slope_weight} = {elevation_weight + slope_weight})"
        )

    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    dem_path = os.path.join(workspace, dem_name)
    if not arcpy.Exists(dem_path):
        raise FileNotFoundError(f"DEM not found at: {dem_path}")

    license_checked_out = False

    try:
        # --- Check out Spatial Analyst license ---
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            license_checked_out = True
        else:
            raise RuntimeError("Spatial Analyst extension is not available or already in use.")

        print("Initializing flood risk model...")
        print(f"Workspace: {workspace}")
        print(f"DEM input: {dem_name}")

        # --- Step 1: Derive Slope from the DEM ---
        print("Calculating slope from DEM...")
        slope_raster = Slope(dem_path, output_measurement="DEGREE")

        # --- Step 2: Reclassify Elevation (lower elevation = higher risk) ---
        # Natural Breaks-style manual bands; adjust to your DEM's actual range.
        print("Reclassifying elevation (lower elevation = higher risk)...")
        elev_reclass = Reclassify(
            dem_path, "Value",
            RemapRange([
                [-100, 20, 3],   # low elevation -> high risk
                [20, 60, 2],     # mid elevation -> medium risk
                [60, 10000, 1],  # high elevation -> low risk
            ]),
            "NODATA"
        )

        # --- Step 3: Reclassify Slope (flatter terrain = higher risk, water pools) ---
        print("Reclassifying slope (flatter terrain = higher risk)...")
        slope_reclass = Reclassify(
            slope_raster, "Value",
            RemapRange([
                [0, 5, 3],     # flat -> high risk
                [5, 15, 2],    # moderate -> medium risk
                [15, 90, 1],   # steep -> low risk
            ]),
            "NODATA"
        )

        # Save intermediate reclassified rasters (useful for QA / re-use)
        elev_reclass.save("elev_reclass_python.tif")
        slope_reclass.save("slope_reclass_python.tif")

        # --- Step 4: Weighted Overlay ---
        print("Running weighted overlay analysis...")
        risk_remap = RemapValue([[1, 1], [2, 2], [3, 3], ["NODATA", "NODATA"]])

        overlay_matrix = WOTable(
            [
                ["elev_reclass_python.tif", elevation_weight, "Value", risk_remap],
                ["slope_reclass_python.tif", slope_weight, "Value", risk_remap],
            ],
            [1, 3, 1],
        )

        final_flood_map = WeightedOverlay(overlay_matrix)
        final_flood_map.save(output_name)

        print(f"Model complete. Output saved as {output_name}")
        return output_name

    finally:
        # Always release the license, even if something above failed
        if license_checked_out:
            arcpy.CheckInExtension("Spatial")
            print("Spatial Analyst extension checked back in.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated multi-criteria flood risk model (Elevation + Slope weighted overlay)."
    )
    parser.add_argument("--workspace", required=True,
                         help=r"Path to the ArcGIS workspace containing the DEM, e.g. C:\Users\you\Documents\ArcGIS")
    parser.add_argument("--dem", required=True,
                         help="Filename of the source DEM within the workspace, e.g. dem.tif")
    parser.add_argument("--elevation-weight", type=int, default=60,
                         help="Percent influence of elevation factor (default: 60)")
    parser.add_argument("--slope-weight", type=int, default=40,
                         help="Percent influence of slope factor (default: 40)")
    parser.add_argument("--output", default="flood_risk_python.tif",
                         help="Output raster filename (default: flood_risk_python.tif)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        build_flood_risk_model(
            workspace=args.workspace,
            dem_name=args.dem,
            elevation_weight=args.elevation_weight,
            slope_weight=args.slope_weight,
            output_name=args.output,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
