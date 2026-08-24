# 📋 CHANGELOG — v1 → v2

## [2.0.0] — Advanced Mini LMS Koding Anak

### Ringkasan
Semua 8 item di daftar "TODO / Fitur Mendatang" pada `README.md` v1 sudah diimplementasikan. Kode dipecah dari 1 file (`web.py`, 894 baris) menjadi `app.py` + 6 modul di `utils/` agar lebih mudah dibaca dan dirawat.

### ✨ Ditambahkan
- **Tipe soal pilihan ganda (`multiple`)** — siswa bisa memilih lebih dari satu jawaban benar; dinilai dengan skema partial credit.
- **Tipe soal essay (`essay`)** — dijawab bebas oleh siswa, dinilai manual oleh guru (0–100) di dashboard, dengan status submission `"Menunggu Review"` → `"Selesai"`.
- **Timer per modul** — guru mengatur batas waktu (menit) per modul; ditampilkan sebagai countdown ke siswa dan ditegakkan di server saat submit.
- **Leaderboard** — ranking nilai tertinggi, bisa difilter per modul, tersedia di sisi Guru maupun Siswa.
- **Generator sertifikat PDF** — diterbitkan otomatis untuk siswa dengan nilai ≥ passing grade modul (default 60, bisa diatur per modul).
- **Notifikasi email (SMTP)** — konfigurasi di dashboard Guru (disarankan Gmail App Password); email otomatis terkirim setelah submit quiz beserta lampiran PDF laporan; guru juga bisa kirim ulang manual.
- **Backup & restore database** — export seluruh data (modul, hasil, session, laporan, config) jadi satu file `.zip`; bisa di-restore kembali dari file `.zip` tersebut.
- **Export hasil ke Excel** — file `.xlsx` dengan sheet "Ringkasan" (per siswa) dan "Detail Jawaban" (per soal).

### 🔧 Diubah
- Struktur data soal sekarang punya field `"type"` (`single` / `multiple` / `essay`). Soal lama tanpa field ini otomatis dianggap `single` — **tidak butuh migrasi data manual**.
- Struktur hasil siswa (`data/*.json`) bertambah field `"status"` (`Selesai` / `Menunggu Review`) dan `"email"` (opsional).
- Setiap modul sekarang punya file meta terpisah (`modules/<nama>.meta.json`) berisi `time_limit_minutes` dan `passing_grade`.

### 🔒 Keamanan / Privasi
- Konfigurasi email (App Password) disimpan di `config/email_config.json` — **tidak untuk di-commit ke repo publik** (sudah dimasukkan ke `.gitignore`).
- Folder `data/`, `sessions/`, `reports/`, `certificates/`, `backups/` berisi data/identitas siswa — juga diexclude dari git.

### 📦 Dependensi Baru
`requirements.txt` bertambah: `pandas`, `openpyxl` (untuk export Excel), `plotly` (untuk grafik statistik).

### File Tidak Berubah
- `web.py` dan `web_sementara.py` (v1) dibiarkan apa adanya sebagai referensi/pembanding.
