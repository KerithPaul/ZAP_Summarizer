from bs4 import BeautifulSoup
import re

def parse_zap_html(html_content):
    """Parse ZAP HTML reports to extract alerts and metadata"""
    soup = BeautifulSoup(html_content, 'html.parser')
    results = {
        'alerts': [],
        'metadata': {}
    }
   
    # Extract alert sections
    for alert_section in soup.find_all(['h1', 'h2', 'h3'], string=re.compile('Alerts', re.IGNORECASE)):
        next_elem = alert_section.find_next_sibling()
        while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
            if next_elem.name == 'div' and 'alert' in next_elem.get('class', []):
                alert = {}
               
                # Extract risk and confidence
                risk_match = re.search(r'Risk=(\w+)', next_elem.text)
                confidence_match = re.search(r'Confidence=(\w+)', next_elem.text)
                alert['risk'] = risk_match.group(1) if risk_match else 'Unknown'
                alert['confidence'] = confidence_match.group(1) if confidence_match else 'Unknown'
               
                # Extract URL
                url_elem = next_elem.find('b', string=re.compile(r'https?://'))
                alert['url'] = url_elem.text.strip() if url_elem else 'No URL found'
               
                # Extract alert title
                title_elem = next_elem.find('b', string=re.compile(r'\d+\.\s+'))
                alert['title'] = title_elem.text.strip() if title_elem else 'Untitled Alert'
               
                # Extract description
                desc_elem = next_elem.find(string=re.compile(r'Alert description'))
                if desc_elem:
                    description = []
                    next_sib = desc_elem.find_next_sibling()
                    while next_sib and next_sib.name != 'h4':
                        if next_sib.name == 'p':
                            description.append(next_sib.text.strip())
                        next_sib = next_sib.find_next_sibling()
                    alert['description'] = '\n'.join(description)
               
                # Extract solution if available
                solution_elem = next_elem.find(string=re.compile(r'Solution'))
                if solution_elem:
                    solution = []
                    next_sib = solution_elem.find_next_sibling()
                    while next_sib and next_sib.name != 'h4':
                        if next_sib.name == 'p':
                            solution.append(next_sib.text.strip())
                        next_sib = next_sib.find_next_sibling()
                    alert['solution'] = '\n'.join(solution)
               
                results['alerts'].append(alert)
            next_elem = next_elem.find_next_sibling()
   
    # Extract metadata tables
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if cells:
                rows.append(dict(zip(headers, cells)))
        if rows:
            results['metadata'] = rows[0]  # Take first row as metadata
   
    return results

