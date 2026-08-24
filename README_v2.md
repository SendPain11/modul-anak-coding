# 🎓 Advanced Mini LMS Koding Anak — v2.0

Versi 2 ini mengimplementasikan **semua 8 item** di daftar "TODO / Future Features" pada README v1:

| # | Fitur | Status |
|---|-------|--------|
| 1 | Multi-choice questions (pilih lebih dari 1) | ✅ |
| 2 | Essay questions | ✅ |
| 3 | Timer per quiz | ✅ |
| 4 | Leaderboard | ✅ |
| 5 | Certificate generator | ✅ |
| 6 | Email notifikasi ke siswa | ✅ |
| 7 | Backup & restore database | ✅ |
| 8 | Export ke Excel | ✅ |

## 🚀 Cara Install & Jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka di browser: `http://localhost:8501`

## 📁 Struktur Kode (dimodulkan dari v1)

```
lms_v2/
├── app.py                  # UI utama Streamlit (Guru & Siswa)
├── requirements.txt
├── utils/
│   ├── storage.py           # baca/tulis modul, soal, session, hasil, config
│   ├── scoring.py            # logika penilaian single/multiple/essay
│   ├── pdf_utils.py          # generate laporan PDF & sertifikat PDF
│   ├── email_utils.py        # kirim notifikasi email (SMTP)
│   ├── excel_utils.py        # export hasil ke .xlsx
│   └── timer_utils.py        # hitung mundur & penegakan batas waktu
├── modules/                 # dibuat otomatis saat run: bank soal per modul
├── data/                    # dibuat otomatis: hasil ujian siswa
├── sessions/                # dibuat otomatis: session lock anti-contek
├── reports/                 # dibuat otomatis: PDF laporan
├── certificates/            # (opsional, sertifikat dibuat on-demand)
├── config/                  # dibuat otomatis: konfigurasi email
└── backups/                 # dibuat otomatis: file backup zip
```

> File `web.py` (v1) tetap ada dan tidak diubah — v2 adalah aplikasi baru di `app.py` + `utils/`, jadi bisa dibandingkan langsung.

## ✨ Detail Fitur Baru

### 1. Multi-choice Questions
- Saat guru upload soal, pilih tipe **"☑️ Pilihan Ganda"**.
- Guru bisa memilih **lebih dari 1** jawaban benar.
- Siswa menjawab pakai checkbox, bisa centang beberapa opsi.
- Penilaian **partial credit**: `(jawaban_benar_dipilih - jawaban_salah_dipilih) / total_jawaban_benar`, minimum 0.

### 2. Essay Questions
- Guru bisa membuat soal essay dengan kunci/model jawaban referensi.
- Siswa menjawab bebas via text area.
- Hasil essay **berstatus "Menunggu Review"** sampai guru memberi nilai manual (slider 0–100) di tab **"📊 Hasil & Review"**.
- Setelah dinilai, skor akhir dihitung ulang, laporan PDF diregenerasi, dan email (jika aktif) otomatis dikirim.

### 3. Timer per Quiz
- Guru mengatur batas waktu (menit) per modul di tab **"➕ Kelola Modul" → ⚙️ Setting** (0 = tanpa batas).
- Siswa melihat countdown visual saat mengerjakan.
- Waktu ditegakkan di **server-side**: kalau waktu habis, form otomatis disubmit dengan jawaban yang sudah terisi.

### 4. Leaderboard
- Tab **"🏆 Leaderboard"** tersedia untuk Siswa & Guru.
- Bisa difilter per modul, menampilkan top 20 nilai tertinggi (hanya hasil yang sudah "Selesai", bukan yang masih menunggu review essay).

### 5. Certificate Generator
- Sertifikat PDF (landscape, desain sederhana dengan border) otomatis bisa di-download siswa/guru **jika nilai ≥ passing grade modul** (diatur per modul, default 60).

### 6. Email Notifikasi
- Tab **"✉️ Email"** di dashboard Guru untuk konfigurasi SMTP (disarankan Gmail + App Password, bukan password akun biasa).
- Siswa bisa mengisi email opsional saat login.
- Email otomatis terkirim setelah submit quiz (kalau fitur diaktifkan & siswa mengisi email), termasuk lampiran PDF laporan.
- Guru juga bisa kirim ulang email manual per siswa dari tab Hasil.
- **Catatan keamanan:** App Password disimpan sebagai plain text di `config/email_config.json` pada server. Jangan gunakan password akun utama, dan jangan commit folder `config/` ke repo publik (`.gitignore` disarankan).

### 7. Backup & Restore
- Tab **"💾 Backup/Restore"**: tombol untuk membuat file `.zip` berisi semua modul, hasil siswa, session, laporan PDF, dan konfigurasi email → langsung bisa di-download.
- Restore dengan upload file `.zip` backup; data di-*merge/overwrite* ke folder yang sesuai.

### 8. Export ke Excel
- Tab **"📥 Export Excel"**: download `.xlsx` berisi 2 sheet:
  - **Ringkasan**: 1 baris per siswa per modul (nama, ID, email, modul, nilai, status, waktu).
  - **Detail Jawaban**: 1 baris per soal (tipe, pertanyaan, jawaban siswa, jawaban benar, skor).

## 🔄 Kompatibilitas dengan Data v1

- Soal lama (format v1, tanpa field `"type"`) otomatis dianggap tipe `"single"` — tidak perlu migrasi manual.
- Folder `modules/`, `data/`, `sessions/`, `reports/` dari v1 bisa langsung dipakai oleh v2 (struktur file kompatibel; v2 hanya menambah file `.meta.json` per modul untuk timer/passing grade dan field baru `status`/`email` di hasil siswa).

## 🐛 Troubleshooting Tambahan (v2)

**Email gagal terkirim**
- Pastikan pakai Gmail **App Password** (bukan password akun), dan 2-Step Verification sudah aktif di akun pengirim.
- Coba tombol "Kirim Email Test" di tab Email untuk debug cepat.

**Excel export error `ModuleNotFoundError: openpyxl`**
```bash
pip install openpyxl
```

**Timer tidak "hidup" (tidak berkurang otomatis) di layar**
- Countdown yang tampil bersifat visual (JS di browser). Penegakan waktu sebenarnya tetap dicek di server saat siswa submit — jadi walau angka di layar tidak refresh terus tanpa interaksi (batasan Streamlit), begitu tombol submit ditekan setelah waktu habis, sistem tetap tahu waktunya sudah lewat.
