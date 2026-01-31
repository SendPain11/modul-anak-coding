# ==========================================================
# ADVANCED MINI LMS KODING ANAK - FULL FEATURED
# ==========================================================
# FITUR LENGKAP:
# 1. Guru bisa upload soal per modul (JSON/CSV)
# 2. Soal random untuk tiap siswa (anti-contek!)
# 3. Session siswa: 1 modul = 1x pengerjaan only
# 4. Siswa bisa lihat pembahasan soal yang salah
# 5. Guru bisa lihat detail hasil semua murid
# 6. Bank soal tersimpan permanent
# 7. Manajemen modul (tambah, edit, hapus)
# INI ADALAH CODE DARI SendPain11
# ==========================================================

import streamlit as st
from fpdf import FPDF
import os, random, json, hashlib
from datetime import datetime
import pandas as pd

# ================== KONFIG ==================
st.set_page_config(
    page_title="Advanced Mini LMS",
    page_icon="🎓",
    layout="wide"
)

REPORT_DIR = "reports"
DATA_DIR = "data"
MODUL_DIR = "modules"
SESSION_DIR = "sessions"

for d in [REPORT_DIR, DATA_DIR, MODUL_DIR, SESSION_DIR]:
    os.makedirs(d, exist_ok=True)

# ================== SESSION INIT ==================
if "role" not in st.session_state:
    st.session_state.role = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# ================== HELPER FUNCTIONS ==================

def save_module(module_name, questions):
    """Simpan modul soal ke file JSON"""
    filepath = f"{MODUL_DIR}/{module_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def load_module(module_name):
    """Load modul soal dari file"""
    filepath = f"{MODUL_DIR}/{module_name}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_modules():
    """Dapatkan list semua modul"""
    if not os.path.exists(MODUL_DIR):
        return []
    files = [f.replace(".json", "") for f in os.listdir(MODUL_DIR) if f.endswith(".json")]
    return files

def check_student_session(student_id, module_name):
    """Cek apakah siswa sudah mengerjakan modul ini"""
    session_file = f"{SESSION_DIR}/{student_id}_{module_name}.json"
    return os.path.exists(session_file)

def create_student_session(student_id, module_name, questions_order):
    """Buat session untuk siswa (lock modul)"""
    session_file = f"{SESSION_DIR}/{student_id}_{module_name}.json"
    session_data = {
        "student_id": student_id,
        "module": module_name,
        "questions_order": questions_order,
        "timestamp": datetime.now().isoformat(),
        "completed": False
    }
    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)

def complete_student_session(student_id, module_name):
    """Tandai session sebagai selesai"""
    session_file = f"{SESSION_DIR}/{student_id}_{module_name}.json"
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            session_data = json.load(f)
        session_data["completed"] = True
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)

def save_student_result(student_id, name, module_name, score, details):
    """Simpan hasil ujian siswa"""
    result_file = f"{DATA_DIR}/{student_id}_{module_name}.json"
    result_data = {
        "student_id": student_id,
        "name": name,
        "module": module_name,
        "score": score,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

def get_student_results(student_id):
    """Ambil semua hasil siswa"""
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    
    for filename in os.listdir(DATA_DIR):
        if filename.startswith(student_id) and filename.endswith(".json"):
            with open(f"{DATA_DIR}/{filename}", "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results

def get_all_student_results():
    """Ambil semua hasil semua siswa (untuk guru)"""
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(f"{DATA_DIR}/{filename}", "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results

def create_pdf_report(name, sid, module, score, details):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 12, "LAPORAN HASIL BELAJAR", ln=True, align="C")
    
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Nama: {name}", ln=True)
    pdf.cell(0, 8, f"ID Siswa: {sid}", ln=True)
    pdf.cell(0, 8, f"Modul: {module}", ln=True)
    pdf.cell(0, 8, f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 14)
    if score >= 80:
        status = "LUAR BIASA!"
    elif score >= 70:
        status = "BAGUS!"
    elif score >= 60:
        status = "CUKUP"
    else:
        status = "PERLU BELAJAR LAGI"
    
    pdf.cell(0, 10, f"Nilai: {score}/100 - {status}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "DETAIL JAWABAN:", ln=True)
    
    # Detail per soal
    for i, d in enumerate(details, 1):
        pdf.ln(3)
        pdf.set_font("helvetica", "B", 11)
        pdf.multi_cell(0, 7, f"Soal {i}: {d['question']}")
        
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 6, f"Jawaban Anda: {d['user_answer']}")
        pdf.multi_cell(0, 6, f"Jawaban Benar: {d['correct_answer']}")
        
        pdf.set_font("helvetica", "B", 10)
        if d['is_correct']:
            pdf.set_text_color(0, 150, 0)
            pdf.cell(0, 6, "Status: BENAR", ln=True)
        else:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 6, "Status: SALAH", ln=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "I", 9)
        pdf.multi_cell(0, 6, f"Penjelasan: {d['explanation']}")
    
    # Footer
    pdf.ln(10)
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 5, "Generated by Advanced Mini LMS | Keep Learning! ", ln=True, align="C")
    
    return pdf.output(dest="S").encode("latin-1")

# ================== MAIN UI ==================
st.title("🎓 Advanced Mini LMS Koding Anak")
st.markdown("**Sistem Pembelajaran Koding yang Interaktif dan Anti-Contek!**")

# ================== ROLE SELECTION ==================
col1, col2 = st.columns([3, 1])

with col1:
    st.session_state.role = st.selectbox(
        "🔐 Login sebagai:",
        ["Pilih Role...", "👦 Siswa", "👩‍🏫 Guru"],
        key="role_selector"
    )

with col2:
    if st.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.divider()

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("📚 Navigation")
    
    if st.session_state.role == "👦 Siswa":
        st.success("Mode: **Siswa**")
        st.markdown("""
        **Menu Siswa:**
        - 📝 Kerjakan Quiz
        - 📊 Lihat Hasil Saya
        - 💡 Review Pembahasan
        """)
    elif st.session_state.role == "👩‍🏫 Guru":
        st.success("Mode: **Guru**")
        st.markdown("""
        **Menu Guru:**
        - ➕ Kelola Modul
        - 📤 Upload Soal
        - 📊 Lihat Hasil Siswa
        - 📈 Statistik Kelas
        """)
    else:
        st.info("Silakan pilih role untuk melanjutkan")
    
    st.divider()
    st.markdown("### 🔗 Resources")
    st.markdown("- [Python.org](https://python.org)\n- [W3Schools](https://w3schools.com)\n- [Code.org](https://code.org)")
    
    st.divider()
    st.caption("v2.0 | Advanced LMS System")

# ================== GURU INTERFACE ==================
if st.session_state.role == "👩‍🏫 Guru":
    st.header("👩‍🏫 Dashboard Guru")
    
    # Password protection
    guru_password = st.text_input("🔒 Password Guru", type="password", key="guru_pass")
    
    if guru_password != "admin123":
        st.warning("⚠️ Masukkan password guru untuk melanjutkan")
        st.info("💡 Password default: `admin123`")
        st.stop()
    
    st.success("✅ Login berhasil!")
    
    # Tabs untuk guru
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Kelola Modul", "📤 Upload Soal", "📊 Hasil Siswa", "📈 Statistik"])
    
    # TAB 1: KELOLA MODUL
    with tab1:
        st.subheader("📚 Manajemen Modul")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Modul yang Tersedia")
            modules = get_all_modules()
            
            if not modules:
                st.info("Belum ada modul. Buat modul baru di bawah!")
            else:
                for idx, mod in enumerate(modules):
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        st.write(f"**{idx+1}. {mod}**")
                        questions = load_module(mod)
                        st.caption(f"📝 {len(questions)} soal")
                    with col_b:
                        if st.button("👁️ Lihat", key=f"view_{mod}"):
                            with st.expander(f"Soal di {mod}", expanded=True):
                                for i, q in enumerate(questions, 1):
                                    st.markdown(f"**Q{i}:** {q['question']}")
                                    st.write(f"✅ Jawaban: {q['answer']}")
                                    st.caption(f"💡 {q['explanation']}")
                                    st.divider()
                    with col_c:
                        if st.button("🗑️", key=f"del_{mod}"):
                            os.remove(f"{MODUL_DIR}/{mod}.json")
                            st.success(f"Modul '{mod}' dihapus!")
                            st.rerun()
        
        with col2:
            st.markdown("#### Buat Modul Baru")
            new_module_name = st.text_input("Nama Modul Baru", placeholder="contoh: Python Dasar")
            
            if st.button("➕ Buat Modul"):
                if new_module_name:
                    save_module(new_module_name, [])
                    st.success(f"✅ Modul '{new_module_name}' berhasil dibuat!")
                    st.rerun()
                else:
                    st.error("Nama modul tidak boleh kosong!")
    
    # TAB 2: UPLOAD SOAL
    with tab2:
        st.subheader("📤 Upload/Tambah Soal")
        
        modules = get_all_modules()
        if not modules:
            st.warning("⚠️ Buat modul terlebih dahulu di tab 'Kelola Modul'")
        else:
            selected_module = st.selectbox("Pilih Modul", modules, key="upload_module")
            
            st.markdown("---")
            st.markdown("#### Method 1: Manual Input")
            
            with st.form("manual_question_form"):
                question = st.text_area("❓ Pertanyaan", placeholder="Apa fungsi print() di Python?")
                
                col1, col2 = st.columns(2)
                with col1:
                    option_a = st.text_input("A.", placeholder="Menampilkan output")
                    option_b = st.text_input("B.", placeholder="Menghitung angka")
                with col2:
                    option_c = st.text_input("C.", placeholder="Menyimpan data")
                    option_d = st.text_input("D.", placeholder="Menghapus variabel")
                
                correct_answer = st.selectbox("✅ Jawaban yang Benar", [option_a, option_b, option_c, option_d])
                explanation = st.text_area("💡 Penjelasan", placeholder="print() digunakan untuk menampilkan output ke layar")
                
                submit_btn = st.form_submit_button("💾 Simpan Soal")
                
                if submit_btn:
                    if question and all([option_a, option_b, option_c, option_d]) and explanation:
                        # Load existing questions
                        existing_questions = load_module(selected_module)
                        
                        # Add new question
                        new_question = {
                            "question": question,
                            "options": [option_a, option_b, option_c, option_d],
                            "answer": correct_answer,
                            "explanation": explanation
                        }
                        existing_questions.append(new_question)
                        
                        # Save
                        save_module(selected_module, existing_questions)
                        st.success(f"✅ Soal berhasil ditambahkan ke '{selected_module}'!")
                        st.rerun()
                    else:
                        st.error("❌ Semua field wajib diisi!")
            
            st.markdown("---")
            st.markdown("#### Method 2: Upload JSON")
            
            st.info("""
            **Format JSON yang benar:**
            ```json
            [
                {
                    "question": "Apa itu variabel?",
                    "options": ["Tempat menyimpan data", "Fungsi", "Loop", "Kondisi"],
                    "answer": "Tempat menyimpan data",
                    "explanation": "Variabel adalah wadah untuk menyimpan data"
                }
            ]
            ```
            """)
            
            uploaded_file = st.file_uploader("Upload file JSON", type=['json'], key="json_uploader")
            
            if uploaded_file:
                try:
                    json_data = json.load(uploaded_file)
                    
                    # Validate structure
                    if isinstance(json_data, list):
                        st.success(f"✅ File valid! Ditemukan {len(json_data)} soal")
                        
                        if st.button("📥 Import ke Modul"):
                            existing = load_module(selected_module)
                            existing.extend(json_data)
                            save_module(selected_module, existing)
                            st.success(f"✅ {len(json_data)} soal berhasil diimport!")
                            st.rerun()
                    else:
                        st.error("Format JSON salah! Harus berupa array/list")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # TAB 3: HASIL SISWA
    with tab3:
        st.subheader("📊 Hasil Ujian Semua Siswa")
        
        all_results = get_all_student_results()
        
        if not all_results:
            st.info("Belum ada siswa yang mengerjakan ujian")
        else:
            # Filter
            col1, col2 = st.columns(2)
            with col1:
                filter_module = st.selectbox("Filter by Modul", ["Semua"] + get_all_modules(), key="filter_mod")
            with col2:
                sort_by = st.selectbox("Urutkan by", ["Terbaru", "Nilai Tertinggi", "Nilai Terendah"])
            
            # Filter data
            filtered_results = all_results
            if filter_module != "Semua":
                filtered_results = [r for r in all_results if r['module'] == filter_module]
            
            # Sort
            if sort_by == "Nilai Tertinggi":
                filtered_results.sort(key=lambda x: x['score'], reverse=True)
            elif sort_by == "Nilai Terendah":
                filtered_results.sort(key=lambda x: x['score'])
            else:
                filtered_results.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Display
            for result in filtered_results:
                with st.expander(f"👦 {result['name']} | {result['student_id']} | {result['module']} | Nilai: {result['score']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nilai", f"{result['score']}/100")
                    with col2:
                        st.metric("Benar", f"{sum(1 for d in result['details'] if d['is_correct'])}/{len(result['details'])}")
                    with col3:
                        timestamp = datetime.fromisoformat(result['timestamp'])
                        st.write(f"**Waktu:**\n{timestamp.strftime('%d/%m/%Y %H:%M')}")
                    
                    st.markdown("##### Detail Jawaban:")
                    for i, detail in enumerate(result['details'], 1):
                        status_icon = "✅" if detail['is_correct'] else "❌"
                        st.markdown(f"{status_icon} **Q{i}:** {detail['question']}")
                        st.write(f"Jawaban siswa: {detail['user_answer']}")
                        if not detail['is_correct']:
                            st.write(f"Jawaban benar: {detail['correct_answer']}")
                        st.caption(f"💡 {detail['explanation']}")
                        st.divider()
                    
                    # Download PDF
                    pdf_bytes = create_pdf_report(
                        result['name'],
                        result['student_id'],
                        result['module'],
                        result['score'],
                        result['details']
                    )
                    st.download_button(
                        "📄 Download PDF Report",
                        pdf_bytes,
                        f"Report_{result['student_id']}_{result['module']}.pdf",
                        key=f"pdf_{result['student_id']}_{result['module']}"
                    )
    
    # TAB 4: STATISTIK
    with tab4:
        st.subheader("📈 Statistik Kelas")
        
        all_results = get_all_student_results()
        
        if not all_results:
            st.info("Belum ada data untuk statistik")
        else:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Ujian", len(all_results))
            with col2:
                unique_students = len(set(r['student_id'] for r in all_results))
                st.metric("Total Siswa", unique_students)
            with col3:
                avg_score = sum(r['score'] for r in all_results) / len(all_results)
                st.metric("Rata-rata Nilai", f"{avg_score:.1f}")
            with col4:
                passing = sum(1 for r in all_results if r['score'] >= 60)
                passing_rate = (passing / len(all_results)) * 100
                st.metric("Tingkat Kelulusan", f"{passing_rate:.1f}%")
            
            # Charts
            st.markdown("---")
            
            # Score distribution
            import plotly.express as px
            import plotly.graph_objects as go
            
            scores = [r['score'] for r in all_results]
            fig = px.histogram(
                x=scores,
                nbins=10,
                title="Distribusi Nilai",
                labels={'x': 'Nilai', 'y': 'Jumlah Siswa'},
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Per module statistics
            st.markdown("##### Statistik per Modul")
            module_stats = {}
            for r in all_results:
                mod = r['module']
                if mod not in module_stats:
                    module_stats[mod] = []
                module_stats[mod].append(r['score'])
            
            for mod, scores in module_stats.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{mod}**")
                with col2:
                    st.metric("Rata-rata", f"{sum(scores)/len(scores):.1f}")
                with col3:
                    st.metric("Jumlah", len(scores))

# ================== SISWA INTERFACE ==================
elif st.session_state.role == "👦 Siswa":
    st.header("👦 Portal Siswa")
    
    # Student login
    if not st.session_state.student_id:
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("📝 Nama Lengkap", placeholder="Nama Anda")
        with col2:
            student_id = st.text_input("🆔 ID Siswa", placeholder="Contoh: SIS001")
        
        if st.button("🚀 Masuk", type="primary"):
            if student_name and student_id:
                st.session_state.student_id = student_id
                st.session_state.student_name = student_name
                st.success(f"Selamat datang, {student_name}!")
                st.rerun()
            else:
                st.error("Nama dan ID wajib diisi!")
        st.stop()
    
    # Student logged in
    st.success(f"👋 Halo, **{st.session_state.student_name}**! (ID: {st.session_state.student_id})")
    
    # Tabs untuk siswa
    tab1, tab2 = st.tabs(["📝 Kerjakan Quiz", "📊 Hasil Saya"])
    
    # TAB 1: KERJAKAN QUIZ
    with tab1:
        st.subheader("📝 Pilih Quiz")
        
        modules = get_all_modules()
        if not modules:
            st.warning("Belum ada modul tersedia. Hubungi guru Anda!")
            st.stop()
        
        # Show available modules
        st.markdown("#### Modul Tersedia:")
        
        for module in modules:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**📚 {module}**")
                questions = load_module(module)
                st.caption(f"{len(questions)} soal")
            
            with col2:
                # Check if already completed
                already_done = check_student_session(st.session_state.student_id, module)
                if already_done:
                    st.success("✅ Selesai")
                else:
                    st.info("❌ Belum")
            
            with col3:
                if already_done:
                    st.button("🔒 Locked", disabled=True, key=f"start_{module}")
                else:
                    if st.button("🚀 Mulai", key=f"start_{module}", type="primary"):
                        # Randomize questions
                        questions = load_module(module)
                        random.shuffle(questions)
                        
                        # Create session
                        questions_order = [q['question'] for q in questions]
                        create_student_session(st.session_state.student_id, module, questions_order)
                        
                        # Store in session state
                        st.session_state.current_quiz = {
                            'module': module,
                            'questions': questions,
                            'answers': {}
                        }
                        st.session_state.quiz_submitted = False
                        st.rerun()
        
        # Quiz interface
        if st.session_state.current_quiz and not st.session_state.quiz_submitted:
            st.markdown("---")
            st.markdown(f"### 📝 Quiz: {st.session_state.current_quiz['module']}")
            
            st.warning("⚠️ **PERHATIAN:** Setiap modul hanya bisa dikerjakan 1 kali! Pastikan jawaban Anda sudah benar sebelum submit.")
            
            questions = st.session_state.current_quiz['questions']
            
            # Answer form
            with st.form("quiz_form"):
                for i, q in enumerate(questions):
                    st.markdown(f"**Soal {i+1}:**")
                    st.write(q['question'])
                    
                    answer = st.radio(
                        "Pilih jawaban:",
                        q['options'],
                        key=f"q_{i}",
                        index=None
                    )
                    
                    if answer:
                        st.session_state.current_quiz['answers'][i] = answer
                    
                    st.divider()
                
                submitted = st.form_submit_button("✅ Submit Jawaban", type="primary")
                
                if submitted:
                    # Check if all answered
                    if len(st.session_state.current_quiz['answers']) != len(questions):
                        st.error("❌ Jawab semua soal terlebih dahulu!")
                    else:
                        # Calculate score
                        correct = 0
                        details = []
                        
                        for i, q in enumerate(questions):
                            user_ans = st.session_state.current_quiz['answers'][i]
                            is_correct = user_ans == q['answer']
                            
                            if is_correct:
                                correct += 1
                            
                            details.append({
                                'question': q['question'],
                                'user_answer': user_ans,
                                'correct_answer': q['answer'],
                                'is_correct': is_correct,
                                'explanation': q['explanation']
                            })
                        
                        score = int((correct / len(questions)) * 100)
                        
                        # Save result
                        save_student_result(
                            st.session_state.student_id,
                            st.session_state.student_name,
                            st.session_state.current_quiz['module'],
                            score,
                            details
                        )
                        
                        # Complete session
                        complete_student_session(
                            st.session_state.student_id,
                            st.session_state.current_quiz['module']
                        )
                        
                        # Generate PDF
                        pdf_bytes = create_pdf_report(
                            st.session_state.student_name,
                            st.session_state.student_id,
                            st.session_state.current_quiz['module'],
                            score,
                            details
                        )
                        
                        # Save PDF
                        pdf_filename = f"{REPORT_DIR}/{st.session_state.student_id}_{st.session_state.current_quiz['module']}.pdf"
                        with open(pdf_filename, "wb") as f:
                            f.write(pdf_bytes)
                        
                        # Mark as submitted
                        st.session_state.quiz_submitted = True
                        st.session_state.last_result = {
                            'score': score,
                            'details': details,
                            'pdf': pdf_bytes
                        }
                        
                        st.rerun()
        
        # Show result after submission
        if st.session_state.quiz_submitted and 'last_result' in st.session_state:
            st.markdown("---")
            st.success("🎉 Quiz berhasil disubmit!")
            
            result = st.session_state.last_result
            
            # Score display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Nilai Anda", f"{result['score']}/100")
            with col2:
                correct_count = sum(1 for d in result['details'] if d['is_correct'])
                st.metric("✅ Jawaban Benar", f"{correct_count}/{len(result['details'])}")
            with col3:
                if result['score'] >= 80:
                    st.success("LUAR BIASA! 🌟")
                elif result['score'] >= 60:
                    st.info("BAGUS! 👍")
                else:
                    st.warning("SEMANGAT BELAJAR! 💪")
            
            # Download PDF
            st.download_button(
                "📄 Download Laporan PDF",
                result['pdf'],
                f"Laporan_{st.session_state.student_id}.pdf",
                mime="application/pdf"
            )
            
            # Show review
            st.markdown("---")
            st.markdown("### 💡 Review & Pembahasan")
            
            for i, detail in enumerate(result['details'], 1):
                if detail['is_correct']:
                    st.success(f"**Soal {i}: ✅ BENAR**")
                else:
                    st.error(f"**Soal {i}: ❌ SALAH**")
                
                st.write(f"**Pertanyaan:** {detail['question']}")
                st.write(f"**Jawaban Anda:** {detail['user_answer']}")
                
                if not detail['is_correct']:
                    st.write(f"**Jawaban Benar:** {detail['correct_answer']}")
                
                with st.expander("💡 Lihat Penjelasan"):
                    st.info(detail['explanation'])
                
                st.divider()
            
            # Button to continue
            if st.button("🔄 Kembali ke Daftar Quiz"):
                st.session_state.current_quiz = None
                st.session_state.quiz_submitted = False
                if 'last_result' in st.session_state:
                    del st.session_state.last_result
                st.rerun()
    
    # TAB 2: HASIL SAYA
    with tab2:
        st.subheader("📊 Riwayat Hasil Saya")
        
        my_results = get_student_results(st.session_state.student_id)
        
        if not my_results:
            st.info("Anda belum mengerjakan quiz apapun")
        else:
            # Summary
            total_quizzes = len(my_results)
            avg_score = sum(r['score'] for r in my_results) / total_quizzes
            best_score = max(r['score'] for r in my_results)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Quiz", total_quizzes)
            with col2:
                st.metric("Rata-rata Nilai", f"{avg_score:.1f}")
            with col3:
                st.metric("Nilai Terbaik", best_score)
            
            st.markdown("---")
            
            # List of results
            for result in sorted(my_results, key=lambda x: x['timestamp'], reverse=True):
                timestamp = datetime.fromisoformat(result['timestamp'])
                
                with st.expander(f"📚 {result['module']} | Nilai: {result['score']} | {timestamp.strftime('%d/%m/%Y %H:%M')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Nilai", f"{result['score']}/100")
                    with col2:
                        correct = sum(1 for d in result['details'] if d['is_correct'])
                        st.metric("Benar", f"{correct}/{len(result['details'])}")
                    
                    st.markdown("#### 💡 Pembahasan Soal")
                    
                    for i, detail in enumerate(result['details'], 1):
                        status_icon = "✅" if detail['is_correct'] else "❌"
                        status_color = "green" if detail['is_correct'] else "red"
                        
                        st.markdown(f"**{status_icon} Soal {i}:** {detail['question']}")
                        st.write(f"Jawaban Anda: {detail['user_answer']}")
                        
                        if not detail['is_correct']:
                            st.write(f"**Jawaban Benar:** :green[{detail['correct_answer']}]")
                        
                        with st.expander("💡 Penjelasan"):
                            st.info(detail['explanation'])
                        
                        st.divider()
                    
                    # Download individual report
                    pdf_file = f"{REPORT_DIR}/{st.session_state.student_id}_{result['module']}.pdf"
                    if os.path.exists(pdf_file):
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                "📄 Download PDF",
                                f.read(),
                                f"Laporan_{result['module']}.pdf",
                                key=f"download_{result['module']}"
                            )

# ================== INFO PAGE ==================
else:
    st.info("👆 Silakan pilih role (Siswa atau Guru) untuk melanjutkan")
    
    st.markdown("---")
    st.markdown("## 🌟 Fitur Lengkap Mini LMS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👦 Untuk Siswa:
        - ✅ Login dengan ID unik
        - 📝 Kerjakan quiz dengan soal acak
        - 🔒 Anti-contek: Soal berbeda urutan
        - 📊 Lihat hasil dan nilai
        - 💡 Review pembahasan soal
        - 📄 Download laporan PDF
        - 🚫 1 modul = 1x pengerjaan only
        """)
    
    with col2:
        st.markdown("""
        ### 👩‍🏫 Untuk Guru:
        - ➕ Buat dan kelola modul
        - 📤 Upload soal (manual/JSON)
        - 📊 Lihat hasil semua siswa
        - 📈 Statistik kelas lengkap
        - 📄 Download laporan per siswa
        - 👁️ Review detail jawaban siswa
        - 🗑️ Hapus modul
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🔐 Anti-Contek System:
    1. **Soal Acak**: Setiap siswa dapat urutan soal berbeda
    2. **Session Lock**: Siswa hanya bisa mengerjakan 1x per modul
    3. **Individual Report**: Hasil tersimpan terpisah per siswa
    4. **Review Terkontrol**: Pembahasan hanya muncul setelah submit
    """)
    
    st.markdown("---")
    st.code("""
# Contoh format JSON untuk upload soal:
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
    }
]
    """, language="json")

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Advanced Mini LMS v2.0</strong> | Sistem Pembelajaran Koding untuk Anak</p>
        <p>Built with ❤️ using Streamlit & Python 🐍</p>
    </div>
    """, unsafe_allow_html=True)