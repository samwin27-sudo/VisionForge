from pathlib import Path
import argparse
import os

SUPPORTED_MODELS = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8n-seg.pt", "yolov8s-seg.pt"]

def main():
    parser = argparse.ArgumentParser(description="Download YOLO weights for VisionForge.")
    parser.add_argument("--model", default="yolov8n.pt", choices=SUPPORTED_MODELS)
    parser.add_argument("--output-dir", default="models/yolo")
    args = parser.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError:
        print("Ultralytics is not installed.")
        print("Run: pip install -r requirements-ai.txt")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    old_cwd = Path.cwd()
    os.chdir(output_dir)
    try:
        print(f"Downloading/loading {args.model} into {output_dir.resolve()} ...")
        YOLO(args.model)
    finally:
        os.chdir(old_cwd)

    expected = output_dir / args.model
    if expected.exists():
        print(f"Done: {expected}")
    else:
        print("Model loaded. Ultralytics may have used its cache.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
