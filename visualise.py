import json
from pathlib import Path

import cv2
import numpy as np

# ---------- Paths ----------
BG_PATH = Path("mrt_clean.png")
DTL_PATH = Path("DTL_px.json")
EWL_PATH = Path("EWL_px.json")
OUT_PATH = Path("overlay.png")

# ---------- Styling ----------
DTL_COLOR = (255, 0 , 255)   # magenta (BGR)
EWL_COLOR = (255, 255, 0)   # cyan (BGR)
THICKNESS = 25             # line thickness (px)


def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def draw_lines(img: np.ndarray, data: dict, colour: tuple[int, int, int]) -> int:
    """
    Draw all polylines from a *_px.json onto img.
    Returns number of polylines drawn.
    """
    h, w = img.shape[:2]
    count = 0

    for item in data.get("lines", []):
        pts = item.get("points", [])
        if len(pts) < 2:
            continue

        arr = np.array(pts, dtype=np.float32)

        # Clip coordinates to image bounds
        arr[:, 0] = np.clip(arr[:, 0], 0, w - 1)
        arr[:, 1] = np.clip(arr[:, 1], 0, h - 1)

        poly = arr.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(
            img,
            [poly],
            isClosed=False,
            color=colour,
            thickness=THICKNESS,
            lineType=cv2.LINE_AA
        )
        count += 1

    return count


def main():
    # Load background at full resolution
    bg = cv2.imread(str(BG_PATH), cv2.IMREAD_COLOR)
    if bg is None:
        raise FileNotFoundError(f"Could not read background image: {BG_PATH.resolve()}")

    print("Background size:", bg.shape)

    # Load line data
    dtl = load_json(DTL_PATH)
    ewl = load_json(EWL_PATH)

    # Draw directly onto a copy
    canvas = bg.copy()

    dtl_count = draw_lines(canvas, dtl, DTL_COLOR)
    ewl_count = draw_lines(canvas, ewl, EWL_COLOR)

    # Write PNG (no scaling, no preview)
    cv2.imwrite(str(OUT_PATH), canvas)

    print(f"Saved {OUT_PATH}")
    print(f"DTL polylines: {dtl_count}")
    print(f"EWL polylines: {ewl_count}")
    print("Output size:", canvas.shape)


if __name__ == "__main__":
    main()

