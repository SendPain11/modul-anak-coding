# ==========================================================
# STREAMLIT MINI LMS KODING ANAK (MULTI-PAGE READY)
# FITUR 1-4:
# 1. Sidebar otomatis sesuai role
# 2. Bank soal modular
# 3. Hasil murid tersimpan & bisa dilihat guru
# 4. Guru bisa download & review hasil murid
# ==========================================================

import streamlit as st
from fpdf import FPDF
import os, random, json
from datetime import datetime

# ================== KONFIG ==================
st.set_page_config(page_title="Mini LMS Koding Anak", page_icon="🐍")
REPORT_DIR = "reports"
DATA_DIR = "data"
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ================== SESSION INIT ==================
if "role" not in st.session_state:
    st.session_state.role = None

# ================== BANK SOAL ==================
BANK_SOAL = {
    "Modul 1 - Dasar Python": [
        {
            "q": "Apa fungsi print()?",
            "options": ["Menampilkan teks", "Menghapus data", "Menggambar"],
            "answer": "Menampilkan teks",
            "explain": "print() digunakan untuk menampilkan teks ke layar"
        },
        {
            "q": "10 + 5 = ?",
            "options": ["15", "5", "50"],
            "answer": "15",
            "explain": "10 ditambah 5 hasilnya 15"
        },
        {
            "q": "Simbol perkalian di Python?",
            "options": ["*", "x", "+"],
            "answer": "*",
            "explain": "Tanda * digunakan untuk perkalian"
        }
    ]
}

# ================== PDF ==================
def create_pdf(name, sid, score, detail):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 12, "HASIL BELAJAR KODING", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Nama: {name}", ln=True)
    pdf.cell(0, 8, f"ID: {sid}", ln=True)
    pdf.cell(0, 8, f"Tanggal: {datetime.now().strftime('%d-%m-%Y')}", ln=True)

    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"Nilai Akhir: {score}", ln=True)

    pdf.ln(5)
    for d in detail:
        pdf.set_font("helvetica", "B", 11)
        pdf.multi_cell(0, 7, f"Soal: {d['q']}")
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 7, f"Jawaban: {d['user']}")
        pdf.multi_cell(0, 7, f"Status: {d['status']}")
        pdf.set_font("helvetica", "I", 10)
        pdf.multi_cell(0, 7, f"Penjelasan: {d['explain']}")
        pdf.ln(2)

    return pdf.output(dest="S").encode("latin-1")

# ================== LANDING ==================
st.title("🎮 Mini LMS Koding Anak")
st.write("Belajar koding dengan seru dan terarah 🚀")

with st.expander("👀 Coba Python"):
    st.code('print("Halo Dunia")\n5 + 5', language="python")

st.divider()

# ================== ROLE ==================
st.session_state.role = st.selectbox(
    "Masuk sebagai:",
    ["Pilih...", "👦 Murid", "👩‍🏫 Guru"]
)

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("📚 Menu")
    if st.session_state.role == "👦 Murid":
        st.success("Mode Murid")
        st.markdown("- 📝 Kerjakan Kuis")
    elif st.session_state.role == "👩‍🏫 Guru":
        st.success("Mode Guru")
        st.markdown("- 📊 Lihat Hasil Murid")
    else:
        st.info("Pilih role terlebih dahulu")

    st.divider()
    st.markdown("### 🔗 Belajar Mandiri")
    st.markdown("- Code.org\n- freeCodeCamp\n- Kelas Terbuka")

# ================== MURID ==================
if st.session_state.role == "👦 Murid":
    st.subheader("👦 Halaman Murid")
    nama = st.text_input("Nama Lengkap")
    sid = st.text_input("ID Siswa")

    modul = st.selectbox("Pilih Modul", list(BANK_SOAL.keys()))
    soal = random.sample(BANK_SOAL[modul], len(BANK_SOAL[modul]))

    jawaban = []
    for i, s in enumerate(soal):
        st.markdown(f"**Soal {i+1}:** {s['q']}")
        pilih = st.radio("Jawaban:", s['options'], key=f"jawab_{i}")
        ragu = st.checkbox("🤔 Ragu", key=f"ragu_{i}")
        if st.button("🧹 Reset", key=f"reset_{i}"):
            st.session_state[f"jawab_{i}"] = None
            st.session_state[f"ragu_{i}"] = False
        jawaban.append({"user": pilih, "ragu": ragu, **s})
        st.divider()

    if st.button("🚀 Kirim Jawaban"):
        if not nama or not sid:
            st.warning("Nama & ID wajib diisi")
        else:
            nilai = 0
            hasil_detail = []
            for j in jawaban:
                benar = j['user'] == j['answer']
                if benar:
                    nilai += int(100 / len(jawaban))
                hasil_detail.append({
                    "q": j['q'],
                    "user": j['user'],
                    "status": "BENAR" if benar else "SALAH",
                    "explain": j['explain'],
                    "ragu": j['ragu']
                })

            data = {
                "nama": nama,
                "id": sid,
                "nilai": nilai,
                "detail": hasil_detail,
                "waktu": datetime.now().isoformat()
            }

            with open(f"{DATA_DIR}/{sid}.json", "w") as f:
                json.dump(data, f, indent=2)

            pdf = create_pdf(nama, sid, nilai, hasil_detail)
            with open(f"{REPORT_DIR}/{sid}.pdf", "wb") as f:
                f.write(pdf)

            st.success(f"Nilai kamu: {nilai}")
            st.download_button("📥 Download PDF", pdf, f"Hasil_{sid}.pdf")

# ================== GURU ==================
if st.session_state.role == "👩‍🏫 Guru":
    st.subheader("👩‍🏫 Dashboard Guru")
    pwd = st.text_input("Password Guru", type="password")

    if pwd == "admin123":
        st.success("Login berhasil")
        files = os.listdir(DATA_DIR)
        if not files:
            st.info("Belum ada data murid")
        for f in files:
            with open(f"{DATA_DIR}/{f}") as jf:
                data = json.load(jf)
            st.markdown(f"### 👦 {data['nama']} ({data['id']})")
            st.write(f"Nilai: {data['nilai']}")
            st.download_button("📄 PDF", open(f"{REPORT_DIR}/{data['id']}.pdf", "rb"), f"{data['id']}.pdf")
            st.divider()
