import http.client
import json
from collections import defaultdict
import re

class LabReportAnalyzer:
    def __init__(self):
        self.conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")
        self.headers = {
            'x-rapidapi-key': "6f3c3cdbd9msh091e6b2679812cap103be0jsn0b5e661fe201",
            'x-rapidapi-host': "copilot5.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        self.body_systems = {
            "metabolism": ["glucose", "insulin", "thyroid", "metabolic"],
            "nutrition": ["vitamin", "mineral", "protein", "albumin"],
            "digestive": ["liver", "enzyme", "bilirubin", "ALT", "AST"],
            "blood": ["hemoglobin", "RBC", "WBC", "platelets"],
            "heart": ["cholesterol", "HDL", "LDL", "triglycerides"],
            "kidney": ["creatinine", "BUN", "GFR", "urea"],
            "immunity": ["lymphocytes", "antibodies", "immunoglobulin"]
        }

        self.patterns = {
            'measurement': r'(\d+\.?\d*)\s*(mg/dL|g/dL|U/L|%|mmol/L|µmol/L|ng/mL|pg/mL|mIU/L|µIU/mL|g/L|mmHg|fL|K/µL)',
            'range': r'Reference Range:\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',
            'date': r'(Date|Collected):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'time': r'Time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            'patient_id': r'(Patient ID|MRN):\s*([A-Z0-9-]+)',
            'doctor_name': r'(Dr\.|Doctor)\s+([A-Za-z\s\.]+)',
            'diagnosis': r'(Diagnosis|Clinical Indication):\s*(.+)',
            'specimen': r'(Specimen|Sample Type):\s*([A-Za-z\s]+)',
            'test_name': r'^([A-Za-z\s&\-]+):\s*(\d+\.?\d*)',
            'abnormal_flags': r'(H|L|HIGH|LOW|CRITICAL|ABNORMAL)',
            'units_extended': r'(ng/dL|pmol/L|mcg/dL|mEq/L|10\^3/µL|10\^6/µL)',
            'percentages': r'(\d+\.?\d*)\s*%',
            'ratios': r'(\d+\.?\d*)\s*:\s*(\d+\.?\d*)',
            'blood_pressure': r'(\d{2,3})/(\d{2,3})\s*mmHg'
        }

    def analyze_with_ai(self, text):
        print("Starting AI analysis...")
        print(f"Input text: {text}")

        payload = json.dumps({
            "message": f"Analyze these lab results as a medical lab professional: {text}",
            "conversation_id": None,
            "tone": "BALANCED",
            "markdown": False,
            "photo_url": None
        })
        print(f"Sending payload to API: {payload}")


        self.conn.request("POST", "/copilot", payload, self.headers)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        print(f"Sending payload to API: {payload}")

        
        if 'response' in data:
            print("No analysis result found in response")
            return {'result': data['response']}
        return {'result': 'Analysis not available'}

    def extract_lab_values(self, text):
        print("Starting lab value extraction...")
        ai_analysis = self.analyze_with_ai(text)
        values = defaultdict(dict)

        print(f"AI Analysis result: {ai_analysis}")
        
        if 'result' in ai_analysis:
            analysis_text = ai_analysis['result']

            for line in analysis_text.split('\n'):
                for test_type, keywords in self.body_systems.items():
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            measurement = re.search(self.patterns['measurement'], line)
                            if measurement:
                                values[test_type][keyword] = measurement.group(1)
                for test_type, keywords in self.body_systems.items():
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            measurement = re.search(self.patterns['measurement'], line)
                            if measurement:
                                values[keyword] = {
                                    'value': measurement.group(1),
                                    'unit': measurement.group(2)
                                }
                                
                                if range_match := re.search(self.patterns['range'], line):
                                    values[keyword]['range'] = {
                                        'min': range_match.group(1),
                                        'max': range_match.group(2)
                                    }
                                    
                                if flag_match := re.search(self.patterns['abnormal_flags'], line):
                                    values[keyword]['flag'] = flag_match.group(1)
                                    
                                if specimen_match := re.search(self.patterns['specimen'], line):
                                    values[keyword]['specimen'] = specimen_match.group(2)
                                    
                                if ratio_match := re.search(self.patterns['ratios'], line):
                                    values[keyword]['ratio'] = f"{ratio_match.group(1)}:{ratio_match.group(2)}"
                                    
                                if doctor_match := re.search(self.patterns['doctor_name'], line):
                                    values[keyword]['doctor'] = doctor_match.group(2)
                                    
                                if date_match := re.search(self.patterns['date'], line):
                                    values[keyword]['test_date'] = date_match.group(2)
        return values

    def determine_status(self, test, value, reference_range):
        try:
            value = float(value)
            test_range = reference_range.get(test, {})
            
            if not test_range:
                return "unknown"
                
            min_val = test_range.get('min')
            max_val = test_range.get('max')
            
            if value < min_val:
                return "low"
            elif value > max_val:
                return "high"
            else:
                return "normal"
        except (ValueError, TypeError):
            return "unknown"

    def get_recommendations(self, test, value, system):
        try:
            value = float(value)
            recommendations = []
            
            if system == "metabolism":
                if test.lower() == "glucose":
                    if value > 100:
                        recommendations.append("Consider dietary changes and regular exercise")
                    elif value < 70:
                        recommendations.append("Monitor blood sugar levels more frequently")
                        
            elif system == "heart":
                if test.lower() == "total cholesterol":
                    if value > 200:
                        recommendations.append("Consider lifestyle changes and dietary modifications")
                        
            elif system == "liver":
                if test.lower() in ["alt", "ast"] and value > 40:
                    recommendations.append("Follow up with hepatologist recommended")
                    
            elif system == "kidney":
                if test.lower() == "creatinine" and value > 1.3:
                    recommendations.append("Schedule follow-up with nephrologist")
                    
            elif system == "blood":
                if test.lower() == "hemoglobin" and value < 13.5:
                    recommendations.append("Iron supplementation may be needed")
                    
            elif system == "immunity":
                if test.lower() == "wbc" and value < 4.5:
                    recommendations.append("Immune system support recommended")
                    
            if not recommendations:
                recommendations.append("Results within normal range. Continue current health practices.")
                
            return recommendations
            
        except (ValueError, TypeError):
            return ["Unable to provide recommendations for this result"]

    def categorize_results(self, values):
        categories = defaultdict(list)
        for test, data in values.items():
            for system, keywords in self.body_systems.items():
                if any(keyword.lower() in test.lower() for keyword in keywords):
                    result = {
                        'test': test,
                        'value': data.get('value'),
                        'unit': data.get('unit'),
                        'status': self.determine_status(test, data.get('value'), {}),
                        'recommendations': self.get_recommendations(test, data.get('value'), system)
                    }
                    categories[system].append(result)
        return categories

    def generate_summary(self, categories):
        summary_text = json.dumps(categories)
        ai_insights = self.analyze_with_ai(summary_text)
        
        summary = {
            'abnormal': [],
            'optimal': [],
            'normal': []
        }
        
        if 'result' in ai_insights:
            analysis = ai_insights['result']
            for line in analysis.split('\n'):
                if 'abnormal' in line.lower():
                    summary['abnormal'].append(line)
                elif 'optimal' in line.lower():
                    summary['optimal'].append(line)
                else:
                    summary['normal'].append(line)
                    
        return summary

    def translate_text(self, text, target_lang):
        payload = json.dumps({
            "message": f"Translate this medical text to {target_lang}: {text}",
            "conversation_id": None,
            "tone": "BALANCED",
            "markdown": False,
            "photo_url": None
        })

        self.conn.request("POST", "/copilot", payload, self.headers)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        return data.get('response', text)
