import json
import numpy as np

CONTROL_PX_JSON = "control_px.json"          
CONTROL_CRS_GEOJSON = "control_crs.geojson"  
OUT_MATRIX_JSON = "transform_H.json"

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_px_points(control_px_path: str) -> np.ndarray:
    d = load_json(control_px_path)
    pts = [p["px"] for p in d.get("points", [])]
    if len(pts) != 4:
        raise ValueError(f"{control_px_path}: expected 4 pixel points, got {len(pts)}")
    return np.array(pts, dtype=np.float64), d.get("image")

def load_qgis_points(control_crs_path: str) -> np.ndarray:
    d = load_json(control_crs_path)
    feats = d.get("features", [])
    if len(feats) != 4:
        raise ValueError(f"{control_crs_path}: expected 4 features, got {len(feats)}")

    pts = []
    for i, feat in enumerate(feats, start=1):
        geom = feat.get("geometry", {})
        if geom.get("type") != "Point":
            raise ValueError(f"{control_crs_path}: feature {i} is not a Point")
        x, y = geom["coordinates"][:2]
        pts.append([float(x), float(y)])

    return np.array(pts, dtype=np.float64), d.get("crs")

def compute_homography(qgis_xy: np.ndarray, px_uv: np.ndarray) -> np.ndarray:
    if qgis_xy.shape != (4, 2) or px_uv.shape != (4, 2):
        raise ValueError("Need 4x2 qgis points and 4x2 pixel points.")

    A = []
    for (x, y), (u, v) in zip(qgis_xy, px_uv):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])

    A = np.array(A, dtype=np.float64)
    _, _, vt = np.linalg.svd(A)
    h = vt[-1, :]
    H = h.reshape(3, 3)

    # normalise
    if abs(H[2, 2]) > 1e-12:
        H = H / H[2, 2]

    return H

def main():
    px_uv, image_name = load_px_points(CONTROL_PX_JSON)
    qgis_xy, crs_info = load_qgis_points(CONTROL_CRS_GEOJSON)

    H = compute_homography(qgis_xy, px_uv)

    # Optional: also store inverse (px -> qgis)
    H_inv = np.linalg.inv(H)
    if abs(H_inv[2, 2]) > 1e-12:
        H_inv = H_inv / H_inv[2, 2]

    out = {
        "image": image_name,
        "control_point_order": "Uses order in control_px.json['points'] and control_crs.geojson['features']",
        "crs_from_control_crs": crs_info,
        "H_qgis_to_px": H.tolist(),
        "H_px_to_qgis": H_inv.tolist()
    }

    with open(OUT_MATRIX_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Saved:", OUT_MATRIX_JSON)
    print("H (QGIS -> px):\n", H)

if __name__ == "__main__":
    main()
