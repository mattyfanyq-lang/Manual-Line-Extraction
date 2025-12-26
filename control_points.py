import cv2
import json
from pathlib import Path

IMAGE_PATH = "mrt_clean.png"
OUT_JSON = "control_px.json"
POINT_IDS = ["P1", "P2", "P3", "P4"] 

points = []
img_disp = None

def redraw(base_img):
    global img_disp
    img_disp = base_img.copy()
    for i, p in enumerate(points):
        x, y = int(p["px"][0]), int(p["px"][1])
        cv2.circle(img_disp, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(img_disp, p["id"], (x + 8, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

def on_mouse(event, x, y, flags, param):
    global points, img_disp
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) >= len(POINT_IDS):
            return
        pid = POINT_IDS[len(points)]
        points.append({"id": pid, "px": [float(x), float(y)]})
        redraw(param)
        cv2.imshow("Pick 4 points (U=undo, S=save, Esc=exit)", img_disp)

def main():
    base = cv2.imread(IMAGE_PATH)
    if base is None:
        raise FileNotFoundError(f"Could not read image: {IMAGE_PATH}")

    redraw(base)

    cv2.namedWindow("Pick 4 points (U=undo, S=save, Esc=exit)", cv2.WINDOW_NORMAL)
    cv2.imshow("Pick 4 points (U=undo, S=save, Esc=exit)", img_disp)
    cv2.setMouseCallback("Pick 4 points (U=undo, S=save, Esc=exit)", on_mouse, param=base)

    while True:
        key = cv2.waitKey(20) & 0xFF

        if key in (ord("u"), ord("U")):
            if points:
                points.pop()
                redraw(base)
                cv2.imshow("Pick 4 points (U=undo, S=save, Esc=exit)", img_disp)

        if key in (ord("s"), ord("S")):
            if len(points) != len(POINT_IDS):
                print(f"Need {len(POINT_IDS)} points, currently have {len(points)}.")
                continue

            payload = {
                "image": str(Path(IMAGE_PATH).name),
                "points": points
            }
            with open(OUT_JSON, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            print(f"Saved: {OUT_JSON}")
            break

        if key == 27:
            print("Exited without saving.")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
