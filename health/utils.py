import http.client
import json
from collections import defaultdict
import re
import logging
import traceback

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
            'x-rapidapi-key': "d35c484194msha36b2157ac188d6p17ddc4jsn651071d2461b",
            'x-rapidapi-host': "copilot5.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        self.body_systems = {
    "blood": {
        "icon": "bloodtype",
        "tests": ["RBC", "Hemoglobin", "HB", "Hgb", "MCV", "MCH", "MCHC", "RDW", "Platelet", "MPV"]
    },
    "immunity": {
        "icon": "shield",
        "tests": ["WBC", "Neutrophil", "Lymphocyte", "Monocyte", "Eosinophil", "Basophil", "Differential"]
    },
    "metabolism": {
        "icon": "local_fire_department",
        "tests": ["Glucose", "eAG", "HbA1c", "Insulin", "TSH", "T4", "T3", "Metabolic"]
    },
    "liver": {
        "icon": "science",
        "tests": ["ALT", "AST", "ALP", "GGT", "Bilirubin", "Albumin", "Protein", "Globulin"]
    },
    "kidney": {
        "icon": "water_drop",
        "tests": ["Creatinine", "BUN", "eGFR", "Urea", "Sodium", "Potassium", "Chloride", "CO2"]
    },
    "heart": {
        "icon": "favorite",
        "tests": ["Cholesterol", "HDL", "LDL", "Triglycerides", "CK", "Troponin", "BNP"]
    },
    "pancreas": {
        "icon": "opacity",
        "tests": ["Amylase", "Lipase", "Glucose", "C-peptide"]
    },
    "thyroid": {
        "icon": "psychology",
        "tests": ["TSH", "T4", "T3", "Free T4", "Free T3", "TPO", "Thyroglobulin"]
    }
}


        self.patterns = {
    'test_line': r'^([\w\s\(\)\/]+?)\s+([\d\.]+)\s*([HL\*]*)\s*([\w\/\%]+)\s*([\d\.-]+(?:\s*-\s*[\d\.]+)?)',
    'measurement': r'(\d+\.?\d*)\s*(mg/dL|g/dL|U/L|%|mmol/L|µmol/L|ng/mL|pg/mL|mIU/L|µIU/mL|g/L|mmHg|fL|K/µL|M/mcL)',
    'range': r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',
    'flags': r'([HL]\*{0,2})',
    'critical': r'\*\*',
    'patient_info': r'Name:\s*(.*?)\s*Age\/Sex:\s*(\d+)\/([MF])',
    'collection_date': r'Collection Date\/Time:\s*(\d{2}\/\d{2}\/\d{2}\s+\d{2}:\d{2})',
    'report_section': r'(COMPLETE BLOOD COUNT|DIFFERENTIAL|CHEMISTRY|LIPID PANEL)(.*?)(?=(COMPLETE BLOOD COUNT|DIFFERENTIAL|CHEMISTRY|LIPID PANEL|\Z))',
    'test_pattern': r'([\w\s\(\)\-\.]+?):\s*([\d\.]+)\s*([A-Za-z\/\s]+)',
    'test_name': r'^([A-Za-z\s&\-]+):\s*(\d+\.?\d*)',
    'abnormal_flags': r'(H|L|HIGH|LOW|CRITICAL|ABNORMAL)',
    'units_extended': r'(ng/dL|pmol/L|mcg/dL|mEq/L|10\^3/µL|10\^6/µL)',
    'percentages': r'(\d+\.?\d*)\s*%',
    'ratios': r'(\d+\.?\d*)\s*:\s*(\d+\.?\d*)',
    'blood_pressure': r'(\d{2,3})/(\d{2,3})\s*mmHg',
    'doctor_name': r'(Dr\.|Doctor)\s+([A-Za-z\s\.]+)',
    'diagnosis': r'(Diagnosis|Clinical Indication):\s*(.+)',
    'specimen': r'(Specimen|Sample Type):\s*([A-Za-z\s]+)',
    'patient_id': r'(Patient ID|MRN):\s*([A-Z0-9-]+)'
}


    def analyze_with_ai(self, text):
        logger.info("Starting AI analysis")
        text_content = str(text) if text else ""
        
        extracted_values = self.extract_lab_values(text_content)
        logger.info(f"Extracted values: {extracted_values}")

        prompt = f"""Provide a clear medical analysis for these lab results:
        1. Key findings
        2. Main abnormalities and their significance
        3. Brief interpretation for each abnormal value
        4. Overall health implications
        
        Values: {extracted_values}"""

        payload = json.dumps({
            "message": prompt,
            "conversation_id": None,
            "tone": "BALANCED",
            "markdown": False
        })

        logger.info(f"Sending summarized prompt: {prompt}")
        self.conn.request("POST", "/copilot", payload, self.headers)
        response = self.conn.getresponse()
        ai_analysis = json.loads(response.read().decode("utf-8"))

         # Extract the message from the nested AI response
        interpretation = ai_analysis.get('data', {}).get('message', '')
        
        logger.info(f"AI Response: {ai_analysis}")

        return {
            'result': 'Analysis completed',
            'categories': self.categorize_results(extracted_values),
            'interpretations': interpretation
        }




    def extract_lab_values(self, text):
        logger.info("Starting lab value extraction")
        values = defaultdict(dict)
        
        # Enhanced test pattern matching
        for line in text.split('\n'):
            match = re.search(self.patterns['test_line'], line)
            if match:
                test_name, value, flag, unit, ref_range = match.groups()
                test_name = test_name.strip()
                
                for system, details in self.body_systems.items():
                    if any(test.lower() in test_name.lower() for test in details['tests']):
                        values[test_name] = {
                            'value': value,
                            'unit': unit,
                            'flag': flag if flag else '',
                            'reference_range': ref_range,
                            'system': system,
                            'critical': bool(re.search(self.patterns['critical'], flag))
                        }
        
        return values

    def categorize_results(self, values):
        logger.info("Starting result categorization")
        categories = defaultdict(list)
        
        for test_name, data in values.items():
            system = data.get('system')
            if system:
                result = {
                    'test': test_name,
                    'value': data['value'],
                    'unit': data['unit'],
                    'status': 'critical' if data['critical'] else 'abnormal' if data['flag'] else 'normal',
                    'flag': data['flag'],
                    'reference_range': data['reference_range']
                }
                categories[system].append(result)
        
        return dict(categories)

    def generate_summary(self, categories):
        summary = {
            'critical': [],
            'abnormal': [],
            'normal': []
        }
        
        for system, results in categories.items():
            for result in results:
                if result['status'] == 'critical':
                    summary['critical'].append(f"{result['test']} in {system}")
                elif result['status'] == 'abnormal':
                    summary['abnormal'].append(f"{result['test']} in {system}")
                else:
                    summary['normal'].append(f"{result['test']} in {system}")
        
        return summary
