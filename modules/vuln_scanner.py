import requests
import logging

logging.basicConfig(level=logging.WARNING)

class VulnScanner:
    def __init__(self, service_name, version):
        self.service = service_name.lower()
        self.version = version
        self.cves = []

    def check_nvd_api(self):
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={self.service}&versionStartInclude={self.version}"
        headers = {'Accept': 'application/json'}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('vulnerabilities', []):
                    cve_id = item['cve']['id']
                    severity = item['cve']['metrics']['cvssMetricV3'][0]['cvssData']['baseSeverity']
                    self.cves.append({
                        'id': cve_id,
                        'severity': severity,
                        'description': item['cve']['descriptions'][0]['value'][:100]
                    })
            else:
                logging.warning(f"NVD API Error: {response.status_code}")
        except Exception as e:
            logging.error(f"API Request Failed: {e}")

    def get_results(self):
        return self.cves