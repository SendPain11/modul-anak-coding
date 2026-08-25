# 🎓 Advanced Mini LMS Koding Anak By SendPain11

Sistem pembelajaran coding yang lengkap dengan fitur **anti-contek**, **randomized questions**, **session management**, **timer**, **leaderboard**, **sertifikat**, **notifikasi email**, **backup/restore**, dan **export Excel**.

> **v2.0** — lihat [`CHANGELOG.md`](CHANGELOG.md) untuk detail perubahan dari v1. File `web.py` (v1) tetap disimpan di repo ini sebagai referensi/pembanding.

## ✨ Fitur Lengkap

### 👦 Untuk Siswa:
- ✅ Login dengan ID unik + email opsional (untuk notifikasi hasil)
- 📝 Kerjakan quiz dengan soal random (urutan berbeda tiap siswa)
- 🔘☑️✍️ 3 tipe soal: pilihan tunggal, pilihan ganda (>1 jawaban benar), dan essay
- ⏱️ Timer per quiz (kalau diaktifkan guru)
- 🔒 **Session Lock**: 1 modul hanya bisa dikerjakan 1x
- 📊 Lihat semua hasil dan nilai
- 💡 Review pembahasan soal yang salah
- 📄 Download laporan PDF hasil ujian
- 🏆 Download sertifikat PDF (kalau nilai ≥ passing grade)
- 🏅 Lihat Leaderboard antar siswa
- 🚫 Tidak bisa mengulang quiz yang sama

### 👩‍🏫 Untuk Guru:
- ➕ Buat & kelola modul (atur timer & passing grade per modul)
- 📤 Upload soal (manual input atau JSON), termasuk soal essay & pilihan ganda
- 🗑️ Hapus modul
- 👁️ Lihat preview soal per modul
- 📊 Lihat hasil semua siswa & nilai soal essay secara manual
- 📈 Statistik kelas (rata-rata, distribusi nilai) & Leaderboard
- 📄 Download laporan PDF per siswa
- 🎖️ Sertifikat otomatis untuk siswa yang lulus
- ✉️ Kirim notifikasi email hasil ujian ke siswa (SMTP/Gmail App Password)
- 💾 Backup & restore seluruh database (satu file `.zip`)
- 📥 Export semua hasil ujian ke Excel (`.xlsx`)
- 🔍 Review detail jawaban siswa
- 🔓 Reset session siswa (izinkan mengulang modul tertentu)

## 🚀 Cara Install

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan aplikasi
streamlit run app.py

# 3. Buka di browser
# http://localhost:8501
```

## 📖 Cara Menggunakan

### Sebagai Guru:

1. **Login:**
   - Pilih role "👩‍🏫 Guru"
   - Masukkan password: `admin123` (lihat [Konfigurasi](#️-konfigurasi) untuk mengganti)

2. **Buat Modul:**
   - Tab "➕ Kelola Modul"
   - Buat modul baru (contoh: "Python Dasar")
   - Atur ⏱️ batas waktu (menit, 0 = tanpa batas) & 🎯 passing grade lewat tombol "⚙️ Setting"

3. **Tambah Soal (2 Cara):**

   **Cara 1 - Manual Input:**
   - Tab "📤 Upload Soal"
   - Pilih modul
   - Pilih tipe soal: 🔘 Pilihan Tunggal / ☑️ Pilihan Ganda / ✍️ Essay
   - Isi form soal → Klik "Simpan Soal"

   **Cara 2 - Upload JSON:**
   - Buat file JSON (lihat format di bawah, mendukung 3 tipe soal)
   - Upload di tab "📤 Upload Soal"
   - Klik "Import ke Modul"

4. **Monitor Siswa:**
   - Tab "📊 Hasil & Review": lihat detail hasil per siswa, nilai soal essay secara manual, kirim email, download sertifikat/PDF
   - Tab "📈 Statistik & Leaderboard": overview kelas & ranking nilai
   - Tab "✉️ Email": konfigurasi SMTP untuk notifikasi otomatis
   - Tab "💾 Backup/Restore": backup seluruh data jadi `.zip`, atau restore dari backup
   - Tab "📥 Export Excel": download semua hasil sebagai `.xlsx`

### Sebagai Siswa:

1. **Login:**
   - Pilih role "👦 Siswa"
   - Masukkan Nama, ID Siswa, dan email (opsional — untuk terima notifikasi hasil)

2. **Kerjakan Quiz:**
   - Tab "📝 Kerjakan Quiz"
   - Pilih modul (yang belum dikerjakan)
   - Klik "🚀 Mulai"
   - ⚠️ **PERHATIAN**: Setiap modul hanya bisa dikerjakan 1x! Perhatikan timer kalau modul punya batas waktu.
   - Jawab semua soal (pilihan tunggal / centang lebih dari 1 untuk pilihan ganda / tulis bebas untuk essay)
   - Klik "Submit Jawaban"

3. **Lihat Hasil:**
   - Setelah submit, langsung lihat nilai (soal essay berstatus "Menunggu Review" sampai dinilai guru)
   - Review pembahasan soal yang salah
   - Download laporan PDF & sertifikat (kalau lulus)
   - Tab "📊 Hasil Saya": lihat riwayat semua quiz
   - Tab "🏆 Leaderboard": lihat ranking nilai antar siswa

## 📁 Format JSON untuk Upload Soal

Mendukung 3 tipe soal — `single`, `multiple`, `essay`. Soal tanpa field `"type"` otomatis dianggap `single` (kompatibel dengan format v1 lama).

```json
[
    {
        "type": "single",
        "question": "Apa fungsi print() di Python?",
        "options": [
            "Menampilkan output ke layar",
            "Menyimpan data ke file",
            "Menghitung angka",
            "Menghapus variabel"
        ],
        "answer": "Menampilkan output ke layar",
        "explanation": "Fungsi print() digunakan untuk menampilkan output atau hasil ke layar/console"
    },
    {
        "type": "multiple",
        "question": "Manakah yang termasuk tipe data di Python? (pilih semua yang benar)",
        "options": ["int", "float", "loop", "str"],
        "answer": ["int", "float", "str"],
        "explanation": "int, float, str adalah tipe data. loop bukan tipe data."
    },
    {
        "type": "essay",
        "question": "Jelaskan perbedaan list dan tuple di Python!",
        "model_answer": "List bisa diubah (mutable), tuple tidak bisa diubah (immutable)",
        "explanation": "Konsep dasar struktur data Python"
    }
]
```

**Aturan Format:**
- File harus array/list (dimulai dengan `[` dan diakhiri `]`)
- Field umum tiap soal: `type` (`single`/`multiple`/`essay`, opsional — default `single`), `question`, `explanation`
- Untuk `single`/`multiple`: `options` (array pilihan), `answer` (string untuk `single`, array untuk `multiple` — harus sama persis dengan salah satu/beberapa `options`)
- Untuk `essay`: `model_answer` (opsional, referensi guru saat menilai manual)

## 🔒 Sistem Anti-Contek

### 1. Randomized Questions
- Setiap siswa mendapat urutan soal berbeda
- Soal di-shuffle saat siswa klik "Mulai"
- Siswa A dan Siswa B pasti berbeda urutan

### 2. Session Lock
- Setelah mulai quiz, session dibuat di folder `sessions/`
- File: `{student_id}_{module_name}.json`
- Siswa tidak bisa mengerjakan modul yang sama lagi
- Button "Mulai" berubah jadi "🔒 Locked"
- Guru bisa reset session tertentu lewat tab "📊 Hasil & Review" kalau siswa perlu mengulang

### 3. Individual Storage
- Hasil tiap siswa tersimpan terpisah
- File: `data/{student_id}_{module_name}.json`
- Tidak bisa diedit siswa

### 4. Timer (v2)
- Guru bisa mengatur batas waktu per modul
- Ditampilkan sebagai countdown ke siswa, dan ditegakkan di server saat submit

## 📂 Struktur Folder

```
project/
├── app.py                      # File utama (Streamlit UI)
├── requirements.txt            # Dependencies
├── README.md / CHANGELOG.md    # Dokumentasi
├── web.py                      # Versi v1 (referensi, tidak dipakai lagi)
│
├── utils/                      # Modul logika (v2)
│   ├── storage.py               # baca/tulis modul, soal, session, hasil, config
│   ├── scoring.py                # penilaian single/multiple/essay
│   ├── pdf_utils.py              # laporan PDF & sertifikat
│   ├── email_utils.py            # notifikasi email (SMTP)
│   ├── excel_utils.py            # export ke .xlsx
│   └── timer_utils.py            # timer/countdown quiz
│
├── modules/                    # Bank soal per modul (+ file .meta.json: timer & passing grade)
│   ├── Python_Dasar.json
│   ├── Python_Dasar.meta.json
│   └── JavaScript_Intro.json
│
├── data/                       # Hasil ujian siswa (JANGAN di-commit ke git)
│   ├── SIS001_Python_Dasar.json
│   └── SIS002_Python_Dasar.json
│
├── sessions/                   # Session lock siswa (JANGAN di-commit)
│   └── SIS001_Python_Dasar.json
│
├── reports/                    # PDF laporan (JANGAN di-commit)
│   └── SIS001_Python_Dasar.pdf
│
├── certificates/               # Sertifikat (dibuat on-demand)
├── config/                     # Konfigurasi email — berisi App Password! (JANGAN di-commit)
└── backups/                    # File backup .zip
```

> Folder `data/`, `sessions/`, `reports/`, `certificates/`, `backups/`, `config/` sudah masuk `.gitignore` karena berisi data pribadi siswa & kredensial email.

## 🎯 Contoh Use Case

### Scenario 1: Guru Membuat Quiz
```
1. Login sebagai Guru
2. Buat modul "Python Dasar", atur timer 30 menit & passing grade 70
3. Tambah 10 soal (campuran pilihan tunggal, pilihan ganda, essay)
4. Siswa bisa mulai mengerjakan
```

### Scenario 2: Siswa Mengerjakan Quiz
```
1. Login dengan ID: SIS001, isi email opsional
2. Lihat modul "Python Dasar" (belum dikerjakan)
3. Klik "Mulai" → Soal di-random, timer mulai berjalan
4. Jawab semua soal
5. Submit → Lihat nilai & pembahasan (soal essay: "Menunggu Review")
6. Download PDF, cek Leaderboard
7. ✅ Modul "Python Dasar" sekarang LOCKED
```

### Scenario 3: Guru Melihat & Menilai Hasil
```
1. Tab "Hasil & Review"
2. Filter by modul / status (Selesai / Menunggu Review)
3. Beri nilai soal essay (slider 0-100) → nilai akhir dihitung ulang otomatis
4. Download PDF report / terbitkan sertifikat
5. Kirim email notifikasi (kalau diaktifkan)
6. Tab "Statistik & Leaderboard" untuk overview kelas
7. Tab "Export Excel" untuk laporan ke pihak lain
```

## ⚙️ Konfigurasi

### Password Guru
Default: `admin123`

Untuk mengganti, edit di `app.py`:
```python
if guru_password != "admin123":  # Ganti password di sini
```

### Passing Grade & Timer
Diatur **per modul** lewat UI (tab "➕ Kelola Modul" → "⚙️ Setting"), disimpan di `modules/<nama>.meta.json`. Default passing grade: 60/100.

### Email Notifikasi
Diatur lewat UI (tab "✉️ Email") — pakai Gmail App Password, bukan password akun biasa:
1. Aktifkan 2-Step Verification di akun Gmail pengirim
2. Buat App Password di `myaccount.google.com/apppasswords`
3. Masukkan di form konfigurasi email

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fpdf'/'openpyxl'/dst"
```bash
pip install -r requirements.txt
```

### Quiz sudah dikerjakan tapi ingin reset
- Cara mudah: tab "📊 Hasil & Review" (Guru) → tombol "🔓 Reset Session Siswa"
- Manual: hapus file `sessions/{student_id}_{module_name}.json`

### Soal tidak muncul
- Pastikan modul sudah dibuat
- Pastikan ada soal di modul (minimal 1)
- Check folder `modules/` ada file JSON

### PDF error encoding
Jika ada karakter special yang error, gunakan huruf standar di soal dan penjelasan.

### Email gagal terkirim
- Pastikan pakai Gmail App Password (bukan password akun), 2-Step Verification aktif
- Coba tombol "Kirim Email Test" di tab Email untuk debug cepat

### Excel export error
```bash
pip install openpyxl pandas
```

## 📝 Status Fitur

Semua fitur di daftar "TODO / Future Features" v1 sudah selesai di v2 — detail lengkap ada di [`CHANGELOG.md`](CHANGELOG.md):

- [x] Multi-choice questions (pilih lebih dari 1)
- [x] Essay questions
- [x] Timer per quiz
- [x] Leaderboard
- [x] Certificate generator
- [x] Email notifikasi ke siswa
- [x] Backup & restore database
- [x] Export ke Excel

## 👤 Author

**Sendy Prismana Nurferian**
- GitHub: [@SendPain11](https://github.com/SendPain11)
- LinkedIn: [Sendy Prismana Nurferian](https://www.linkedin.com/in/sendy-prismana-nurferian-95a27b213/)
- Email: sendyprisma02@gmail.com
- Documentation Project: [modul-anak-coding](https://modul-anak-coding-sendpain11.streamlit.app/)

## 🤝 Contributing

Silakan fork dan submit PR untuk improvement!

## 📄 License

MIT License - Free to use untuk pendidikan

---

**Made with ❤️ for Indonesian kids learning to code** 🇮🇩🐍
