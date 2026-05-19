# VisionForge v1.0.0 Launch Kit

## Install commands

```bash
git clone https://github.com/YOUR_USERNAME/VisionForge.git
cd VisionForge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

## AI feature install command

```bash
pip install -r requirements-ai.txt
```

## Segmentation feature install command

```bash
pip install -r requirements-segmentation.txt
```

## Test with sample image folder

```bash
python run.py
# Click Open Dataset
# Select any folder containing JPG/PNG/BMP/WEBP images
# Add classes, draw boxes, save project
```

## Load YOLO model

1. Install AI dependencies.
2. Click **Auto Label**.
3. Select a `.pt` file such as `yolov8n.pt` or your custom model.
4. Set confidence, IoU, image size, and device.
5. Run on the current image or full dataset.

## Enable segmentation model

1. Install segmentation dependencies.
2. Place your SAM checkpoint locally.
3. Use `visionforge/ai/sam_segmenter.py` as the backend adapter.
4. Use mask utilities in `visionforge/core/mask_utils.py` to convert masks to polygons/bboxes.

## Auto-label current image

Open a dataset, select an image, click **Auto Label**, choose model, click **Run**.

## Auto-label full dataset

Use `Ctrl+Shift+A`, choose the YOLO model, and run batch labeling.

## Review AI predictions

AI predictions are saved as `pending`. Use:

- **Accept Selected**
- **Reject Selected**
- **Accept All Pending**
- **Reject All Pending**
- `Space` to accept selected
- `X` to reject selected

## Export YOLO labels

Click **Export** → choose **YOLO TXT** → choose output folder → export.

## Export COCO segmentation

Click **Export** → choose **COCO Segmentation JSON**. This exports polygons when segmentation/polygon data exists.

## Generate dataset report

Click **Generate Report** and choose an output folder. VisionForge generates HTML, XLSX, CSV, JSON, TXT, and charts.

## GitHub upload commands

```bash
git init
git add .
git commit -m "Release VisionForge v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/VisionForge.git
git push -u origin main
git tag v1.0.0
git push origin v1.0.0
```

## GitHub repository description

VisionForge is an offline-first AI-assisted annotation, segmentation, and dataset intelligence tool for Edge AI, ADAS, and computer vision datasets.

## GitHub topics/tags

computer-vision, annotation-tool, image-annotation, object-detection, segmentation, yolo, sam, dataset-management, adas, edge-ai, machine-learning, deep-learning, coco-format, pascal-voc, yolo-format, pyside6, python

## Release checklist

- [ ] Run `pytest`.
- [ ] Run `python run.py`.
- [ ] Open a dataset.
- [ ] Draw manual boxes.
- [ ] Test save/load project.
- [ ] Test YOLO missing dependency message.
- [ ] Test YOLO export.
- [ ] Test COCO export.
- [ ] Test report generation.
- [ ] Add screenshots.
- [ ] Create GitHub release `v1.0.0`.

## LinkedIn launch post

I’m releasing **VisionForge v1.0.0** — an offline-first AI-assisted annotation, segmentation, and dataset intelligence tool for Edge AI, ADAS, and computer vision datasets.

Most annotation workflows stop at drawing boxes. VisionForge is built around the full dataset preparation workflow: manual annotation, YOLO auto-labeling, optional SAM-style segmentation assistance, AI label review, ADAS class grouping, dataset quality analysis, train/val/test splitting, export, and readiness reporting.

The goal is simple: help computer vision engineers prepare datasets that are not just labeled, but actually closer to training-ready and edge-deployment-ready.

GitHub: https://github.com/YOUR_USERNAME/VisionForge

#ComputerVision #ADAS #EdgeAI #Python #OpenSource #MachineLearning #YOLO #Segmentation

## Reddit / IndieHackers launch post

I built and released **VisionForge v1.0.0**, an offline-first desktop tool for computer vision dataset preparation.

It supports manual bbox annotation, optional YOLO auto-labeling, optional SAM-style segmentation backend, AI prediction review, ADAS class grouping, dataset intelligence, readiness scoring, augmentation, splitting, YOLO/VOC/COCO/CSV exports, and report generation.

The idea is: LabelImg helps draw boxes. VisionForge helps prepare datasets for training, validation, and edge deployment.

It is open-source and built with Python + PySide6.

Repo: https://github.com/YOUR_USERNAME/VisionForge

Feedback and contributions are welcome.

## Future roadmap

- Better box resize/move handles.
- Class mapping UI.
- SAM checkpoint configuration UI.
- Polygon point editing.
- SAM2 adapter.
- Active learning sample selector.
- Video-sequence-aware splitting.
- Dataset diff tool.
- Per-class mAP/result importer.
- ONNX/TFLite readiness assistant.
