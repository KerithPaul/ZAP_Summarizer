import matplotlib.pyplot as plt
import pandas as pd

from src.config import output_dir


def generate_visualizations(alerts, report_id):
    """Create comprehensive visualizations for the report"""
    # Risk distribution
    risk_counts = pd.Series([alert['risk'] for alert in alerts]).value_counts()
   
    plt.figure(figsize=(10, 12))
   
    # 1. Risk Distribution (Pie Chart)
    plt.subplot(2, 1, 1)
    colors = {'High': '#ff6b6b', 'Medium': '#ffd166', 'Low': '#06d6a0', 'Unknown': '#adb5bd'}
    risk_colors = [colors.get(r, '#6c757d') for r in risk_counts.index]
    plt.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', colors=risk_colors)
    plt.title('Risk Level Distribution')
   
    # 2. Confidence Distribution (Bar Chart)
    plt.subplot(2, 1, 2)
    conf_counts = pd.Series([alert.get('confidence', 'Unknown') for alert in alerts]).value_counts()
    conf_colors = {'High': '#2a9d8f', 'Medium': '#e9c46a', 'Low': '#e76f51', 'Unknown': '#6c757d'}
    conf_colors = [conf_colors.get(c, '#6c757d') for c in conf_counts.index]
    plt.bar(conf_counts.index, conf_counts.values, color=conf_colors)
    plt.title('Confidence Level Distribution')
    plt.xlabel('Confidence Level')
    plt.ylabel('Number of Alerts')
   
    viz_path = f"{output_dir}/{report_id}_visualizations.png"
    plt.tight_layout()
    plt.savefig(viz_path)
    plt.close()
   
    return {"visualizations": viz_path}