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
    
    # Baza bilan ishlash
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documents WHERE guid = ? AND pin = ?', (guid, input_pin))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        filename = row[2]
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        if os.path.exists(file_path):
            # Faylni yuklab olish uchun berish
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "Hujjat serverga yuklanmagan (uploads papkasini tekshiring).", 404
    else:
        return "PIN-kod noto'g'ri kiritildi yoki bunday hujjat bazada yo'q! <br><a href='/'>Orqaga qaytish</a>", 403

if __name__ == '__main__':
    app.run(port=3000, debug=True)