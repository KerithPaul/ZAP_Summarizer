import json
import requests
import re

from src.config import ollama_url, ollama_model


def summarize_with_ollama(alerts):
    """Generate executive summary using Ollama-Mistral"""
    prompt = f"""

    {json.dumps(alerts, indent=2)}
   
    Based on the provided Report Data, generate a summary report adhering to the following structure and guidelines:
    Overall Scan Summary:
    * State the total number of distinct alert types found.
    * Provide a clear breakdown of alerts by risk level (e.g., "X Low, Y Informational").
    Key Findings / Top Alerts:
    * For each distinct alert type identified in the 'alerts' list:
    * State the 'alertName' and its associated 'risk' level.
    * Mention the 'count' of instances found for this specific alert type.
    * Provide a very brief, 1-2 sentence summary of the 'description' to explain the vulnerability.
    * Provide a very brief, 1-2 sentence summary of the 'solution' for remediation.
    * Indicate if there are affected URLs (e.g., "affecting X URLs" or "affecting URLs such as Y"). Do not list all URLs if there are many; summarize or pick a few examples.
    Conclusion/Recommendations (Optional, if data allows for inference):
    * Provide a high-level statement about the overall security posture implied by this report.
    * If appropriate, suggest general next steps for addressing identified issues.
    Formatting Guidelines:
    * Use clear headings and bullet points for readability.
    * Keep all summaries extremely concise and to the point.
    * Maintain a professional, objective, and analytical tone.
    * Avoid conversational language, intros, or outros like "Here is your summary:" or "I hope this helps." Just provide the summary content.

    """
   
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        },
        timeout=120
    )
    return response.json()["response"]

def generate_simplified_solutions(alerts):
    """Generate non-technical solutions for each alert"""
    simplified_alerts = []
    for alert in alerts:
        prompt = f"""
        Explain this security vulnerability to a non-technical audience and provide a simple solution:
       
        alert_type: {alert.get('title', '')}
        Risk: {alert.get('risk', '')}
        description: {alert.get('description', '')[:500]}
        solution: {alert.get('solution', '')[:500]}
       
        Based on the provided Report Data, generate a summary report adhering to the following structure and guidelines:
        Overall Scan Summary:
        * State the total number of distinct alert types found.
        * Provide a clear breakdown of alerts by risk level (e.g., "X Low, Y Informational").
        Key Findings / Top Alerts:
        * For each distinct alert type identified in the 'alerts' list:
        * State the 'alertName' and its associated 'risk' level.
        * Mention the 'count' of instances found for this specific alert type.
        * Provide a very brief, 1-2 sentence summary of the 'description' to explain the vulnerability.
        * Provide a very brief, 1-2 sentence summary of the 'solution' for remediation.
        * Indicate if there are affected URLs (e.g., "affecting X URLs" or "affecting URLs such as Y"). Do not list all URLs if there are many; summarize or pick a few examples.
        Conclusion/Recommendations (Optional, if data allows for inference):
        * Provide a high-level statement about the overall security posture implied by this report.
        * If appropriate, suggest general next steps for addressing identified issues.
        Formatting Guidelines:
        * Use clear headings and bullet points for readability.
        * Keep all summaries extremely concise and to the point.
        * Maintain a professional, objective, and analytical tone.
        * Avoid conversational language, intros, or outros like "Here is your summary:" or "I hope this helps." Just provide the summary content.

        """
       
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2}
            },
            timeout=90
        )
        simplified = response.json()["response"]
       
        # Parse the structured response
        parts = re.split(r'\[(Simple Vulnerability Explanation|Business Impact|Actionable Solution Steps)\]', simplified)
        simplified_alerts.append({
            **alert,
            "simple_explanation": parts[2].strip() if len(parts) > 2 else simplified,
            "business_impact": parts[4].strip() if len(parts) > 4 else "",
            "simple_solution": parts[6].strip() if len(parts) > 6 else ""
        })
   
    return simplified_alerts