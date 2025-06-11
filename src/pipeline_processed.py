from datetime import datetime
from weasyprint import HTML
import traceback

from src.config import output_dir
from src.pipeline.html_parser import parse_zap_html
from src.pipeline.report_processing import summarize_with_ollama, generate_simplified_solutions
from src.pipeline.visualization_generator import generate_visualizations

from jinja2 import Environment, FileSystemLoader
import os

# Set up Jinja2 environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def process_report(report_id, html_content):
    """Full processing pipeline for HTML reports"""
    try:
        # 1. Parse HTML
        parsed_data = parse_zap_html(html_content)
       
        # 2. Generate executive summary
        executive_summary = summarize_with_ollama(parsed_data['alerts'])
       
        # 3. Simplify each alert
        simplified_alerts = generate_simplified_solutions(parsed_data['alerts'])
       
        # 4. Create visualizations
        charts = generate_visualizations(parsed_data['alerts'], report_id)
       
        # 5. Render PDF
        template = env.get_template("report_template.html")
        html_out = template.render(
            report_id=report_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            summary=executive_summary,
            alerts=simplified_alerts,
            metadata=parsed_data.get('metadata', {}),
            charts=charts
        )
       
        # 6. Generate PDF
        pdf_path = f"{output_dir}/{report_id}_security_report.pdf"
        HTML(string=html_out).write_pdf(pdf_path)
       
        print(f"✅ Generated report: {pdf_path}")
        return pdf_path
       
    except Exception as e:
        print(f"🚨 Error processing report: {str(e)}")
        traceback.print_exc()
        return None