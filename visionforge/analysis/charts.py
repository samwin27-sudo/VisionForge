from pathlib import Path

def _plt():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; return plt

def class_distribution_chart(counts, output_path):
    plt=_plt(); p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True); fig=plt.figure(figsize=(10,5)); plt.bar(list(counts.keys()) or ['none'], list(counts.values()) or [0]); plt.xticks(rotation=45,ha='right'); plt.tight_layout(); fig.savefig(p); plt.close(fig); return p
def status_pie_chart(counts, output_path):
    plt=_plt(); p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True); fig=plt.figure(figsize=(5,5)); plt.pie(list(counts.values()) or [1], labels=list(counts.keys()) or ['none'], autopct='%1.1f%%'); fig.savefig(p); plt.close(fig); return p
def object_size_chart(counts, output_path):
    plt=_plt(); p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True); fig=plt.figure(figsize=(6,4)); labels=['small','medium','large']; plt.bar(labels,[counts.get(x,0) for x in labels]); fig.savefig(p); plt.close(fig); return p
