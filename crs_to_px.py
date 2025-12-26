import json
import numpy as np
from pathlib import Path

MATRIX_FILE = Path("transform_H.json")
IN_GEOJSON = Path("DTL_crs.geojson")
OUT_JSON = Path("DTL_px.json")


def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p: Path, obj: dict) -> None:
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def apply_homography(H: np.ndarray, xy: np.ndarray) -> np.ndarray:
    """
    H maps QGIS (x,y) -> pixel (u,v)
    xy: Nx2
    """
    xy = np.asarray(xy, dtype=np.float64)
    ones = np.ones((xy.shape[0], 1), dtype=np.float64)
    pts = np.hstack([xy, ones])              
    proj = (H @ pts.T).T                    
    uv = proj[:, :2] / proj[:, 2:3]         
    return uv


def geometry_to_polylines(geom: dict) -> list:
    """
    Return a list of polylines; each polyline is a list of [x,y].
    Supports LineString and MultiLineString.
    """
    gtype = geom.get("type")
    coords = geom.get("coordinates")

    if gtype == "LineString":
        return [coords]
    if gtype == "MultiLineString":
        return coords

    raise ValueError(f"Unsupported geometry type: {gtype}")


def main():
    if not MATRIX_FILE.exists():
        raise FileNotFoundError(f"Missing {MATRIX_FILE}. Run your transform script first.")
    if not IN_GEOJSON.exists():
        raise FileNotFoundError(f"Missing {IN_GEOJSON}. Put DTL.geojson next to this script.")

    m = load_json(MATRIX_FILE)
    H = np.array(m["H_qgis_to_px"], dtype=np.float64)

    gj = load_json(IN_GEOJSON)

    out_lines = []
    feature_count = 0

    for i, feat in enumerate(gj.get("features", [])):
        geom = feat.get("geometry")
        if not geom:
            continue

        polylines = geometry_to_polylines(geom)
        props = feat.get("properties") or {}
        feature_count += 1

        for j, line in enumerate(polylines):
            xy = np.array([[pt[0], pt[1]] for pt in line], dtype=np.float64)
            uv = apply_homography(H, xy)

            out_lines.append({
                "id": f"feature_{i}_{j}" if len(polylines) > 1 else f"feature_{i}",
                "points": [[float(u), float(v)] for u, v in uv],
                "properties": props
            })

    out = {
        "source": str(IN_GEOJSON.name),
        "image": m.get("image"),
        "transform": "H_qgis_to_px",
        "lines": out_lines
    }

    save_json(OUT_JSON, out)
    print(f"Wrote {OUT_JSON} with {len(out_lines)} polyline(s) from {feature_count} feature(s).")


if __name__ == "__main__":
    main()
