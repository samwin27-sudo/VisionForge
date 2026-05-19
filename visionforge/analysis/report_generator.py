import json
from pathlib import Path
import pandas as pd
from visionforge.analysis.dataset_analyzer import analyze_project
from visionforge.analysis.readiness_score import calculate_readiness_score
from visionforge.analysis.charts import class_distribution_chart, status_pie_chart, object_size_chart

def generate_report(project, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    charts = out / "charts"
    analysis = analyze_project(project)
    ready = calculate_readiness_score(analysis, analysis.get("segmentation_annotation_count", 0) > 0)
    class_distribution_chart(analysis["class_wise_object_count"], charts / "class_distribution.png")
    status_pie_chart(analysis["annotation_status_counts"], charts / "annotation_status.png")
    object_size_chart(analysis["object_size_distribution"], charts / "object_size_distribution.png")
    pd.DataFrame([analysis]).to_excel(out / "dataset_summary.xlsx", index=False)
    pd.DataFrame(list(analysis["class_wise_object_count"].items()), columns=["class_name", "object_count"]).to_csv(out / "class_distribution.csv", index=False)
    pd.DataFrame([{"image": i.relative_path, "annotations": len(i.annotations), "accepted": sum(a.status == "accepted" for a in i.annotations)} for i in project.images]).to_csv(out / "image_annotation_summary.csv", index=False)
    (out / "readiness_score.json").write_text(json.dumps(ready, indent=2), encoding="utf-8")
    warning_text = "Warnings:\n" + "\n".join("- " + w for w in ready["warnings"]) + "\n\nRecommendations:\n" + "\n".join("- " + r for r in ready["recommendations"])
    (out / "warnings_and_recommendations.txt").write_text(warning_text, encoding="utf-8")
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>VisionForge Dataset Report</title><style>body{{font-family:Arial;background:#0B1120;color:#E5E7EB;padding:24px}}.card{{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:16px;margin:12px 0}}img{{max-width:100%;background:white;border-radius:8px}}</style></head><body><h1>VisionForge Dataset Report</h1><div class='card'><p>Project: {project.project_name}</p><p>Images: {analysis['total_images']}</p><p>Annotations: {analysis['total_annotations']}</p></div><div class='card'><h2>Readiness Score</h2><p style='font-size:32px'>{ready['score']} / 100</p><p>{ready['risk_level']}</p></div><div class='card'><img src='charts/class_distribution.png'><img src='charts/annotation_status.png'><img src='charts/object_size_distribution.png'></div></body></html>"""
    (out / "dataset_report.html").write_text(html, encoding="utf-8")
    return out
