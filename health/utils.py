import http.client
import json
from collections import defaultdict
import re
import logging
import traceback

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lab_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LabReportAnalyzer')

class LabReportAnalyzer:
    def __init__(self):
        logger.info("Initializing LabReportAnalyzer")
        self.conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")
        self.headers = {
            'x-rapidapi-key': "6f3c3cdbd9msh091e6b2679812cap103be0jsn0b5e661fe201",
            'x-rapidapi-host': "copilot5.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        self.body_systems = {
            "metabolism": {
                "icon": "local_fire_department",
                "tests": ["glucose", "insulin", "thyroid", "metabolic"]
            },
            "nutrition": {
                "icon": "restaurant", 
                "tests": ["vitamin", "mineral", "protein", "albumin"]
            },
            "digestive": {
                "icon": "lunch_dining",
                "tests": ["liver", "enzyme", "bilirubin", "ALT", "AST"]
            },
            "blood": {
                "icon": "bloodtype",
                "tests": ["hemoglobin", "RBC", "WBC", "platelets"]
            },
            "heart": {
                "icon": "favorite",
                "tests": ["cholesterol", "HDL", "LDL", "triglycerides"]
            },
            "kidney": {
                "icon": "water_drop",
                "tests": ["creatinine", "BUN", "GFR", "urea"]
            },
            "immunity": {
                "icon": "shield",
                "tests": ["lymphocytes", "antibodies", "immunoglobulin"]
            }
        }

        self.patterns = {
            'measurement': r'(\d+\.?\d*)\s*(mg/dL|g/dL|U/L|%|mmol/L|µmol/L|ng/mL|pg/mL|mIU/L|µIU/mL|g/L|mmHg|fL|K/µL)',
            'range': r'Reference Range:\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',
            'test_name': r'^([A-Za-z\s&\-]+):\s*(\d+\.?\d*)',
            'abnormal_flags': r'(H|L|HIGH|LOW|CRITICAL|ABNORMAL)'
        }

    def analyze_with_ai(self, text):
        logger.info("Starting AI analysis")
        try:
            text_content = str(text) if text else ""
            logger.debug(f"Processing text content: {text_content[:100]}...")
            
            systems_prompt = "Analyze these lab results and categorize them into the following body systems:\n"
            for system, details in self.body_systems.items():
                systems_prompt += f"- {system.title()}: {', '.join(details['tests'])}\n"
            
            payload = json.dumps({
                "message": f"{systems_prompt}\nLab Results:\n{text_content}",
                "conversation_id": None,
                "tone": "BALANCED",
                "markdown": False
            })
            
            logger.debug("Sending request to API")
            self.conn.request("POST", "/copilot", payload, self.headers)
            response = self.conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            logger.info("API response received successfully")
            
            categories = self.categorize_results(text_content)
            logger.debug(f"Categorized results: {categories}")
            
            return {
                'result': data.get('response', 'Analysis pending'),
                'categories': categories
            }
        except Exception as e:
            logger.error(f"Error in analyze_with_ai: {str(e)}")
            logger.error(traceback.format_exc())
            return {'result': 'Analysis failed', 'categories': {}}

def extract_lab_values(self, text):
    logger.info("Starting lab value extraction")
    values = defaultdict(dict)
    text_content = str(text) if text else ""
    
    for line in text_content.split('\n'):
        for test_type, details in self.body_systems.items():
            for test in details['tests']:
                if test.lower() in line.lower():
                    if measurement := re.search(self.patterns['measurement'], line):
                        values[test] = {
                            'value': measurement.group(1),
                            'unit': measurement.group(2),
                            'system': test_type
                        }
                        if flag_match := re.search(self.patterns['abnormal_flags'], line):
                            values[test]['flag'] = flag_match.group(1)
    return values


def determine_status(self, value, reference_range):
        logger.debug(f"Determining status for value: {value}, range: {reference_range}")
        try:
            value = float(value)
            min_val = float(reference_range.get('min', 0))
            max_val = float(reference_range.get('max', 100))
            
            if value < min_val:
                return "low"
            elif value > max_val:
                return "high"
            return "normal"
        except (ValueError, TypeError) as e:
            logger.error(f"Error determining status: {str(e)}")
            return "unknown"

def categorize_results(self, text):
        logger.info("Starting result categorization")
        try:
            values = self.extract_lab_values(text)
            categories = defaultdict(list)
            
            for test, data in values.items():
                system = data.get('system')
                if system:
                    result = {
                        'test': test,
                        'value': data.get('value'),
                        'unit': data.get('unit'),
                        'status': 'abnormal' if data.get('flag') else 'normal'
                    }
                    categories[system].append(result)
                    logger.debug(f"Categorized {test} under {system}")
            
            return dict(categories)
        except Exception as e:
            logger.error(f"Error in categorize_results: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
def generate_summary(self, categories):
        logger.info("Generating summary")
        try:
            summary = {
                'abnormal': [],
                'optimal': [],
                'normal': []
            }
            
            for system, results in categories.items():
                for result in results:
                    if result['status'] == 'abnormal':
                        summary['abnormal'].append(f"{result['test']} in {system}")
                    elif result['status'] == 'normal':
                        summary['normal'].append(f"{result['test']} in {system}")
            
            logger.debug(f"Generated summary: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            logger.error(traceback.format_exc())
            return {'abnormal': [], 'optimal': [], 'normal': []}
