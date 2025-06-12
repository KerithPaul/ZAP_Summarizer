import json

def parse_zap_json(json_content) -> dict:
    """
    Parses a summarized ZAP JSON content to extract vulnerabilities and summary.
    """
    results = {
        'summary': {},
        'alerts': [], # Renamed from 'vulnerabilities_by_type' for consistency with previous output structure
        'metadata': {} # Placeholder for any global metadata if found later
    }

    try:
        zap_report_data = json.loads(json_content)

        # Extract Summary
    
        if 'summary' in zap_report_data:
            summary_val = zap_report_data['summary']
            if isinstance(summary_val, str):
                try:
                    summary_val = json.loads(summary_val)
                except Exception:
                    summary_val = {}



                    
            if isinstance(summary_val, dict):
                results['summary'] = summary_val
      
        # Extract Vulnerabilities (Alerts)
        if 'vulnerabilities_by_type' in zap_report_data and isinstance(zap_report_data['vulnerabilities_by_type'], list):
            for vuln_item in zap_report_data['vulnerabilities_by_type']:
                # Mapping the JSON keys to a consistent output format
                alert_name = vuln_item.get('alert_type') # This seems to be the alert name/title
                description = vuln_item.get('description')
                solution = vuln_item.get('solution')
                risk = vuln_item.get('risk')
                count = vuln_item.get('count') # Number of instances for this alert type
                affected_urls = vuln_item.get('affected_urls', []) # List of affected URLs

                results['alerts'].append({
                    'alertName': alert_name if alert_name else 'Untitled Alert',
                    'description': description if description else 'No description provided.',
                    'solution': solution if solution else 'No solution provided.',
                    'risk': risk if risk else 'Unknown',
                    'count': count if count is not None else 0, # Ensure count is a number
                    'affected_urls': affected_urls
                })


    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        # Consider returning an empty/error state or raising the exception
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return results


your_json_content = """
{
  "summary": {
    "Low": 1,
    "Informational": 1
  },
  "vulnerabilities_by_type": [
    {
      "risk": "Low",
      "count": 4,
      "evidence": "",
      "solution": "Ensure that your web server, application server, load balancer, etc. is configured to enforce Strict-Transport-Security.",
      "parameter": "",
      "alert_tags": "CWE-319, OWASP 2021 A15",
      "alert_type": "Strict-Transport-Security Header Not Set (1)",
      "description": "HTTP Strict Transport Security (HSTS) is a web security policy mechanism whereby a web server declares that complying user agents (such as a web browser) are to interact with it using only secure HTTPS connections (i.e. HTTP layered over TLS/SSL). HSTS is an IETF standards track protocol and is specified in RFC 6797.",
      "affected_urls": [
        "https://google.com/",
        "https://google.com",
        "https://google.com/sitemap.xml",
        "...and 1 more"
      ]
    },
    {
      "risk": "Informational",
      "count": 1,
      "evidence": "Age: 960",
      "solution": "Validate that the response does not contain sensitive, personal or user-specific information. If it does, consider the use of the following HTTP response headers, to limit, or prevent the content being stored and retrieved from the cache by another user:\\nCache-Control: no-cache, no-store, must-revalidate, private\\nPragma: no-cache\\nExpires: 0\\nThis configuration directs both HTTP 1.0 and HTTP 1.1 compliant caching servers to not store the response, and to not retrieve the response (without validation) from the cache, in response to a similar request.",
      "parameter": "",
      "alert_tags": "CWE--1",
      "alert_type": "Retrieved from Cache (1)",
      "description": "The content was retrieved from a shared cache. If the response data is sensitive, personal or user-specific, this may result in sensitive information being leaked. In some cases, this may even result in a user gaining complete control of the session of another user, depending on the configuration of the caching components in use in their environment. This is primarily an issue where caching servers such as \\"proxy\\" caches are configured on the local network. This configuration is typically found in corporate or educational environments, for instance.",
      "affected_urls": [
        "https://google.com/robots.txt"
      ]
    }
  ]
}
"""

if __name__ == "__main__":
    parsed_data = parse_zap_json(your_json_content)
    print(json.dumps(parsed_data, indent=2))

    print("\n--- Summarized Alerts ---")
    for alert in parsed_data['alerts']:
        print(f"Alert: {alert['alertName']} (Risk: {alert['risk']})")
        print(f"  Description: {alert['description'][:100]}...") # Truncate for display
        print(f"  Solution: {alert['solution'][:100]}...") # Truncate for display
        print(f"  Count: {alert['count']}")
        print(f"  Affected URLs: {', '.join(alert['affected_urls'])}")
        print("-" * 30)

    print("\n--- Overall Summary ---")
    if parsed_data['summary']:
        for risk_level, count in parsed_data['summary'].items():
            print(f"{risk_level} Alerts: {count}")
    else:
        print("No overall summary data available.")