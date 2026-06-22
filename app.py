from flask import Flask, render_template, request, send_file, jsonify, session
import os
import uuid
import re
import tempfile
import shutil
import json
from datetime import datetime
from cv_generator import create_cv_from_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'calvin-cv-builder-pro-2026'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Inject current year into all templates to avoid undefined now() calls
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

GENERATED_FOLDER = 'generated'
if not os.path.exists(GENERATED_FOLDER):
    os.makedirs(GENERATED_FOLDER)

extracted_data_store = {}

# 6 Layouts (expanded to support premium themes)
LAYOUTS = [
    {'id': 'classic', 'name': 'Classic', 'icon': 'fa-solid fa-crown', 'color': 'from-blue-500 to-indigo-600', 'bg': 'bg-gradient-to-br from-blue-50 to-indigo-50', 'desc': 'Traditional two-column layout with sidebar for contact and skills.'},
    {'id': 'modern', 'name': 'Modern', 'icon': 'fa-solid fa-bolt', 'color': 'from-purple-500 to-pink-500', 'bg': 'bg-gradient-to-br from-purple-50 to-pink-50', 'desc': 'Top header, timeline-style experience and clean, contemporary lines.'},
    {'id': 'elegant', 'name': 'Elegant', 'icon': 'fa-solid fa-gem', 'color': 'from-amber-500 to-orange-500', 'bg': 'bg-gradient-to-br from-amber-50 to-orange-50', 'desc': 'Centered, minimalist and sophisticated with gold accents.'},
    {'id': 'professional', 'name': 'Professional', 'icon': 'fa-solid fa-briefcase', 'color': 'from-emerald-500 to-teal-500', 'bg': 'bg-gradient-to-br from-emerald-50 to-teal-50', 'desc': 'Corporate, structured layout ideal for business roles.'},
    {'id': 'creative', 'name': 'Creative', 'icon': 'fa-solid fa-palette', 'color': 'from-pink-500 to-violet-500', 'bg': 'bg-gradient-to-br from-pink-50 to-violet-50', 'desc': 'Bold color blocks and playful typography for creative professionals.'},
    {'id': 'minimal', 'name': 'Minimal', 'icon': 'fa-solid fa-ellipsis', 'color': 'from-gray-700 to-gray-900', 'bg': 'bg-gradient-to-br from-white to-gray-50', 'desc': 'Maximum white-space and clean typography for a sleek look.'}
]

SAMPLE_DATA = {
    'name': 'John Amwayi Ngatia',
    'title': 'Compliance Account Manager',
    'summary': 'Highly motivated professional with over 5 years of experience in tax administration, revenue management, and financial compliance.',
    'skills': ['Tax Laws', 'Data Analytics', 'Auditing', 'Customer Service', 'Relationship Building'],
    'experience': [
        {'company': 'Kenya Revenue Authority (KRA)', 'title': 'Compliance Account Manager', 'date': '2023 - Present', 'bullets': ['Manage tax compliance for 150+ taxpayers', 'Conduct tax audits and reconciliations']},
        {'company': 'Balkan Ltd', 'title': 'Research Associate', 'date': '2020 - 2022', 'bullets': ['Conducted market research and data analysis', 'Prepared comprehensive reports']}
    ],
    'education': ["Master's Degree, Moi University (2024 - To Date)", "Bachelor's Degree, Kenyatta University (2016 - 2021)"],
    'references': [{'name': 'Surbhi S. Vashisht', 'position': 'Head Teacher', 'email': 'surbhi@hillcrest.ac.ke', 'phone': '+254 733 941 398'}],
    'phone': '+254 712 345 678',
    'email': 'john.ngatia@email.com'
}


def parse_cv_text(text):
    """Parse CV text into structured data - Handles ALL formats including bullet points"""
    if not text:
        return {
            'name': 'CURRICULUM VITAE', 'title': '', 'email': '', 'phone': '',
            'summary': '', 'skills': [], 'experience': [], 'education': [],
            'achievements': [], 'references': []
        }
    
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    info = {
        'name': 'CURRICULUM VITAE', 'title': '', 'email': '', 'phone': '',
        'summary': '', 'skills': [], 'experience': [], 'education': [],
        'achievements': [], 'references': []
    }
    
    # ===== Extract Name =====
    for line in lines[:5]:
        if len(line) < 50 and not any(x in line.lower() for x in ['curriculum', 'vitae', 'cv', 'resume']):
            if not any(x in line.lower() for x in ['education', 'employment', 'skill', 'reference']):
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
    for line in lines:
        if 'education' in line.lower():
            break
        if len(line) > 20 and not any(x in line.lower() for x in ['curriculum', 'vitae', 'cv']):
            if not any(x in line.lower() for x in ['education', 'employment', 'skill', 'reference']):
                summary_lines.append(line)
    if summary_lines:
        info['summary'] = ' '.join(summary_lines[:5])
    
    # ===== Education =====
    info['education'] = sections.get('education', [])[:10]
    
    # ===== Experience =====
    exp_lines = sections.get('experience', [])
    exp_section = []
    current_exp = None
    
    for line in exp_lines:
        # Check if line has a year (date pattern)
        has_year = re.search(r'\d{4}', line)
        
        if has_year:
            if current_exp:
                exp_section.append(current_exp)
            
            line_clean = line
            
            # Try multiple parsing strategies
            date_part = ''
            title_part = ''
            company_part = ''
            
            # Strategy 1: Colon separator "2023 – To Date: Title – Company"
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
                        else:
                            company_part = rest
                    else:
                        company_part = rest
            
            # Strategy 2: Dash separator "2023 – To Date – Title – Company"
            elif '–' in line_clean or '-' in line_clean:
                parts = re.split(r'[–\-]', line_clean)
                clean_parts = [p.strip() for p in parts if p.strip()]
                
                # Remove date from parts
                date_parts = []
                non_date_parts = []
                for p in clean_parts:
                    if re.search(r'\d{4}', p):
                        date_parts.append(p)
                    else:
                        non_date_parts.append(p)
                
                date_part = ' – '.join(date_parts) if date_parts else ''
                
                if len(non_date_parts) >= 2:
                    title_part = non_date_parts[0].strip()
                    company_part = non_date_parts[1].strip()
                elif len(non_date_parts) == 1:
                    company_part = non_date_parts[0]
                else:
                    company_part = line_clean
            
            # Strategy 3: Just date and text
            else:
                date_match = re.search(r'(\d{4}\s*[–\-]\s*[A-Za-z\s]+)', line_clean)
                date_part = date_match.group(1) if date_match else ''
                rest = re.sub(r'\d{4}\s*[–\-]\s*', '', line_clean)
                if rest:
                    if '–' in rest or '-' in rest:
                        rest_parts = re.split(r'[–\-]', rest)
                        if len(rest_parts) >= 2:
                            title_part = rest_parts[0].strip()
                            company_part = rest_parts[1].strip()
                        else:
                            company_part = rest
                    else:
                        company_part = rest
            
            current_exp = {
                'company': company_part if company_part else line_clean,
                'title': title_part,
                'date': date_part,
                'bullets': []
            }
        
        elif current_exp and line and len(line) > 3:
            # Clean bullet points - remove ALL bullet symbols
            clean_line = line
            clean_line = re.sub(r'^[•●◆▪▸››►➢➣➤]\s*', '', clean_line)
            clean_line = re.sub(r'^[\u2022\u25CF\u25A0\u25AA\u25AB\u25E6\u2023\u2043]\s*', '', clean_line)
            clean_line = re.sub(r'^[•\-]\s*', '', clean_line)
            clean_line = re.sub(r'^•\s*', '', clean_line)
            clean_line = re.sub(r'^-\s*', '', clean_line)
            clean_line = re.sub(r'^\s*[•\-]\s*', '', clean_line)
            
            if clean_line and not any(x in clean_line.lower() for x in ['education', 'skill', 'qualification', 'reference', 'employment']):
                current_exp['bullets'].append(clean_line)
    
    if current_exp:
        exp_section.append(current_exp)
    info['experience'] = exp_section
    
    # ===== Skills =====
    skills_lines = sections.get('skills', [])
    skills_found = []
    
    for line in skills_lines:
        # Try splitting by commas, bullets, semicolons
        parts = re.split(r'[•●◆▪▸››►➢➣➤,;\n]', line)
        for part in parts:
            part = part.strip()
            if part and len(part) < 60 and len(part) > 2:
                # Remove leading bullet symbols
                part = re.sub(r'^[•●◆▪▸››►➢➣➤]\s*', '', part)
                part = re.sub(r'^[\u2022\u25CF\u25A0\u25AA\u25AB\u25E6\u2023\u2043]\s*', '', part)
                part = re.sub(r'^[•\-]\s*', '', part)
                part = re.sub(r'^•\s*', '', part)
                part = re.sub(r'^-\s*', '', part)
                part = re.sub(r'^\s*[•\-]\s*', '', part)
                part = re.sub(r'\s+', ' ', part)
                
                if part and not any(x in part.lower() for x in ['skills', 'abilities']):
                    skills_found.append(part)
    
    # If no skills found, try alternate method
    if not skills_found:
        in_skills = False
        for line in lines:
            if 'skill' in line.lower():
                in_skills = True
                continue
            if in_skills and line:
                if any(x in line.lower() for x in ['education', 'employment', 'experience', 'qualification', 'reference']):
                    break
                parts = re.split(r'[•●◆▪▸››►➢➣➤,;\n]', line)
                for part in parts:
                    part = part.strip()
                    if part and len(part) < 60 and len(part) > 2:
                        part = re.sub(r'^[•\-]\s*', '', part)
                        part = re.sub(r'^•\s*', '', part)
                        part = re.sub(r'^-\s*', '', part)
                        if part:
                            skills_found.append(part)
    
    info['skills'] = skills_found[:15]
    
    # ===== Achievements =====
    ach_lines = sections.get('achievements', [])
    achievements_found = []
    for line in ach_lines:
        clean_line = line
        clean_line = re.sub(r'^[•●◆▪▸››►➢➣➤]\s*', '', clean_line)
        clean_line = re.sub(r'^[\u2022\u25CF\u25A0\u25AA\u25AB\u25E6\u2023\u2043]\s*', '', clean_line)
        clean_line = re.sub(r'^[•\-]\s*', '', clean_line)
        clean_line = re.sub(r'^•\s*', '', clean_line)
        clean_line = re.sub(r'^-\s*', '', clean_line)
        clean_line = re.sub(r'^\s*[•\-]\s*', '', clean_line)
        if clean_line and len(clean_line) > 3:
            achievements_found.append(clean_line)
    info['achievements'] = achievements_found[:8]
    
    # ===== References =====
    ref_lines = sections.get('references', [])
    references = []
    current_ref = {}
    
    for line in ref_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        is_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line_clean)
        is_phone = re.search(r'\+254\s?\d{9}|0\d{9}|07\d{8}|01\d{8}', line_clean)
        
        # If it's a name (not email, not phone, and reasonable length)
        if not is_email and not is_phone and len(line_clean) > 5:
            if current_ref and current_ref.get('name'):
                references.append(current_ref)
            current_ref = {'name': line_clean, 'position': '', 'email': '', 'phone': ''}
        elif current_ref and current_ref.get('name'):
            if is_email:
                current_ref['email'] = is_email.group()
                line_clean = line_clean.replace(is_email.group(), '').strip()
                if line_clean and not current_ref['position']:
                    current_ref['position'] = line_clean
            elif is_phone:
                current_ref['phone'] = is_phone.group()
                line_clean = line_clean.replace(is_phone.group(), '').strip()
                if line_clean and not current_ref['position']:
                    current_ref['position'] = line_clean
            elif not current_ref['position'] and len(line_clean) > 3:
                current_ref['position'] = line_clean
    
    if current_ref and current_ref.get('name'):
        references.append(current_ref)
    
    info['references'] = references[:5]
    
    # ===== Extract Title =====
    if info['experience'] and len(info['experience']) > 0:
        first_exp = info['experience'][0]
        if first_exp.get('title'):
            info['title'] = first_exp['title']
    
    return info


# ===== Routes =====
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
        cv_data['raw_text'] = cv_text
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
        
        pdf_path = create_cv_from_dict(data, layout)
        filename = os.path.basename(pdf_path)
        # store pdf path under the session data
        extracted_data_store[session_id]['pdf_path'] = pdf_path
        
        return render_template('download.html', filename=filename, name=data.get('name', 'CV'))
    
    except Exception as e:
        return render_template('error.html', message=f'Error generating PDF: {str(e)}')


@app.route('/download/<filename>')
def download_cv(filename):
    try:
        # Try to find the generated path in stored sessions
        stored_path = None
        for val in extracted_data_store.values():
            if isinstance(val, dict) and val.get('pdf_path'):
                if os.path.basename(val.get('pdf_path')) == filename:
                    stored_path = val.get('pdf_path')
                    break

        if stored_path and os.path.exists(stored_path):
            return send_file(stored_path, as_attachment=True, download_name=filename)
        
        filepath = os.path.join('generated', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(temp_path):
            return send_file(temp_path, as_attachment=True, download_name=filename)
        
        return render_template('error.html', message='File not found. Please generate again.')
    
    except Exception as e:
        return render_template('error.html', message=f'Error: {str(e)}')


@app.route('/api/preview/<layout_id>')
def preview_layout(layout_id):
    return jsonify(SAMPLE_DATA)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
