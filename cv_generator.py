from fpdf import FPDF
import os
import textwrap
import uuid
import re
import tempfile
import shutil

def clean_text(text):
    """Clean text of special characters"""
    if not text:
        return ""
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '-', '\u2026': '...',
        '\u00a0': ' ', '\u00e9': 'e', '\u00e8': 'e', '\u00e0': 'a',
        '\u00f4': 'o', '\u00ee': 'i', '\u00e7': 'c', '\u00f1': 'n',
        '\u00fc': 'u', '\u00e4': 'a', '\u00f6': 'o', '\u00df': 'ss',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_cv_from_dict(data, layout='classic'):
    """Generate a professional CV PDF with selected layout"""
    
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = clean_text(value)
        elif isinstance(value, list):
            cleaned_data[key] = [clean_text(item) if isinstance(item, str) else item for item in value]
        else:
            cleaned_data[key] = value
    
    if layout == 'modern':
        return create_modern_cv(cleaned_data)
    elif layout == 'elegant':
        return create_elegant_cv(cleaned_data)
    elif layout == 'professional':
        return create_professional_cv(cleaned_data)
    else:
        return create_classic_cv(cleaned_data)


# ============================================
# LAYOUT 1: CLASSIC - Traditional Two-Column (WORKING)
# ============================================
def create_classic_cv(data):
    """Classic two-column layout with sidebar"""
    
    class ClassicCV(FPDF):
        def __init__(self):
            super().__init__(orientation='P', unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=15)
            self.set_margins(15, 15, 15)
            self.primary = (26, 35, 85)
            self.accent = (41, 128, 185)
            self.text_dark = (33, 33, 33)
            self.text_light = (117, 117, 117)
            self.sidebar_bg = (248, 249, 252)
            self.gold = (184, 134, 11)
            self.sidebar_width = 52
            self.main_x = 66
            self.main_width = 130
        
        def set_color(self, r, g, b):
            self.set_text_color(int(r), int(g), int(b))
        
        def set_fill(self, r, g, b):
            self.set_fill_color(int(r), int(g), int(b))
        
        def set_draw(self, r, g, b):
            self.set_draw_color(int(r), int(g), int(b))
        
        def add_sidebar(self, name, title, contact_info, skills, languages):
            page_height = 297
            sidebar_width = self.sidebar_width
            
            self.set_fill(self.sidebar_bg[0], self.sidebar_bg[1], self.sidebar_bg[2])
            self.rect(0, 0, sidebar_width, page_height, 'F')
            
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, 210, 5, 'F')
            self.rect(0, page_height - 5, 210, 5, 'F')
            
            name_clean = clean_text(name) if name else "CURRICULUM VITAE"
            self.set_xy(8, 18)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 10)
            self.multi_cell(sidebar_width - 16, 4.5, name_clean.upper(), 0, 'C')
            
            if title:
                self.set_xy(8, 35)
                self.set_color(self.accent[0], self.accent[1], self.accent[2])
                self.set_font("Helvetica", "B", 6.5)
                title_clean = clean_text(title)
                self.cell(sidebar_width - 16, 3, title_clean, 0, 1, 'C')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.line(18, 40, sidebar_width - 18, 40)
            
            y_pos = 50
            self.set_xy(10, y_pos)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 6.5)
            self.cell(sidebar_width - 20, 3, "CONTACT", 0, 1, 'L')
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.line(10, y_pos + 4, sidebar_width - 10, y_pos + 4)
            
            y_pos += 8
            
            if contact_info.get('email') and contact_info['email'] not in ['', 'Email not provided']:
                self.set_xy(12, y_pos)
                self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                self.set_font("Helvetica", "B", 5.5)
                self.cell(8, 2.5, "EMAIL:", 0, 0, 'L')
                self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                self.set_font("Helvetica", "", 5.5)
                self.set_xy(12, y_pos + 3)
                email_clean = clean_text(str(contact_info['email']))
                wrapped_email = textwrap.fill(email_clean, width=20)
                self.multi_cell(sidebar_width - 24, 2.5, wrapped_email, 0, 'L')
                y_pos += len(wrapped_email.split('\n')) * 2.5 + 4
            
            if skills:
                y_pos += 2
                if y_pos < 250:
                    self.set_xy(10, y_pos)
                    self.set_color(self.primary[0], self.primary[1], self.primary[2])
                    self.set_font("Helvetica", "B", 6.5)
                    self.cell(sidebar_width - 20, 3, "SKILLS", 0, 1, 'L')
                    self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                    self.line(10, y_pos + 4, sidebar_width - 10, y_pos + 4)
                    
                    y_pos += 8
                    for skill in skills[:12]:
                        if y_pos > 250:
                            break
                        self.set_xy(12, y_pos)
                        self.set_color(self.accent[0], self.accent[1], self.accent[2])
                        self.set_font("Helvetica", "", 5.5)
                        self.cell(3, 2.5, "-", 0, 0, 'L')
                        self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                        self.set_font("Helvetica", "", 5.5)
                        skill_clean = clean_text(skill)
                        wrapped_skill = textwrap.fill(skill_clean, width=18)
                        self.multi_cell(sidebar_width - 24, 2.5, wrapped_skill, 0, 'L')
                        y_pos += len(wrapped_skill.split('\n')) * 2.5 + 1
            
            languages = languages or ["English", "Swahili"]
            y_pos += 2
            if y_pos < 250:
                self.set_xy(10, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 6.5)
                self.cell(sidebar_width - 20, 3, "LANGUAGES", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.line(10, y_pos + 4, sidebar_width - 10, y_pos + 4)
                
                y_pos += 8
                for lang in languages[:3]:
                    if y_pos > 250:
                        break
                    self.set_xy(12, y_pos)
                    self.set_color(self.accent[0], self.accent[1], self.accent[2])
                    self.set_font("Helvetica", "", 5.5)
                    self.cell(3, 2.5, "-", 0, 0, 'L')
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 5.5)
                    lang_clean = clean_text(lang)
                    self.cell(sidebar_width - 24, 2.5, lang_clean, 0, 1, 'L')
                    y_pos += 3
            
            self.set_draw(self.primary[0], self.primary[1], self.primary[2])
            self.set_line_width(0.5)
            self.line(sidebar_width, 0, sidebar_width, page_height)
        
        def add_main_content(self, summary, experience, education, achievements, references):
            main_x = self.main_x
            main_width = self.main_width
            y_pos = 15
            
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.set_xy(main_x, y_pos)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 22)
            self.cell(main_width, 9, name_clean.upper(), 0, 1, 'L')
            y_pos += 9
            
            title = data.get('title', '')
            if title:
                self.set_xy(main_x, y_pos)
                self.set_color(self.accent[0], self.accent[1], self.accent[2])
                self.set_font("Helvetica", "B", 10)
                title_clean = clean_text(title)
                self.cell(main_width, 5, title_clean, 0, 1, 'L')
                y_pos += 6
            
            self.set_draw(self.gold[0], self.gold[1], self.gold[2])
            self.set_line_width(0.6)
            self.line(main_x, y_pos, main_x + 50, y_pos)
            y_pos += 10
            
            if summary:
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "PROFESSIONAL SUMMARY", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 40, y_pos + 5.5)
                y_pos += 8
                
                self.set_xy(main_x, y_pos)
                self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                self.set_font("Helvetica", "", 8.5)
                summary_clean = clean_text(summary)
                wrapped_summary = textwrap.fill(summary_clean, width=68)
                self.multi_cell(main_width, 4.5, wrapped_summary, 0, 'L')
                y_pos += len(wrapped_summary.split('\n')) * 4.5 + 8
            
            if education:
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "EDUCATION", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 28, y_pos + 5.5)
                y_pos += 8
                
                for edu in education[:5]:
                    if y_pos > 260:
                        self.add_page()
                        y_pos = 15
                    self.set_xy(main_x, y_pos)
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 8.5)
                    edu_clean = clean_text(edu)
                    self.cell(main_width, 4.5, edu_clean, 0, 1, 'L')
                    y_pos += 5
                y_pos += 3
            
            if experience:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 15
                
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "EMPLOYMENT", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 32, y_pos + 5.5)
                y_pos += 8
                
                for idx, exp in enumerate(experience[:5]):
                    if y_pos > 245:
                        self.add_page()
                        y_pos = 15
                    
                    company = clean_text(exp.get('company', ''))
                    if company:
                        self.set_xy(main_x, y_pos)
                        self.set_color(self.primary[0], self.primary[1], self.primary[2])
                        self.set_font("Helvetica", "B", 8.5)
                        self.cell(main_width, 4.5, company, 0, 1, 'L')
                        y_pos += 4.5
                    
                    title_text = clean_text(exp.get('title', ''))
                    date_text = clean_text(exp.get('date', ''))
                    
                    if title_text or date_text:
                        self.set_xy(main_x, y_pos)
                        if title_text:
                            self.set_color(self.accent[0], self.accent[1], self.accent[2])
                            self.set_font("Helvetica", "B", 8)
                            self.cell(main_width * 0.55, 4, title_text, 0, 0, 'L')
                        if date_text:
                            if title_text:
                                self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                                self.set_font("Helvetica", "I", 7)
                                self.cell(main_width * 0.45, 4, date_text, 0, 1, 'R')
                            else:
                                self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                                self.set_font("Helvetica", "I", 7)
                                self.cell(main_width, 4, date_text, 0, 1, 'R')
                        else:
                            self.cell(0, 4, '', 0, 1)
                        y_pos += 4
                    
                    if exp.get('bullets'):
                        for bullet in exp['bullets'][:3]:
                            if y_pos > 260:
                                self.add_page()
                                y_pos = 15
                            bullet_clean = clean_text(bullet)
                            bullet_clean = re.sub(r'^[•\-]\s*', '', bullet_clean)
                            self.set_xy(main_x + 4, y_pos)
                            self.set_color(self.accent[0], self.accent[1], self.accent[2])
                            self.set_font("Helvetica", "", 6.5)
                            self.cell(3, 3, "-", 0, 0, 'L')
                            self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                            self.set_font("Helvetica", "", 7)
                            wrapped_bullet = textwrap.fill(bullet_clean, width=58)
                            self.multi_cell(main_width - 12, 3, wrapped_bullet, 0, 'L')
                            y_pos += len(wrapped_bullet.split('\n')) * 3 + 1
                    
                    if idx < len(experience[:5]) - 1:
                        y_pos += 2
                y_pos += 3
            
            if achievements:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 15
                
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "ADDITIONAL QUALIFICATIONS", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 48, y_pos + 5.5)
                y_pos += 8
                
                for ach in achievements[:8]:
                    if y_pos > 260:
                        self.add_page()
                        y_pos = 15
                    ach_clean = clean_text(ach)
                    self.set_xy(main_x + 4, y_pos)
                    self.set_color(self.gold[0], self.gold[1], self.gold[2])
                    self.set_font("Helvetica", "", 6.5)
                    self.cell(3, 3, "+", 0, 0, 'L')
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 7)
                    wrapped_ach = textwrap.fill(ach_clean, width=58)
                    self.multi_cell(main_width - 12, 3, wrapped_ach, 0, 'L')
                    y_pos += len(wrapped_ach.split('\n')) * 3 + 1
                y_pos += 3
            
            if references:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 15
                
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "REFERENCES", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 32, y_pos + 5.5)
                y_pos += 8
                
                for ref in references[:4]:
                    if y_pos > 260:
                        self.add_page()
                        y_pos = 15
                    
                    ref_name = clean_text(ref.get('name', ''))
                    if ref_name:
                        self.set_xy(main_x, y_pos)
                        self.set_color(self.primary[0], self.primary[1], self.primary[2])
                        self.set_font("Helvetica", "B", 8.5)
                        self.cell(main_width, 4, ref_name, 0, 1, 'L')
                        y_pos += 4
                    
                    ref_pos = clean_text(ref.get('position', ''))
                    if ref_pos:
                        self.set_xy(main_x, y_pos)
                        self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                        self.set_font("Helvetica", "", 7.5)
                        self.cell(main_width, 3.5, ref_pos, 0, 1, 'L')
                        y_pos += 3.5
                    
                    ref_email = clean_text(ref.get('email', ''))
                    if ref_email:
                        self.set_xy(main_x, y_pos)
                        self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                        self.set_font("Helvetica", "", 7)
                        self.cell(main_width, 3, ref_email, 0, 1, 'L')
                        y_pos += 3
                    
                    ref_phone = clean_text(ref.get('phone', ''))
                    if ref_phone:
                        self.set_xy(main_x, y_pos)
                        self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                        self.set_font("Helvetica", "", 7)
                        self.cell(main_width, 3, ref_phone, 0, 1, 'L')
                        y_pos += 4
                    
                    if ref != references[-1]:
                        self.set_draw(self.sidebar_bg[0], self.sidebar_bg[1], self.sidebar_bg[2])
                        self.set_line_width(0.3)
                        self.line(main_x, y_pos, main_x + main_width, y_pos)
                        y_pos += 3
        
        def add_page(self):
            super().add_page()
            page_height = 297
            sidebar_width = self.sidebar_width
            
            self.set_fill(self.sidebar_bg[0], self.sidebar_bg[1], self.sidebar_bg[2])
            self.rect(0, 0, sidebar_width, page_height, 'F')
            
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, 210, 5, 'F')
            self.rect(0, page_height - 5, 210, 5, 'F')
            
            self.set_draw(self.primary[0], self.primary[1], self.primary[2])
            self.set_line_width(0.5)
            self.line(sidebar_width, 0, sidebar_width, page_height)
            
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.set_xy(8, 18)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 9)
            self.multi_cell(sidebar_width - 16, 4, name_clean, 0, 'C')
            
            title = data.get('title', 'Professional CV')
            if title:
                self.set_xy(8, 33)
                self.set_color(self.accent[0], self.accent[1], self.accent[2])
                self.set_font("Helvetica", "B", 6)
                title_clean = clean_text(title)
                self.cell(sidebar_width - 16, 2.5, title_clean, 0, 1, 'C')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.line(18, 38, sidebar_width - 18, 38)
            
            self.set_xy(8, page_height - 18)
            self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
            self.set_font("Helvetica", "I", 5.5)
            self.cell(sidebar_width - 16, 2.5, f"Page {self.page_no()}", 0, 1, 'C')
    
    pdf = ClassicCV()
    pdf.add_page()
    
    name = data.get('name', 'CURRICULUM VITAE')
    title = data.get('title', '')
    
    contact_info = {}
    if data.get('email'):
        contact_info['email'] = clean_text(data['email'])
    if data.get('phone'):
        contact_info['phone'] = clean_text(data['phone'])
    
    skills = data.get('skills', [])
    if not skills:
        skills = ['No skills extracted']
    
    languages = ['English', 'Swahili']
    
    pdf.add_sidebar(name, title, contact_info, skills, languages)
    
    pdf.add_main_content(
        data.get('summary', ''),
        data.get('experience', []),
        data.get('education', []),
        data.get('achievements', []),
        data.get('references', [])
    )
    
    safe_name = re.sub(r'[^\x00-\x7F]+', '', name.replace(' ', '_')[:20]) if name else 'cv'
    filename = f"{safe_name}_classic_{uuid.uuid4().hex[:8]}.pdf"
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    pdf.output(temp_path)
    
    try:
        if not os.path.exists('generated'):
            os.makedirs('generated')
        shutil.copy2(temp_path, os.path.join('generated', filename))
    except:
        pass
    
    return temp_path


# ============================================
# LAYOUT 2: MODERN - Top Header with Timeline (FIXED)
# ============================================
def create_modern_cv(data):
    """Modern layout with header at top and timeline experience"""
    
    class ModernCV(FPDF):
        def __init__(self):
            super().__init__(orientation='P', unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=15)
            self.set_margins(15, 15, 15)
            self.primary = (44, 62, 80)
            self.accent = (231, 76, 60)
            self.text_dark = (44, 62, 80)
            self.text_light = (127, 140, 141)
            self.white = (255, 255, 255)
            self.gold = (241, 196, 15)
            self.main_x = 15
            self.main_width = 180
        
        def set_color(self, r, g, b):
            self.set_text_color(int(r), int(g), int(b))
        
        def set_fill(self, r, g, b):
            self.set_fill_color(int(r), int(g), int(b))
        
        def set_draw(self, r, g, b):
            self.set_draw_color(int(r), int(g), int(b))
        
        def add_header(self, name, title, contact_info):
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, 210, 45, 'F')
            
            self.set_xy(15, 10)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 24)
            name_clean = clean_text(name) if name else "CURRICULUM VITAE"
            self.cell(180, 10, name_clean.upper(), 0, 1, 'L')
            
            if title:
                self.set_xy(15, 22)
                self.set_color(self.accent[0], self.accent[1], self.accent[2])
                self.set_font("Helvetica", "B", 12)
                title_clean = clean_text(title)
                self.cell(180, 6, title_clean, 0, 1, 'L')
            
            self.set_xy(15, 32)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "", 8)
            contact_text = ""
            if contact_info.get('email'):
                contact_text += f"Email: {contact_info['email']}  "
            if contact_info.get('phone'):
                contact_text += f"Phone: {contact_info['phone']}"
            self.cell(180, 5, contact_text, 0, 1, 'L')
            
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(2)
            self.line(15, 40, 195, 40)
            
            return 48
        
        def add_section_title(self, title, y_pos):
            self.set_xy(self.main_x, y_pos)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 12)
            self.cell(self.main_width, 6, title.upper(), 0, 1, 'L')
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(0.5)
            self.line(self.main_x, y_pos + 7, self.main_x + 40, y_pos + 7)
            return y_pos + 10
        
        def add_main_content(self, summary, experience, education, achievements, references):
            y_pos = 48
            
            if summary:
                y_pos = self.add_section_title("PROFESSIONAL SUMMARY", y_pos)
                self.set_xy(self.main_x, y_pos)
                self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                self.set_font("Helvetica", "", 9)
                summary_clean = clean_text(summary)
                wrapped_summary = textwrap.fill(summary_clean, width=90)
                self.multi_cell(self.main_width, 4.5, wrapped_summary, 0, 'L')
                y_pos += len(wrapped_summary.split('\n')) * 4.5 + 8
            
            if experience:
                y_pos = self.add_section_title("WORK EXPERIENCE", y_pos)
                for exp in experience[:4]:
                    if y_pos > 260:
                        self.add_page()
                        y_pos = 48
                    
                    company = clean_text(exp.get('company', ''))
                    title_text = clean_text(exp.get('title', ''))
                    date_text = clean_text(exp.get('date', ''))
                    
                    self.set_xy(self.main_x, y_pos)
                    self.set_color(self.primary[0], self.primary[1], self.primary[2])
                    self.set_font("Helvetica", "B", 10)
                    self.cell(self.main_width * 0.6, 5, company, 0, 0, 'L')
                    self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                    self.set_font("Helvetica", "I", 9)
                    self.cell(self.main_width * 0.4, 5, date_text, 0, 1, 'R')
                    y_pos += 5
                    
                    if title_text:
                        self.set_xy(self.main_x, y_pos)
                        self.set_color(self.accent[0], self.accent[1], self.accent[2])
                        self.set_font("Helvetica", "B", 9)
                        self.cell(self.main_width, 4.5, title_text, 0, 1, 'L')
                        y_pos += 4.5
                    
                    if exp.get('bullets'):
                        for bullet in exp['bullets'][:3]:
                            if y_pos > 260:
                                self.add_page()
                                y_pos = 48
                            bullet_clean = clean_text(bullet)
                            bullet_clean = re.sub(r'^[•\-]\s*', '', bullet_clean)
                            self.set_xy(self.main_x + 4, y_pos)
                            self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                            self.set_font("Helvetica", "", 8)
                            self.cell(3, 4, "▶", 0, 0, 'L')
                            wrapped_bullet = textwrap.fill(bullet_clean, width=80)
                            self.multi_cell(self.main_width - 10, 4, wrapped_bullet, 0, 'L')
                            y_pos += len(wrapped_bullet.split('\n')) * 4 + 1
                    y_pos += 3
            
            if education:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 48
                y_pos = self.add_section_title("EDUCATION", y_pos)
                for edu in education[:4]:
                    self.set_xy(self.main_x, y_pos)
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 9)
                    edu_clean = clean_text(edu)
                    self.cell(self.main_width, 4.5, edu_clean, 0, 1, 'L')
                    y_pos += 5
        
        def add_page(self):
            super().add_page()
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, 210, 45, 'F')
            
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.set_xy(15, 10)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 18)
            self.cell(180, 8, name_clean.upper(), 0, 1, 'L')
            self.set_xy(15, 22)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "", 8)
            self.cell(180, 4, f"Page {self.page_no()}", 0, 1, 'R')
            
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(2)
            self.line(15, 40, 195, 40)
    
    pdf = ModernCV()
    pdf.add_page()
    
    name = data.get('name', 'CURRICULUM VITAE')
    title = data.get('title', '')
    
    contact_info = {}
    if data.get('email'):
        contact_info['email'] = clean_text(data['email'])
    if data.get('phone'):
        contact_info['phone'] = clean_text(data['phone'])
    
    pdf.add_header(name, title, contact_info)
    
    pdf.add_main_content(
        data.get('summary', ''),
        data.get('experience', []),
        data.get('education', []),
        data.get('achievements', []),
        data.get('references', [])
    )
    
    safe_name = re.sub(r'[^\x00-\x7F]+', '', name.replace(' ', '_')[:20]) if name else 'cv'
    filename = f"{safe_name}_modern_{uuid.uuid4().hex[:8]}.pdf"
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    pdf.output(temp_path)
    
    try:
        if not os.path.exists('generated'):
            os.makedirs('generated')
        shutil.copy2(temp_path, os.path.join('generated', filename))
    except:
        pass
    
    return temp_path


# ============================================
# LAYOUT 3: ELEGANT - Centered with Gold Accents (FIXED)
# ============================================
def create_elegant_cv(data):
    """Elegant layout with centered name, gold accents, minimalist"""
    
    class ElegantCV(FPDF):
        def __init__(self):
            super().__init__(orientation='P', unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=15)
            self.set_margins(15, 15, 15)
            self.primary = (60, 30, 50)
            self.accent = (200, 160, 120)
            self.text_dark = (40, 30, 35)
            self.text_light = (140, 120, 130)
            self.white = (255, 255, 255)
            self.gold = (180, 140, 100)
            self.main_x = 25
            self.main_width = 160
        
        def set_color(self, r, g, b):
            self.set_text_color(int(r), int(g), int(b))
        
        def set_fill(self, r, g, b):
            self.set_fill_color(int(r), int(g), int(b))
        
        def set_draw(self, r, g, b):
            self.set_draw_color(int(r), int(g), int(b))
        
        def add_header(self, name, title, contact_info):
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(1.5)
            self.line(25, 8, 185, 8)
            
            self.set_xy(0, 15)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 28)
            name_clean = clean_text(name) if name else "CURRICULUM VITAE"
            self.cell(210, 10, name_clean.upper(), 0, 1, 'C')
            
            if title:
                self.set_xy(0, 28)
                self.set_color(self.accent[0], self.accent[1], self.accent[2])
                self.set_font("Helvetica", "B", 12)
                title_clean = clean_text(title)
                self.cell(210, 6, title_clean, 0, 1, 'C')
            
            contact_text = ""
            if contact_info.get('email'):
                contact_text += f"Email: {contact_info['email']}  "
            if contact_info.get('phone'):
                contact_text += f"Phone: {contact_info['phone']}"
            self.set_xy(0, 36)
            self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
            self.set_font("Helvetica", "", 8)
            self.cell(210, 5, contact_text, 0, 1, 'C')
            
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(1)
            self.line(55, 44, 155, 44)
            
            return 50
        
        def add_section_title(self, title, y_pos):
            self.set_xy(self.main_x, y_pos)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 11)
            self.cell(self.main_width, 5, title.upper(), 0, 1, 'L')
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(0.3)
            self.line(self.main_x, y_pos + 6, self.main_x + 30, y_pos + 6)
            return y_pos + 9
        
        def add_main_content(self, summary, experience, education, achievements, references):
            y_pos = 50
            
            if summary:
                y_pos = self.add_section_title("PROFILE", y_pos)
                self.set_xy(self.main_x, y_pos)
                self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                self.set_font("Helvetica", "", 9)
                summary_clean = clean_text(summary)
                wrapped_summary = textwrap.fill(summary_clean, width=80)
                self.multi_cell(self.main_width, 4.5, wrapped_summary, 0, 'L')
                y_pos += len(wrapped_summary.split('\n')) * 4.5 + 8
            
            if experience:
                y_pos = self.add_section_title("WORK EXPERIENCE", y_pos)
                for exp in experience[:4]:
                    if y_pos > 260:
                        self.add_page()
                        y_pos = 50
                    
                    company = clean_text(exp.get('company', ''))
                    title_text = clean_text(exp.get('title', ''))
                    date_text = clean_text(exp.get('date', ''))
                    
                    self.set_xy(self.main_x, y_pos)
                    self.set_color(self.primary[0], self.primary[1], self.primary[2])
                    self.set_font("Helvetica", "B", 10)
                    self.cell(self.main_width, 5, company, 0, 1, 'L')
                    y_pos += 5
                    
                    if title_text or date_text:
                        self.set_xy(self.main_x, y_pos)
                        if title_text:
                            self.set_color(self.accent[0], self.accent[1], self.accent[2])
                            self.set_font("Helvetica", "B", 9)
                            self.cell(self.main_width * 0.6, 4.5, title_text, 0, 0, 'L')
                        if date_text:
                            self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                            self.set_font("Helvetica", "I", 8)
                            self.cell(self.main_width * 0.4, 4.5, date_text, 0, 1, 'R')
                        y_pos += 4.5
                    
                    if exp.get('bullets'):
                        for bullet in exp['bullets'][:3]:
                            if y_pos > 260:
                                self.add_page()
                                y_pos = 50
                            bullet_clean = clean_text(bullet)
                            bullet_clean = re.sub(r'^[•\-]\s*', '', bullet_clean)
                            self.set_xy(self.main_x + 5, y_pos)
                            self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                            self.set_font("Helvetica", "", 8)
                            self.cell(3, 4, "•", 0, 0, 'L')
                            wrapped_bullet = textwrap.fill(bullet_clean, width=75)
                            self.multi_cell(self.main_width - 10, 4, wrapped_bullet, 0, 'L')
                            y_pos += len(wrapped_bullet.split('\n')) * 4 + 1
                    y_pos += 3
            
            if education:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 50
                y_pos = self.add_section_title("EDUCATION", y_pos)
                for edu in education[:4]:
                    self.set_xy(self.main_x, y_pos)
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 9)
                    edu_clean = clean_text(edu)
                    self.cell(self.main_width, 4.5, edu_clean, 0, 1, 'L')
                    y_pos += 5
        
        def add_page(self):
            super().add_page()
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(1.5)
            self.line(25, 8, 185, 8)
            
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.set_xy(0, 15)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 18)
            self.cell(210, 8, name_clean.upper(), 0, 1, 'C')
            self.set_xy(0, 27)
            self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
            self.set_font("Helvetica", "I", 8)
            self.cell(210, 4, f"Page {self.page_no()}", 0, 1, 'C')
            self.set_draw(self.accent[0], self.accent[1], self.accent[2])
            self.set_line_width(1)
            self.line(55, 34, 155, 34)
    
    pdf = ElegantCV()
    pdf.add_page()
    
    name = data.get('name', 'CURRICULUM VITAE')
    title = data.get('title', '')
    
    contact_info = {}
    if data.get('email'):
        contact_info['email'] = clean_text(data['email'])
    if data.get('phone'):
        contact_info['phone'] = clean_text(data['phone'])
    
    pdf.add_header(name, title, contact_info)
    
    pdf.add_main_content(
        data.get('summary', ''),
        data.get('experience', []),
        data.get('education', []),
        data.get('achievements', []),
        data.get('references', [])
    )
    
    safe_name = re.sub(r'[^\x00-\x7F]+', '', name.replace(' ', '_')[:20]) if name else 'cv'
    filename = f"{safe_name}_elegant_{uuid.uuid4().hex[:8]}.pdf"
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    pdf.output(temp_path)
    
    try:
        if not os.path.exists('generated'):
            os.makedirs('generated')
        shutil.copy2(temp_path, os.path.join('generated', filename))
    except:
        pass
    
    return temp_path


# ============================================
# LAYOUT 4: PROFESSIONAL - Clean Corporate (FIXED)
# ============================================
def create_professional_cv(data):
    """Professional corporate layout with clean sections"""
    
    class ProfessionalCV(FPDF):
        def __init__(self):
            super().__init__(orientation='P', unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=15)
            self.set_margins(15, 15, 15)
            self.primary = (0, 80, 60)
            self.accent = (0, 150, 136)
            self.text_dark = (30, 50, 40)
            self.text_light = (100, 130, 120)
            self.white = (255, 255, 255)
            self.gold = (255, 193, 7)
            self.sidebar_width = 45
        
        def set_color(self, r, g, b):
            self.set_text_color(int(r), int(g), int(b))
        
        def set_fill(self, r, g, b):
            self.set_fill_color(int(r), int(g), int(b))
        
        def set_draw(self, r, g, b):
            self.set_draw_color(int(r), int(g), int(b))
        
        def add_sidebar(self, name, contact_info, skills, languages):
            page_height = 297
            sidebar_width = self.sidebar_width
            
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, sidebar_width + 5, page_height, 'F')
            
            self.set_xy(5, 15)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 12)
            name_clean = clean_text(name) if name else "CV"
            self.multi_cell(sidebar_width, 5, name_clean.upper(), 0, 'L')
            
            self.set_xy(5, 35)
            self.set_color(self.gold[0], self.gold[1], self.gold[2])
            self.set_font("Helvetica", "B", 7)
            title = data.get('title', 'Professional')
            title_clean = clean_text(title)
            self.cell(sidebar_width, 4, title_clean, 0, 1, 'L')
            
            self.set_draw(self.gold[0], self.gold[1], self.gold[2])
            self.set_line_width(0.3)
            self.line(5, 42, sidebar_width, 42)
            
            y_pos = 50
            self.set_xy(5, y_pos)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 7)
            self.cell(sidebar_width, 4, "CONTACT", 0, 1, 'L')
            y_pos += 6
            
            if contact_info.get('email'):
                self.set_xy(5, y_pos)
                self.set_color(self.white[0], self.white[1], self.white[2])
                self.set_font("Helvetica", "", 6)
                email_clean = clean_text(str(contact_info['email']))
                wrapped_email = textwrap.fill(email_clean, width=15)
                self.multi_cell(sidebar_width, 3, wrapped_email, 0, 'L')
                y_pos += len(wrapped_email.split('\n')) * 3 + 3
            
            if contact_info.get('phone'):
                self.set_xy(5, y_pos)
                self.set_color(self.white[0], self.white[1], self.white[2])
                self.set_font("Helvetica", "", 6)
                phone_clean = clean_text(str(contact_info['phone']))
                self.cell(sidebar_width, 3, phone_clean, 0, 1, 'L')
                y_pos += 5
            
            if skills:
                y_pos += 2
                self.set_xy(5, y_pos)
                self.set_color(self.white[0], self.white[1], self.white[2])
                self.set_font("Helvetica", "B", 7)
                self.cell(sidebar_width, 4, "SKILLS", 0, 1, 'L')
                y_pos += 6
                for skill in skills[:10]:
                    self.set_xy(5, y_pos)
                    self.set_color(self.white[0], self.white[1], self.white[2])
                    self.set_font("Helvetica", "", 6)
                    skill_clean = clean_text(skill)
                    self.cell(sidebar_width, 3, f"- {skill_clean}", 0, 1, 'L')
                    y_pos += 3
            
            languages = languages or ["English", "Swahili"]
            y_pos += 2
            self.set_xy(5, y_pos)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 7)
            self.cell(sidebar_width, 4, "LANGUAGES", 0, 1, 'L')
            y_pos += 6
            for lang in languages[:3]:
                self.set_xy(5, y_pos)
                self.set_color(self.white[0], self.white[1], self.white[2])
                self.set_font("Helvetica", "", 6)
                lang_clean = clean_text(lang)
                self.cell(sidebar_width, 3, f"- {lang_clean}", 0, 1, 'L')
                y_pos += 3
        
        def add_main_content(self, summary, experience, education, achievements):
            main_x = self.sidebar_width + 15
            main_width = 210 - main_x - 15
            y_pos = 15
            
            self.set_xy(main_x, y_pos)
            self.set_color(self.primary[0], self.primary[1], self.primary[2])
            self.set_font("Helvetica", "B", 18)
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.cell(main_width, 8, name_clean.upper(), 0, 1, 'L')
            y_pos += 10
            
            if summary:
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "SUMMARY", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 30, y_pos + 5.5)
                y_pos += 8
                
                self.set_xy(main_x, y_pos)
                self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                self.set_font("Helvetica", "", 8.5)
                summary_clean = clean_text(summary)
                wrapped_summary = textwrap.fill(summary_clean, width=75)
                self.multi_cell(main_width, 4.5, wrapped_summary, 0, 'L')
                y_pos += len(wrapped_summary.split('\n')) * 4.5 + 8
            
            if experience:
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "EXPERIENCE", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 32, y_pos + 5.5)
                y_pos += 8
                
                for exp in experience[:4]:
                    if y_pos > 245:
                        self.add_page()
                        y_pos = 15
                    
                    company = clean_text(exp.get('company', ''))
                    title_text = clean_text(exp.get('title', ''))
                    date_text = clean_text(exp.get('date', ''))
                    
                    self.set_xy(main_x, y_pos)
                    self.set_color(self.primary[0], self.primary[1], self.primary[2])
                    self.set_font("Helvetica", "B", 9)
                    self.cell(main_width, 4.5, company, 0, 1, 'L')
                    y_pos += 4.5
                    
                    if title_text or date_text:
                        self.set_xy(main_x, y_pos)
                        if title_text:
                            self.set_color(self.accent[0], self.accent[1], self.accent[2])
                            self.set_font("Helvetica", "B", 8)
                            self.cell(main_width * 0.5, 4, title_text, 0, 0, 'L')
                        if date_text:
                            self.set_color(self.text_light[0], self.text_light[1], self.text_light[2])
                            self.set_font("Helvetica", "I", 7.5)
                            self.cell(main_width * 0.5, 4, date_text, 0, 1, 'R')
                        y_pos += 4
                    
                    if exp.get('bullets'):
                        for bullet in exp['bullets'][:3]:
                            if y_pos > 260:
                                self.add_page()
                                y_pos = 15
                            bullet_clean = clean_text(bullet)
                            bullet_clean = re.sub(r'^[•\-]\s*', '', bullet_clean)
                            self.set_xy(main_x + 4, y_pos)
                            self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                            self.set_font("Helvetica", "", 7.5)
                            self.cell(3, 3.5, "›", 0, 0, 'L')
                            wrapped_bullet = textwrap.fill(bullet_clean, width=70)
                            self.multi_cell(main_width - 10, 3.5, wrapped_bullet, 0, 'L')
                            y_pos += len(wrapped_bullet.split('\n')) * 3.5 + 1
                    y_pos += 3
            
            if education:
                if y_pos > 240:
                    self.add_page()
                    y_pos = 15
                self.set_xy(main_x, y_pos)
                self.set_color(self.primary[0], self.primary[1], self.primary[2])
                self.set_font("Helvetica", "B", 9)
                self.cell(main_width, 4.5, "EDUCATION", 0, 1, 'L')
                self.set_draw(self.accent[0], self.accent[1], self.accent[2])
                self.set_line_width(0.3)
                self.line(main_x, y_pos + 5.5, main_x + 28, y_pos + 5.5)
                y_pos += 8
                
                for edu in education[:4]:
                    self.set_xy(main_x, y_pos)
                    self.set_color(self.text_dark[0], self.text_dark[1], self.text_dark[2])
                    self.set_font("Helvetica", "", 8.5)
                    edu_clean = clean_text(edu)
                    self.cell(main_width, 4.5, edu_clean, 0, 1, 'L')
                    y_pos += 5
        
        def add_page(self):
            super().add_page()
            page_height = 297
            sidebar_width = self.sidebar_width
            
            self.set_fill(self.primary[0], self.primary[1], self.primary[2])
            self.rect(0, 0, sidebar_width + 5, page_height, 'F')
            
            name = data.get('name', 'CURRICULUM VITAE')
            name_clean = clean_text(name)
            self.set_xy(5, 15)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "B", 10)
            self.multi_cell(sidebar_width, 4, name_clean.upper(), 0, 'L')
            self.set_xy(5, 30)
            self.set_color(self.white[0], self.white[1], self.white[2])
            self.set_font("Helvetica", "", 6)
            self.cell(sidebar_width, 3, f"Page {self.page_no()}", 0, 1, 'L')
    
    pdf = ProfessionalCV()
    pdf.add_page()
    
    name = data.get('name', 'CURRICULUM VITAE')
    
    contact_info = {}
    if data.get('email'):
        contact_info['email'] = clean_text(data['email'])
    if data.get('phone'):
        contact_info['phone'] = clean_text(data['phone'])
    
    skills = data.get('skills', [])
    if not skills:
        skills = ['No skills extracted']
    
    languages = ['English', 'Swahili']
    
    pdf.add_sidebar(name, contact_info, skills, languages)
    
    pdf.add_main_content(
        data.get('summary', ''),
        data.get('experience', []),
        data.get('education', []),
        data.get('achievements', [])
    )
    
    safe_name = re.sub(r'[^\x00-\x7F]+', '', name.replace(' ', '_')[:20]) if name else 'cv'
    filename = f"{safe_name}_professional_{uuid.uuid4().hex[:8]}.pdf"
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    pdf.output(temp_path)
    
    try:
        if not os.path.exists('generated'):
            os.makedirs('generated')
        shutil.copy2(temp_path, os.path.join('generated', filename))
    except:
        pass
    
    return temp_path
