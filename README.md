# Manual Line Extraction & Coordinate Conversion

The objective of this project is to develop a workflow to manually extract lines by tracing and converting line data into pixel coordinates that can be accurately overlaid onto the original schematic.

QGIS is selected as the tracing software because, while it does not directly output pixel coordinates for traced lines, its exported CRS coordinates remain anchored relative to the overall dimensions of the schematic. Inkscape, on the other hand, produces vector layers whose coordinate system is constrained to the minimal bounding area of the path itself. As a result, these paths cannot be accurately mapped back to the complete schematic without additional context.

The central challenge of this project is therefore converting QGIS-exported CRS coordinates into schematic pixel coordinates without losing spatial accuracy. This repository addresses that challenge by deriving and applying an affine transformation matrix to map GIS space into pixel space consistently.

---

## Overview

The pipeline consists of 3 stages:

1. **Manual tracing in QGIS**  
   MRT lines are traced by hand over a schematic background image. Each point along the traced line is stored using CRS coordinates and exported as GeoJSON.
     <p align="center">
     <img src="QGIS_trace.png" alt="QGIS hand tracing" width="520">
   </p>
  

2. **Produce control coordinates for each coordinate system**  
   4 common reference points are identified. Their CRS coordinates are obtained from QGIS and saved in GeoJSON, while their pixel coordinates are extracted directly from the image using Python and OpenCV. These pairs serve as anchors to relate the two coordinate systems.  
   <p align="center">
     <img src="control_points.png" alt="Control points extracted using OpenCV" width="520">
   </p>

3. **Matrix-based transformation**  
   A conversion matrix is derived to map CRS coordinates into pixel coordinates using an affine transformation. Given a set of corresponding control points in CRS space and image space, a linear system is solved to estimate the transformation parameters(scale, translation, and axis inversion). Once derived, the same affine transformation matrix is applied to convert all CRS files in GeoJson to pixel coordinate files in Json. Any future accuracy improvements only require updating the matrix, without modifying the original GeoJSON data.
---

## Final Result

The image below illustrates the transformed line data aligned accurately with the original schematic:

<p align="center">
     <img src="overlay.png" alt="Control points extracted using OpenCV" width="520">
   </p>


---

## Limitations and Future Improvements

The accuracy of the CRS-to-pixel conversion depends entirely on the precision of the manually selected control points. The same four reference points must be identified both in QGIS (CRS space) and in Python using OpenCV (pixel space). Any discrepancy in these selections propagates directly into the estimated affine transformation matrix and affects the final alignment.

In the current implementation, four MRT stations distributed across the schematic are used as control points. Their pixel coordinates are obtained by manually clicking the approximate centre of the station code rectangles. This introduces small but unavoidable human error.

Future work could explore automating control point detection. This could further enhance the accuracy of the coordinate conversion.


