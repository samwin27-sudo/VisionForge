# Changelog

## v1.1.0

### Added
- Batch/full-dataset auto-annotation workflow.
- Editable COCO/ADAS class mapping for YOLO predictions.
- Default YOLO and SAM model memory via `~/.visionforge/settings.json`.
- Optional YOLO + SAM segmentation flow from detected boxes.
- Class-colored bounding boxes.
- Additional augmentations: grayscale, contrast, saturation, blur, noise, sharpen, vertical flip, random crop, resize, and small-angle rotation.

### Improved
- SAM checkpoint handling with auto model type detection.
- Auto-labeling error messages and fallback behavior.
- Annotation editing canvas behavior.


## v1.0.4 - Dialog layout hotfix

- Fixed clipped/overlapping text in Export dialog on macOS.
- Increased minimum sizes for all modal dialogs.
- Added scroll-safe dialog bodies so content does not overlap or disappear on smaller screens.
- Updated visible app version to v1.0.4.


## v1.0.0 - 2026-05-19

- Initial GitHub-ready VisionForge release.
- Manual annotation, optional YOLO, optional SAM backend, analysis, exports, docs, tests.