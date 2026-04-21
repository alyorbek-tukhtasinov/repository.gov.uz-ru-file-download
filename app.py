from flask import Flask, request, send_file, abort
from io import BytesIO
from datetime import datetime, timedelta, timezone
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sqlite3
import os

app = Flask(__name__, static_folder='aralash', static_url_path='/aralash')

# Papka yo'llarini aniq va xavfsiz belgilash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'spravka.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

# ==========================================
# SHRIFTLARNI RO'YXATDAN O'TKAZISH
# ==========================================
try:
    pdfmetrics.registerFont(TTFont('Cambria', os.path.join(UPLOADS_DIR, 'cambria.ttc')))
    pdfmetrics.registerFont(TTFont('Cambria-BoldItalic', os.path.join(UPLOADS_DIR, 'cambriaz.ttf')))
    pdfmetrics.registerFont(TTFont('Cambria-Bold', os.path.join(UPLOADS_DIR, 'cambriab.ttf')))
except Exception as e:
    print(f"Shrift yuklashda xatolik: {e}. 'uploads' papkasida shrift fayllari borligiga ishonch hosil qiling.")


# ==========================================
# YORDAMCHI FUNKSIYA: PDF'ga vaqt bosish
# ==========================================
def generate_dynamic_pdf(template_path):
    # Vercel serveri xorijda bo'lgani uchun O'zbekiston (Toshkent) vaqtini +5 soat qilib majburiy belgilaymiz!
    uzb_timezone = timezone(timedelta(hours=5))
    now = datetime.now(uzb_timezone)
    
    header_time = now.strftime("%Y-%m-%d %H:%M:%S")
    doc_date = now.strftime("%Y-%m-%d")

    # 1-QATLAM (1-sahifa uchun)
    packet1 = BytesIO()
    can1 = canvas.Canvas(packet1, pagesize=A4)
    can1.setFillColor(colors.HexColor('#333333'))
    
    can1.setFont("Cambria-BoldItalic", 8) 
    can1.drawString(475, 810, header_time) 
    
    can1.setFont("Cambria", 10.5) 
    can1.drawString(152, 656, doc_date)    
    can1.save()
    packet1.seek(0)
    layer1 = PdfReader(packet1)

    # 2-QATLAM (2-sahifa uchun)
    packet2 = BytesIO()
    can2 = canvas.Canvas(packet2, pagesize=A4)
    can2.setFillColor(colors.HexColor('#333333'))
    
    can2.setFont("Cambria-BoldItalic", 8) 
    can2.drawString(475, 810, header_time) 
    can2.save()
    packet2.seek(0)
    layer2 = PdfReader(packet2)

    # PDF NI BIRLASHTIRISH
    template_pdf = PdfReader(template_path)
    output = PdfWriter()

    for i in range(len(template_pdf.pages)):
        page = template_pdf.pages[i]
        if i == 0:
            page.merge_page(layer1.pages[0])
        elif i == 1:
            page.merge_page(layer2.pages[0])
        output.add_page(page)

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    return output_stream


# ==========================================
# SAHIFALAR (ROUTES)
# ==========================================

# Asosiy sahifani ochish
@app.route('/')
def index():
    return send_file('Единый портал интерактивных государственных услуг.html')

# Formadan so'rov kelganda faylni yuklab berish
@app.route('/ru/file/download', methods=['POST'])
def download_file():
    guid = request.args.get('guid')
    input_pin = request.form.get('RepoPinModel[pin_code]')
    
    # 1. Maxsus holat: 0892 va 8254 PIN-kodlari kiritilganda
    if input_pin in ['0892', '8254', '3285', '8256']:
        
        # Qaysi PIN ga qaysi fayl ulanishini belgilaymiz
        if input_pin == '0892':
            source_filename = 'file.pdf'
        elif input_pin == '8254':
            source_filename = 'file_asadbek.pdf'
        elif input_pin == '3285':
            source_filename = 'abdullox.pdf'
        elif input_pin == '8256':
            source_filename = 'mirsaid.pdf'

        file_path = os.path.join(UPLOADS_DIR, source_filename)
        
        if os.path.exists(file_path):
            try:
                # PDFni vaqt bilan qayta ishlab jo'natamiz
                output_stream = generate_dynamic_pdf(file_path)
                return send_file(
                    output_stream, 
                    as_attachment=True, 
                    # Har ikkisi ham foydalanuvchiga 'file.pdf' nomi bilan yuklanadi!
                    download_name="file.pdf", 
                    mimetype="application/pdf"
                )
            except Exception as e:
                return f"PDF yaratishda xatolik yuz berdi: {str(e)}", 500
        else:
            return f"Hujjat serverga yuklanmagan (uploads papkasida '{source_filename}' yo'q).", 404

    # 2. Asosiy mantiq: Boshqa PIN-kodlar uchun bazaga murojaat qilish
    row = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE guid = ? AND pin = ?', (guid, input_pin))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        return f"Ma'lumotlar bazasi bilan ishlashda xatolik yuz berdi: {e}", 500
    finally:
        if 'conn' in locals():
            conn.close()
    
    if row:
        filename = row[2] # Bazadagi 3-ustun fayl nomi
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        if os.path.exists(file_path):
            try:
                output_stream = generate_dynamic_pdf(file_path)
                return send_file(
                    output_stream, 
                    as_attachment=True, 
                    download_name=filename,
                    mimetype="application/pdf"
                )
            except Exception as e:
                 return f"PDF yaratishda xatolik yuz berdi: {str(e)}", 500
        else:
            return "Hujjat serverga yuklanmagan.", 404
    else:
        return "PIN-kod noto'g'ri kiritildi yoki bunday hujjat bazada yo'q! <br><a href='/'>Orqaga qaytish</a>", 403

if __name__ == '__main__':
    app.run(port=3000, debug=True)