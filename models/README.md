# VisionForge Model Folder

VisionForge does not ship pretrained model weights inside the GitHub repository.

Place your local model files here:

models/yolo/yolov8n.pt
models/yolo/your_custom_model.pt
models/sam/sam_vit_b_01ec64.pth

Why models are not committed:
- Keeps the repository lightweight
- Avoids redistributing third-party weights
- Prevents accidental large GitHub commits
- Allows users to bring their own YOLO/SAM/custom models

Recommended YOLO test model:
python scripts/download_yolo_models.py --model yolov8n.pt

Recommended SAM model:
sam_vit_b_01ec64.pth
