# VisionForge

**Version:** v1.0.0  
**Tagline:** Offline-first AI-assisted annotation, segmentation, and dataset intelligence tool for Edge AI, ADAS, and computer vision datasets.

![Screenshot placeholder](docs/screenshots.md)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#installation)
[![PySide6](https://img.shields.io/badge/UI-PySide6-green)](#installation)
[![License MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## What is VisionForge?

VisionForge is an offline-first AI-assisted annotation, segmentation, and dataset intelligence tool for Edge AI, ADAS, and computer vision datasets.

**LabelImg helps you draw boxes. VisionForge helps you prepare datasets for training, validation, and edge deployment.**

VisionForge supports manual bounding-box annotation, optional YOLO auto-labeling, optional SAM-compatible segmentation assistance, class grouping for ADAS/edge deployment, dataset analysis, augmentation, train/val/test splitting, export, and report generation.

## Why VisionForge?

VisionForge is not just a LabelImg clone. It focuses on the full dataset preparation workflow: annotate, auto-label, review predictions, group classes, analyze quality, balance data, split safely, export in training-ready formats, and generate readiness reports.

This project does not insult LabelImg, CVAT, Roboflow, or Label Studio. They are strong tools. VisionForge is a local, developer-friendly workflow for serious dataset preparation.

## Core Features

- Manual bounding-box annotation.
- Optional YOLO auto-labeling with lazy dependency loading.
- Optional SAM/SAM-compatible segmentation backend.
- Pending/accepted/rejected/edited review workflow for AI labels.
- Class manager and class group manager.
- ADAS grouping examples: Vehicle, Bike, Pedestrian, Road Damage, Road Feature, Road Signage.
- Dataset intelligence dashboard.
- Edge AI / ADAS readiness score out of 100.
- Augmentation with bbox correction for supported transforms.
- Dataset randomizer and safe filename mapping.
- Train/val/test splitter.
- YOLO TXT, Pascal VOC XML, COCO detection, COCO segmentation, CSV, and grouped class exports.
- HTML/XLSX/CSV/JSON/TXT report outputs.

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/VisionForge.git
cd VisionForge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

### AI feature installation

```bash
pip install -r requirements-ai.txt
```

### Segmentation feature installation

```bash
pip install -r requirements-segmentation.txt
```

## Quick Start

1. Run `python run.py`.
2. Click **Open Dataset** and select an image folder.
3. Add classes or use `examples/sample_classes.txt`.
4. Draw boxes manually.
5. Optional: run YOLO auto-labeling and review pending predictions.
6. Optional: use segmentation backend modules to generate masks from prompt boxes.
7. Analyze dataset quality.
8. Export YOLO/VOC/COCO/CSV labels.
9. Generate a report.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| A / Left Arrow | Previous image |
| D / Right Arrow | Next image |
| Delete | Delete selected annotation |
| Ctrl+S | Save project |
| Ctrl+O | Open dataset |
| Ctrl+E | Export |
| Ctrl+R | Generate report |
| Ctrl+A | Auto-label current image |
| Ctrl+Shift+A | Auto-label full dataset |
| Ctrl+M | Toggle segmentation visibility |
| Ctrl+G | Open class grouping manager |
| Space | Accept current AI prediction |
| X | Reject current AI prediction |

## Export Formats

- YOLO Detection TXT
- Pascal VOC XML
- COCO Detection JSON
- COCO Segmentation JSON
- CSV Summary
- Grouped Class Export

## Disclaimer

VisionForge helps prepare datasets. It does not guarantee model accuracy, regulatory compliance, or ADAS production safety. Always validate models and datasets before deployment.
