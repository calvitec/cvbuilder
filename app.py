from flask import Flask, render_template, request, send_file, jsonify, session
import os
import uuid
import re
import tempfile
import shutil
import json
from cv_generator import create_cv_from_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'calvin-cv-builder-pro-2026'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

GENERATED_FOLDER = 'generated'
if not os.path.exists(GENERATED_FOLDER):
    os.makedirs(GENERATED_FOLDER)

extracted_data_store = {}

# 4 Completely Different Layouts with unique designs
LAYOUTS = [
    {
        'id': 'classic',
        'name': 'Classic',
        'icon': 'fa-solid fa-crown',
        'color': 'from-blue-500 to-indigo-600',
        'bg': 'bg-gradient-to-br from-blue-50 to-indigo-50',
        'desc': 'Traditional two-column with sidebar',
        'structure': 'Sidebar + Main Content'
    },
    {
        'id': 'modern',
        'name': 'Modern',
        'icon': 'fa-solid fa-bolt',
        'color': 'from-purple-500 to-pink-500',
        'bg': 'bg-gradient-to-br from-purple-50 to-pink-50',
        'desc': 'Top header with timeline experience',
        'structure': 'Header + Timeline'
    },
    {
        'id': 'elegant',
        'name': 'Elegant',
        'icon': 'fa-solid fa-gem',
        'color': 'from-amber-500 to-orange-500',
        'bg': 'bg-gradient-to-br from-amber-50 to-orange-50',
        'desc': 'Centered with gold accents',
        'structure': 'Centered + Minimalist'
    },
    {
        'id': 'professional',
        'name': 'Professional',
        'icon': 'fa-solid fa-briefcase',
        'color': 'from-emerald-500 to-teal-500',
        'bg': 'bg-gradient-to-br from-emerald-50 to-teal-50',
        'desc': 'Left sidebar corporate style',
        'structure': 'Corporate + Structured'
    }
]

# Sample data for preview
SAMPLE_DATA = {
    'name': 'John Amwayi Ngatia',
    'title': 'Compliance Account Manager',
    'summary': 'Highly motivated professional with over 5 years of experience in tax administration, revenue management, and financial compliance. Currently pursuing a Master\'s degree at Moi University.',
    'skills': ['Tax Laws', 'Data Analytics', 'Auditing', 'Customer Service', 'Relationship Building', 'Python', 'SQL'],
    'experience': [
        {'company': 'Kenya Revenue Authority (KRA)', 'title': 'Compliance Account Manager', 'date': '2023 - Present', 'bullets': ['Manage tax compliance for 150+ taxpayers', 'Conduct tax audits and investigations', 'Prepare detailed reports for management']},
        {'company': 'Balkan Ltd', 'title': 'Research Associate', 'date': '2020 - 2022', 'bullets': ['Conducted market research and data analysis', 'Prepared comprehensive reports', 'Managed data collection processes']}
    ],
    'education': ['Master\'s Degree, Moi University (2024 - To Date)', 'Bachelor\'s Degree, Kenyatta University (2016 - 2021)'],
    'references': [
        {'name': 'Surbhi S. Vashisht', 'position': 'Head Teacher', 'email': 'surbhi@hillcrest.ac.ke', 'phone': '+254 733 941 398'}
    ],
    'phone': '+254 712 345 678',
    'email': 'john.ngatia@email.com'
}

def parse_cv_text(text):
    """Parse CV text into structured data"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    info = {
        'name': 'CURRICULUM VITAE', 'title': '', 'email': '', 'phone': '',
        'summary': '', 'skills': [], 'experience': [], 'education': [],
        'achievements': [], 'references': []
    }
    
    # ===== Extract Name =====
    for line in lines[:5]:
        if len(line) < 50 and not any(x in line.lower() for x in ['curriculum', 'vitae', 'cv', 'resume']):
            info['name'] = line
            break
    
    # ===== Extract Email & Phone =====
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        info['email'] = email_match.group()
    
    phone_patterns = [r'\+254\s?\d{9}', r'0\d{9}', r'07\d{8}', r'01\d{8}']
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            info['phone'] = phone_match.group()
            break
    
    # ===== Find sections =====
    sections = {}
    current_section = None
    section_keywords = {
        'education': ['education', 'academic'],
        'experience': ['employment', 'experience', 'work'],
        'skills': ['skill'],
        'achievements': ['qualification', 'additional', 'certification', 'award'],
        'references': ['reference', 'referee']
    }
    
    for line in lines:
        line_lower = line.lower()
        found = False
        for key, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line) < 40:
                current_section = key
                if key not in sections:
                    sections[key] = []
                found = True
                break
        if not found and current_section and line:
            sections[current_section].append(line)
    
    # ===== Extract Summary =====
    summary_lines = []
    edu_start = 999
    for i, l in enumerate(lines):
        if 'education' in l.lower():
            edu_start = i
            break
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if i < edu_start and len(line) > 20 and not any(x in line.lower() for x in ['curriculum', 'vitae', 'cv']):
            summary_lines.append(line)
    if summary_lines:
        info['summary'] = ' '.join(summary_lines)
    
    # ===== Education =====
    info['education'] = sections.get('education', [])[:10]
    
    # ===== Experience =====
    exp_lines = sections.get('experience', [])
    exp_section = []
    current_exp = None
    
    for line in exp_lines:
        if re.search(r'\d{4}', line):
            if current_exp:
                exp_section.append(current_exp)
            
            line_clean = line
            
            # Check for colon separator: "2023 – To Date: Compliance Account Manager – KRA"
            if ':' in line_clean:
                parts = line_clean.split(':')
                if len(parts) >= 2:
                    date_part = parts[0].strip()
                    rest = parts[1].strip()
                    if '–' in rest or '-' in rest:
                        rest_parts = re.split(r'[–\-]', rest)
                        if len(rest_parts) >= 2:
                            title_part = rest_parts[0].strip()
                            company_part = rest_parts[1].strip()
                            current_exp = {
                                'company': company_part,
                                'title': title_part,
                                'date': date_part,
                                'bullets': []
                            }
                        else:
                            current_exp = {
                                'company': rest,
                                'title': '',
                                'date': date_part,
                                'bullets': []
                            }
                    else:
                        current_exp = {
                            'company': rest,
                            'title': '',
                            'date': date_part,
                            'bullets': []
                        }
                else:
                    current_exp = {
                        'company': line_clean,
                        'title': '',
                        'date': '',
                        'bullets': []
                    }
            elif '–' in line_clean or '-' in line_clean:
                parts = re.split(r'[–\-]', line_clean)
                clean_parts = []
                for p in parts:
                    p_clean = p.strip()
                    if p_clean and not re.search(r'\d{4}', p_clean):
                        clean_parts.append(p_clean)
                
                if len(clean_parts) >= 2:
                    title_part = clean_parts[0].strip()
                    company_part = clean_parts[1].strip()
                    date_match = re.search(r'(\d{4}\s*[–\-]\s*[A-Za-z\s]+)', line_clean)
                    date_part = date_match.group(1) if date_match else ''
                    current_exp = {
                        'company': company_part,
                        'title': title_part,
                        'date': date_part,
                        'bullets': []
                    }
                else:
                    current_exp = {
                        'company': line_clean,
                        'title': '',
                        'date': '',
                        'bullets': []
                    }
            else:
                current_exp = {
                    'company': line_clean,
                    'title': '',
                    'date': '',
                    'bullets': []
                }
        elif current_exp and line and len(line) > 3:
            clean_line = re.sub(r'^[•\-]\s*', '', line)
            if clean_line and not any(x in clean_line.lower() for x in ['education', 'skill', 'qualification', 'reference']):
                current_exp['bullets'].append(clean_line)
    
    if current_exp:
        exp_section.append(current_exp)
    info['experience'] = exp_section
    
    # ===== Skills =====
    skills_lines = sections.get('skills', [])
    skills_found = []
    for line in skills_lines:
        parts = re.split(r'[•,;\n]', line)
        for part in parts:
            part = part.strip()
            if part and len(part) < 60 and len(part) > 2:
                part = re.sub(r'^[•\-]\s*', '', part)
                if part and not any(x in part.lower() for x in ['skills', 'abilities']):
                    skills_found.append(part)
    info['skills'] = skills_found[:15]
    
    # ===== Achievements =====
    ach_lines = sections.get('achievements', [])
    achievements_found = []
    for line in ach_lines:
        clean_line = re.sub(r'^[•\-]\s*', '', line)
        if clean_line and len(clean_line) > 3:
            achievements_found.append(clean_line)
    info['achievements'] = achievements_found[:8]
    
    # ===== References =====
    ref_lines = sections.get('references', [])
    references = []
    current_ref = {}
    for line in ref_lines:
        if line and not any(x in line.lower() for x in ['email:', 'phone:', 'tel:', 'address']):
            if len(line) > 5 and not re.match(r'^[\d\-+]', line):
                if current_ref and current_ref.get('name'):
                    references.append(current_ref)
                current_ref = {'name': line, 'position': '', 'email': '', 'phone': ''}
            elif line and current_ref:
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
                if email_match:
                    current_ref['email'] = email_match.group()
                    line = line.replace(email_match.group(), '').strip()
                    if line and not current_ref['position']:
                        current_ref['position'] = line
                phone_match = re.search(r'\+254\s?\d{9}|0\d{9}|07\d{8}|01\d{8}', line)
                if phone_match:
                    current_ref['phone'] = phone_match.group()
                    line = line.replace(phone_match.group(), '').strip()
                    if line and not current_ref['position']:
                        current_ref['position'] = line
                elif line and not current_ref['position']:
                    current_ref['position'] = line
    if current_ref and current_ref.get('name'):
        references.append(current_ref)
    info['references'] = references[:5]
    
    # ===== Extract Title =====
    if info['experience'] and info['experience'][0].get('title'):
        info['title'] = info['experience'][0]['title']
    
    return info

@app.route('/')
def index():
    return render_template('index.html', layouts=LAYOUTS, sample=SAMPLE_DATA)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        cv_text = request.form.get('cv_text', '')
        layout = request.form.get('layout', 'classic')
        
        if not cv_text:
            return render_template('index.html', error='Please paste your CV text.', layouts=LAYOUTS, sample=SAMPLE_DATA)
        
        cv_data = parse_cv_text(cv_text)
        cv_data['layout'] = layout
        session_id = uuid.uuid4().hex[:8]
        extracted_data_store[session_id] = cv_data
        
        return render_template('result.html', data=cv_data, session_id=session_id, layouts=LAYOUTS)
    
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}', layouts=LAYOUTS, sample=SAMPLE_DATA)

@app.route('/generate-pdf/<session_id>')
def generate_pdf(session_id):
    try:
        if session_id not in extracted_data_store:
            return render_template('error.html', message='Session expired. Please try again.')
        
        data = extracted_data_store[session_id]
        layout = data.get('layout', 'classic')
        
        # Generate PDF with selected layout
        pdf_path = create_cv_from_dict(data, layout)
        filename = os.path.basename(pdf_path)
        extracted_data_store['pdf_path'] = pdf_path
        
        return render_template('download.html', filename=filename, name=data.get('name', 'CV'))
    
    except Exception as e:
        return render_template('error.html', message=f'Error generating PDF: {str(e)}')

@app.route('/download/<filename>')
def download_cv(filename):
    try:
        # Check stored path
        if 'pdf_path' in extracted_data_store:
            stored_path = extracted_data_store.get('pdf_path')
            if stored_path and os.path.exists(stored_path):
                return send_file(stored_path, as_attachment=True, download_name=filename)
        
        # Check generated folder
        filepath = os.path.join('generated', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        # Check temp directory
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(temp_path):
            return send_file(temp_path, as_attachment=True, download_name=filename)
        
        return render_template('error.html', message='File not found. Please generate again.')
    
    except Exception as e:
        return render_template('error.html', message=f'Error: {str(e)}')

@app.route('/api/preview/<layout_id>')
def preview_layout(layout_id):
    """Return preview data for a layout"""
    return jsonify(SAMPLE_DATA)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
