# 🎓 Advanced Mini LMS Koding Anak By SendPain11

Sistem pembelajaran coding yang lengkap dengan fitur **anti-contek**, **randomized questions**, dan **session management**.

## ✨ Fitur Lengkap

### 👦 Untuk Siswa:
- ✅ Login dengan ID unik
- 📝 Kerjakan quiz dengan soal random (urutan berbeda tiap siswa)
- 🔒 **Session Lock**: 1 modul hanya bisa dikerjakan 1x
- 📊 Lihat semua hasil dan nilai
- 💡 Review pembahasan soal yang salah
- 📄 Download laporan PDF hasil ujian
- 🚫 Tidak bisa mengulang quiz yang sama

### 👩‍🏫 Untuk Guru:
- ➕ Buat modul baru
- 📤 Upload soal (manual input atau JSON)
- 🗑️ Hapus modul
- 👁️ Lihat preview soal per modul
- 📊 Lihat hasil semua siswa
- 📈 Statistik kelas (rata-rata, distribusi nilai)
- 📄 Download laporan PDF per siswa
- 🔍 Review detail jawaban siswa

## 🚀 Cara Install

```bash
# 1. Install dependencies
pip install streamlit fpdf plotly

# 2. Jalankan aplikasi
streamlit run app.py

# 3. Buka di browser
# http://localhost:8501
```

## 📖 Cara Menggunakan

### Sebagai Guru:

1. **Login:**
   - Pilih role "👩‍🏫 Guru"
   - Masukkan password: `admin123`

2. **Buat Modul:**
   - Tab "Kelola Modul"
   - Buat modul baru (contoh: "Python Dasar")

3. **Tambah Soal (2 Cara):**

   **Cara 1 - Manual Input:**
   - Tab "Upload Soal"
   - Pilih modul
   - Isi form soal
   - Klik "Simpan Soal"

   **Cara 2 - Upload JSON:**
   - Buat file JSON (lihat format di bawah)
   - Upload di tab "Upload Soal"
   - Klik "Import ke Modul"

4. **Monitor Siswa:**
   - Tab "Hasil Siswa": Lihat detail hasil per siswa
   - Tab "Statistik": Lihat overview kelas

### Sebagai Siswa:

1. **Login:**
   - Pilih role "👦 Siswa"
   - Masukkan Nama & ID Siswa

2. **Kerjakan Quiz:**
   - Tab "Kerjakan Quiz"
   - Pilih modul (yang belum dikerjakan)
   - Klik "🚀 Mulai"
   - ⚠️ **PERHATIAN**: Setiap modul hanya bisa dikerjakan 1x!
   - Jawab semua soal
   - Klik "Submit Jawaban"

3. **Lihat Hasil:**
   - Setelah submit, langsung lihat nilai
   - Review pembahasan soal yang salah
   - Download laporan PDF
   - Tab "Hasil Saya": Lihat riwayat semua quiz

## 📁 Format JSON untuk Upload Soal

Buat file dengan format berikut:

```json
[
    {
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
        "question": "Simbol untuk komentar di Python?",
        "options": ["#", "//", "/*", "--"],
        "answer": "#",
        "explanation": "Simbol # digunakan untuk membuat komentar satu baris di Python"
    },
    {
        "question": "Tipe data untuk angka desimal?",
        "options": ["float", "int", "str", "bool"],
        "answer": "float",
        "explanation": "Float digunakan untuk menyimpan angka desimal seperti 3.14"
    }
]
```

**Aturan Format:**
- File harus array/list (dimulai dengan `[` dan diakhiri `]`)
- Setiap soal adalah object dengan field:
  - `question`: String pertanyaan
  - `options`: Array 4 pilihan jawaban
  - `answer`: String jawaban yang benar (harus sama persis dengan salah satu option)
  - `explanation`: String penjelasan untuk siswa

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

### 3. Individual Storage
- Hasil tiap siswa tersimpan terpisah
- File: `data/{student_id}_{module_name}.json`
- Tidak bisa diedit siswa

## 📂 Struktur Folder

```
project/
├── app.py                      # File utama
├── requirements.txt            # Dependencies
│
├── modules/                    # Bank soal per modul
│   ├── Python_Dasar.json
│   ├── Python_Lanjut.json
│   └── JavaScript_Intro.json
│
├── data/                       # Hasil ujian siswa
│   ├── SIS001_Python_Dasar.json
│   ├── SIS001_JavaScript_Intro.json
│   └── SIS002_Python_Dasar.json
│
├── sessions/                   # Session lock siswa
│   ├── SIS001_Python_Dasar.json
│   └── SIS002_Python_Dasar.json
│
└── reports/                    # PDF reports
    ├── SIS001_Python_Dasar.pdf
    └── SIS002_Python_Dasar.pdf
```

## 🎯 Contoh Use Case

### Scenario 1: Guru Membuat Quiz
```
1. Login sebagai Guru
2. Buat modul "Python Dasar"
3. Tambah 10 soal (manual atau JSON)
4. Siswa bisa mulai mengerjakan
```

### Scenario 2: Siswa Mengerjakan Quiz
```
1. Login dengan ID: SIS001
2. Lihat modul "Python Dasar" (belum dikerjakan)
3. Klik "Mulai" → Soal di-random
4. Jawab semua soal
5. Submit → Lihat nilai & pembahasan
6. Download PDF
7. ✅ Modul "Python Dasar" sekarang LOCKED
```

### Scenario 3: Guru Melihat Hasil
```
1. Tab "Hasil Siswa"
2. Filter by modul (opsional)
3. Lihat detail jawaban tiap siswa
4. Download PDF report
5. Tab "Statistik" untuk overview kelas
```

## ⚙️ Konfigurasi

### Password Guru
Default: `admin123`

Untuk mengganti, edit di code:
```python
if guru_password != "admin123":  # Ganti password di sini
```

### Passing Grade
Saat ini: 60/100

Untuk mengganti, edit di fungsi `create_pdf_report()`:
```python
if score >= 80:
    status = "LUAR BIASA!"
elif score >= 70:  # Sesuaikan nilai ini
    status = "BAGUS!"
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fpdf'"
```bash
pip install fpdf
```

### Quiz sudah dikerjakan tapi ingin reset
1. Hapus file di folder `sessions/SIS001_Python_Dasar.json`
2. Siswa bisa mengerjakan lagi

### Soal tidak muncul
- Pastikan modul sudah dibuat
- Pastikan ada soal di modul (minimal 1)
- Check folder `modules/` ada file JSON

### PDF error encoding
Jika ada karakter special yang error, gunakan huruf standar di soal dan penjelasan.

## 📝 TODO / Future Features

- [ ] Multi-choice questions (pilih lebih dari 1)
- [ ] Essay questions
- [ ] Timer per quiz
- [ ] Leaderboard
- [ ] Certificate generator
- [ ] Email notifikasi ke siswa
- [ ] Backup & restore database
- [ ] Export ke Excel


## 👤 Author

**Sendy Prismana Nurferian**
- GitHub: [@yourusername](https://github.com/SendPain11)
- LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/sendy-prismana-nurferian-95a27b213/)
- Email: sendyprisma02@gmail.com
- Documentation Project: [streamlit web](OnTheWay)


## 🤝 Contributing

Silakan fork dan submit PR untuk improvement!

## 📄 License

MIT License - Free to use untuk pendidikan

---

**Made with ❤️ for Indonesian kids learning to code** 🇮🇩🐍
