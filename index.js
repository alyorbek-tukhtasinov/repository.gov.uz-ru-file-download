const express = require('express');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();

const app = express();
app.use(express.urlencoded({ extended: true }));

// Statik fayllar (CSS, rasmlar, JS) papkasiga ruxsat berish
app.use('/aralash', express.static(path.join(__dirname, 'aralash')));

const port = 3000;
const dbPath = path.join(__dirname, 'spravka.db');

const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error("Database connection error:", err.message);
});

// Asosiy sahifani ochish uchun
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'Единый портал интерактивных государственных услуг.html'));
});

// '/ru/file/download' manziliga tushgan barcha POST so'rovlarni qabul qilish
app.post('*', (req, res) => {
    const guid = req.query.guid;
    const inputPin = req.body['RepoPinModel[pin_code]']; 

    // Baza ichidan qidiramiz
    db.get('SELECT * FROM documents WHERE guid = ? AND pin = ?', [guid, inputPin], (err, row) => {
        if (err) {
            return res.status(500).send("Bazaga ulanishda xato yuz berdi. Sababi: " + err.message);
        }

        if (row) {
            const filePath = path.join(__dirname, 'uploads', row.filename);
            if (fs.existsSync(filePath)) {
                res.download(filePath, row.filename);
            } else {
                res.status(404).send("Hujjat serverga yuklanmagan (uploads papkasini tekshiring).");
            }
        } else {
            res.status(403).send("PIN-kod noto'g'ri kiritildi yoki bunday hujjat bazada yo'q! <br><a href='/'>Orqaga qaytish</a>");
        }
    });
});

app.listen(port, () => {
    console.log(`Lokal server http://localhost:${port} da ishga tushdi...`);
});