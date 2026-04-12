import sqlite3

def init_db():
    # spravka.db bazasiga ulanish (fayl yo'q bo'lsa, o'zi yaratadi)
    conn = sqlite3.connect('spravka.db')
    cursor = conn.cursor()
    
    # Jadvalni yaratish
    cursor.execute("CREATE TABLE IF NOT EXISTS documents (guid TEXT, pin TEXT, filename TEXT)")
    
    # Baza ichiga test ma'lumotlarni qo'shish
    cursor.execute("INSERT INTO documents (guid, pin, filename) VALUES (?, ?, ?)", 
                   ("8267-6669-db97-4183-f1a8-5183-1317", "0892", "file.pdf"))
    
    conn.commit()
    conn.close()
    print("spravka.db fayli muvaffaqiyatli yaratildi!")

if __name__ == '__main__':
    init_db()