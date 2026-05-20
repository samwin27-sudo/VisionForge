# Download SAM Models for VisionForge

VisionForge does not commit SAM weights to GitHub.

Create folder:
mkdir -p models/sam

Download smallest SAM checkpoint:
curl -L -o models/sam/sam_vit_b_01ec64.pth "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"

Install segmentation dependencies:
pip install -r requirements-segmentation.txt

Run VisionForge:
python run.py
