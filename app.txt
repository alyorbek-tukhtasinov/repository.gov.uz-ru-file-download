from flask import Flask, request, send_file, abort
import sqlite3
import os

# aralash papkasini dizaynlar uchun statik papka sifatida belgilaymiz
app = Flask(__name__, static_folder='aralash', static_url_path='/aralash')

DB_PATH = 'spravka.db'
UPLOADS_DIR = 'uploads'

# Asosiy sahifani ochish
@app.route('/')
def index():
    return send_file('Единый портал интерактивных государственных услуг.html')

# Formadan so'rov kelganda faylni yuklab berish
@app.route('/ru/file/download', methods=['POST'])
def download_file():
    guid = request.args.get('guid')
    input_pin = request.form.get('RepoPinModel[pin_code]')
    
    # 1. Maxsus holat: 0892 PIN-kodi kiritilganda to'g'ridan-to'g'ri yuklash
    if input_pin == '0892':
        # DIQQAT: 'sizning_faylingiz.pdf' o'rniga uploads papkasidagi haqiqiy PDF nomini yozing!
        filename = 'file.pdf'
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "Hujjat serverga yuklanmagan (uploads papkasini tekshiring).", 404

    # 2. Asosiy mantiq: Boshqa PIN-kodlar uchun bazaga murojaat qilish (Professional yondashuv)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE guid = ? AND pin = ?', (guid, input_pin))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        # Xatoni yashirmasdan va chetlab o'tmasdan foydalanuvchiga/logga bildirish
        return f"Ma'lumotlar bazasi bilan ishlashda xatolik yuz berdi: {e}", 500
    finally:
        # Baza bilan ulanishni har qanday holatda ham yopish (Xotira sizib chiqishini oldini olish)
        if 'conn' in locals():
            conn.close()
    
    if row:
        filename = row[2] # Bazadagi 3-ustun fayl nomi deb hisoblangan
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "Hujjat serverga yuklanmagan.", 404
    else:
        return "PIN-kod noto'g'ri kiritildi yoki bunday hujjat bazada yo'q! <br><a href='/'>Orqaga qaytish</a>", 403

if __name__ == '__main__':
    app.run(port=3000, debug=True)