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
   # Matches test names with various formats, including parentheses, slashes, and special characters
    'test_line': r'([\w\s\-\/\(\)\,\+\%\d]+?)\s+([\d\.]+)\s*([\w\/µ\%\^\d]+\/?\w*)\s*([\d\.]+\s*-\s*[\d\.]+|[\d\.]+\s*(?:and|to)\s*[\d\.]+)?\s*([NHL\*]+)?',
    
    # Captures all possible measurement units across different lab standards
    'measurement': r'(\d+\.?\d*)\s*(mmol/L|µmol/L|g/L|U/L|mg/dL|g/dL|%|ng/mL|pg/mL|mIU/L|µIU/mL|mmHg|fL|K/µL|10\^3/µL|10\^6/µL|mEq/L|IU/L|µg/L|ng/L|pmol/L|kU/L)',
    
    # Matches various range formats including decimal points and different separators
    'range': r'([\d\.]+)\s*(?:-|to|and|\~)\s*([\d\.]+)',
    
    # Captures all possible flag indicators including combinations
    'flags': r'([NHL\*\+\-\!\?]+)',
    
    # Identifies critical values with various markings
    'critical': r'(\*\*|\!\!|\+\+|!!|CRIT|CRITICAL)',
    
    # Comprehensive patient information pattern
    'patient_info': r'(?:Patient|Name|ID):\s*(.*?)\s*(?:Age|DOB)[\s\/]*(?:Sex)?:\s*(\d+)?\s*[\/-]?\s*([MFmf])',
    
    # Multiple date formats from different regions
    'collection_date': r'(?:Collection|Draw|Sample|Test)\s*(?:Date|Time):\s*(\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{2,4})?(?:\s+(\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?)?)',
     # Expanded section headers for different report types
    'section_header': r'^(?:REPORT\s+FOR|TEST\s+RESULTS?|LABORATORY\s+RESULTS?|ANALYSIS\s+RESULTS?)?\s*(Complete Blood Count|CBC|Liver Function Test|LFT|Lipid Profile|Kidney Function|Thyroid Profile|Metabolic Panel|Chemistry Panel|Hematology|Serology|Urinalysis|Immunology|Hormone Analysis|Tumor Markers|Cardiac Markers|Diabetes Panel)',
    
    # Various ratio calculations
    'ratio': r'([\w\s\/\-\+]+(?:Ratio|Index|Score))\s*[:\=]?\s*([\d\.]+)',
    
    # Extended unit patterns including international variations
    'unit_extended': r'(nmol/L|pmol/L|mIU/mL|ng/dL|µg/dL|mEq/L|kIU/L|µIU/mL|g/mmol|mmol/mol|µkat/L|mkat/L)',
    
    # International date formats
    'date_formats': r'(\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{2,4})|(\d{4}[-\/\.]\d{1,2}[-\/\.]\d{1,2})',
    
    # 12/24 hour time formats
    'time_format': r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)',
    
    # Comprehensive report sections with subsections
    'report_section': r'(?:^|\n)((?:COMPLETE\s+)?(?:BLOOD\s+COUNT|CBC|DIFFERENTIAL|CHEMISTRY|METABOLIC\s+PANEL|LIPID\s+PANEL|LIVER\s+PANEL|KIDNEY\s+PANEL|THYROID\s+PANEL|CARDIAC\s+PANEL|DIABETES\s+PANEL)(?:\s+RESULTS?)?)(.*?)(?=\n(?:(?:COMPLETE\s+)?(?:BLOOD\s+COUNT|CBC|DIFFERENTIAL|CHEMISTRY|METABOLIC\s+PANEL|LIPID\s+PANEL|LIVER\s+PANEL|KIDNEY\s+PANEL|THYROID\s+PANEL|CARDIAC\s+PANEL|DIABETES\s+PANEL)(?:\s+RESULTS?)?)|$)',
    
    # Detailed test name pattern
    'test_name': r'^([\w\s\-\/\(\)\,\+\%\d]+?)(?=\s+[\d\.]+)',
    
    # Scientific notation and decimal values
    'numeric_value': r'\b(\d+\.?\d*(?:[Ee][\+\-]?\d+)?)\b',
    
    # Reference intervals with various formats
    'reference_interval': r'(?:Reference\s+(?:Range|Interval|Values?)|Normal\s+Range|Expected\s+Values?)?\s*(?:<|>|≤|≥)?\s*([\d\.]+)\s*(?:-|to|and)\s*([\d\.]+)',
    
    # Comprehensive abnormal flags
    'abnormal_flags': r'\b([HLhl\*\+\!\?]+)\b',
    
    # All possible unit combinations
    'units_all': r'\b(g/L|mg/dL|µmol/L|mmol/L|U/L|%|ng/mL|pg/mL|fL|10\^9/L|10\^12/L|mEq/L|IU/L|µg/L|ng/L|pmol/L|kU/L|µkat/L|mkat/L|g/mmol|mmol/mol)\b'
}

    def analyze_with_ai(self, text):
        logger.info("Starting AI analysis")
        text_content = str(text) if text else ""
        
        extracted_values = self.extract_lab_values(text_content)
        logger.info(f"Extracted values: {extracted_values}")

        prompt = f"""Analyze these lab results in simple, patient-friendly language:
        1. What's Normal: List all tests that are within healthy ranges
        2. Areas of Concern: Highlight any abnormal values and what they mean for health
        3. Action Steps: Suggest lifestyle changes or follow-up actions
        4. Simple Summary: Brief overview in everyday language
        
        Lab Values: {extracted_values}"""

        payload = json.dumps({
            "message": prompt,
            "conversation_id": None,
            "tone": "BALANCED",
            "markdown": False
        })

        logger.info(f"Sending patient-focused prompt: {prompt}")
        self.conn.request("POST", "/copilot", payload, self.headers)
        response = self.conn.getresponse()
        ai_analysis = json.loads(response.read().decode("utf-8"))
        
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
