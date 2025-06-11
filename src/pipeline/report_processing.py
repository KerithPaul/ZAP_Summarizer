import json
import requests
import re

from src.config import ollama_url, ollama_model


def summarize_with_ollama(alerts):
    """Generate executive summary using Ollama-Mistral"""
    prompt = f"""
    You are a security analyst summarizing vulnerability scan results for non-technical executives.
    Below are security alerts found during scanning:
   
    {json.dumps(alerts, indent=2)}
   
    Create a concise executive summary covering:
    1. Overall risk posture (high/medium/low)
    2. Key business impacts
    3. Recommended action priorities
    4. Technical summary in simple terms
   
    Structure your response as:
    [Overall Risk Assessment]
    [Business Impact Analysis]
    [Priority Recommendations]
    [Simple Technical Explanation]
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
       
        Title: {alert.get('title', '')}
        Risk: {alert.get('risk', '')}
        Description: {alert.get('description', '')[:500]}
        Technical Solution: {alert.get('solution', '')[:500]}
       
        Structure your response as:
        [Simple Vulnerability Explanation]
        [Business Impact]
        [Actionable Solution Steps]
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