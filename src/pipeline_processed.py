import datetime
import traceback
import os
from jinja2 import Environment, FileSystemLoader

from src.config import output_dir
from src.pipeline.json_parser import parse_zap_json 
from src.pipeline.report_processing import summarize_with_ollama, generate_simplified_solutions
from src.pipeline.visualization_generator import generate_visualizations

# Set up Jinja2 Environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def process_report(report_id, json_content): 
    """Full processing pipeline for HTML reports"""

    try:

        parsed_data = parse_zap_json(json_content) 
        executive_summary = summarize_with_ollama(parsed_data['alerts'])

        simplified_alerts = generate_simplified_solutions(parsed_data['alerts'])
      
        charts = generate_visualizations(parsed_data['alerts'], report_id) 

        template = env.get_template("report_template.html")
        html_out = template.render(
            report_id=report_id,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            summary=parsed_data.get('summary', {}),
            alerts=simplified_alerts,
            metadata=parsed_data.get('metadata', {}),
            charts=charts
            )

        # 6. Save HTML file instead of generating PDF
        html_file_name = f"{report_id}_security_report.html"
        html_file_path = os.path.join(output_dir, html_file_name)

        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_out)

        print(f"Generated HTML report: {html_file_path}")
        return html_file_path # Return the path to the HTML file

    except Exception as e:
        print(f"Error processing report: {str(e)}") #
        traceback.print_exc() #
        return None #
