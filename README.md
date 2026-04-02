# Accra-Flood-Risk-Automation
A Python (ArcPy) script that automates a multi-criteria spatial flood risk model.
Automated Flood Risk Spatial Model
Project Overview
This project automates a traditional manual GIS workflow into a single Python script. It uses ArcPy and Map Algebra to evaluate terrain data and output a categorized flood risk map for [Insert District/Area Name], Accra.

The Problem
Traditional flood modeling in GIS requires manually running sequential geoprocessing tools (Slope calculation, Reclassification, Weighted Overlay), which is time-consuming and prone to human error when adjusting parameters.

The Solution
I built a Python script that bypasses the manual interface, handles file management, and executes the spatial logic instantly.

Methodology & Logic
The model uses a multi-criteria decision matrix with the following weights:

Elevation (60% Influence): Reclassified so lower elevations present a higher risk.

Slope (40% Influence): Reclassified so flatter terrain (where water pools) presents a higher risk.

Technologies Used

Python

ArcPy (ArcGIS Spatial Analyst)

Digital Elevation Models (DEM)
<img width="14044" height="9934" alt="Automated Flood Susceptibility Model - Accra District" src="https://github.com/user-attachments/assets/fd0c45e1-fd57-4af8-991f-e6e5895da974" />
