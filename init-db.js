const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./spravka.db');

db.serialize(() => {
    // Jadval yaratish
    db.run("CREATE TABLE IF NOT EXISTS documents (guid TEXT, pin TEXT, filename TEXT)");
    
    // Baza ichiga test ma'lumotlarni qo'shish
    const stmt = db.prepare("INSERT INTO documents (guid, pin, filename) VALUES (?, ?, ?)");
    
    // HTML faylingizdagi guid va unga mos pin, hamda pdf fayl nomi
    stmt.run("8267-6669-db97-4183-f1a8-5183-1317", "0892", "file.pdf");
    
    // Yangi PDF hujjatni bazaga qo'shish (guid, pin, fayl_nomi)
    stmt.run("yangi-guid-raqami-12345", "0892", "file.pdf");
    stmt.finalize();
});

db.close(() => {
    console.log("spravka.db fayli muvaffaqiyatli yaratildi!");
});