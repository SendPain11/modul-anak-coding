# ==========================================================
# ADVANCED MINI LMS KODING ANAK - v2.0
# ==========================================================
# FITUR BARU DI v2 (dari TODO README v1):
#  1. Multi-choice questions (pilih lebih dari 1 jawaban)
#  2. Essay questions (dinilai manual oleh guru)
#  3. Timer per quiz
#  4. Leaderboard
#  5. Certificate generator (PDF sertifikat kelulusan)
#  6. Email notifikasi ke siswa (SMTP, opsional/configurable)
#  7. Backup & restore database (zip semua data)
#  8. Export hasil ke Excel
#
# Dibangun di atas fitur v1: login role, soal random anti-contek,
# session lock 1x kerjakan, laporan PDF, statistik kelas.
# ==========================================================

import streamlit as st
import os
import random
from datetime import datetime

from utils import storage
from utils import scoring
from utils import pdf_utils
from utils import email_utils
from utils import excel_utils
from utils import timer_utils

# ================== KONFIG HALAMAN ==================
st.set_page_config(
    page_title="Advanced Mini LMS v2",
    page_icon="🎓",
    layout="wide",
)

storage.ensure_dirs()

# ================== SESSION STATE INIT ==================
defaults = {
    "role": None,
    "student_id": None,
    "student_name": None,
    "student_email": None,
    "current_quiz": None,
    "quiz_submitted": False,
    "quiz_start_time": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================== MAIN UI HEADER ==================
st.title("🎓 Advanced Mini LMS Koding Anak")
st.markdown("**v2.0 — Sistem Pembelajaran Koding Interaktif, Anti-Contek, & Lengkap!**")

col1, col2 = st.columns([3, 1])
with col1:
    st.session_state.role = st.selectbox(
        "🔐 Login sebagai:",
        ["Pilih Role...", "👦 Siswa", "👩‍🏫 Guru"],
        key="role_selector",
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
        - 📊 Hasil Saya
        - 🏆 Leaderboard
        """)
    elif st.session_state.role == "👩‍🏫 Guru":
        st.success("Mode: **Guru**")
        st.markdown("""
        **Menu Guru:**
        - ➕ Kelola Modul
        - 📤 Upload Soal
        - 📊 Hasil & Review Essay
        - 📈 Statistik & Leaderboard
        - ✉️ Pengaturan Email
        - 💾 Backup & Restore
        - 📥 Export Excel
        """)
    else:
        st.info("Silakan pilih role untuk melanjutkan")

    st.divider()
    st.markdown("### 🔗 Resources")
    st.markdown("- [Python.org](https://python.org)\n- [W3Schools](https://w3schools.com)\n- [Code.org](https://code.org)")
    st.divider()
    st.caption("v2.0 | Advanced LMS System")


# ==========================================================
# ================== GURU INTERFACE =======================
# ==========================================================
if st.session_state.role == "👩‍🏫 Guru":
    st.header("👩‍🏫 Dashboard Guru")

    guru_password = st.text_input("🔒 Password Guru", type="password", key="guru_pass")
    if guru_password != "admin123":
        st.warning("⚠️ Masukkan password guru untuk melanjutkan")
        st.info("💡 Password default: `admin123`")
        st.stop()

    st.success("✅ Login berhasil!")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "➕ Kelola Modul", "📤 Upload Soal", "📊 Hasil & Review",
        "📈 Statistik & Leaderboard", "✉️ Email", "💾 Backup/Restore", "📥 Export Excel",
    ])

    # ---------------- TAB 1: KELOLA MODUL ----------------
    with tab1:
        st.subheader("📚 Manajemen Modul")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### Modul yang Tersedia")
            modules = storage.get_all_modules()

            if not modules:
                st.info("Belum ada modul. Buat modul baru di samping!")
            else:
                for idx, mod in enumerate(modules):
                    meta = storage.load_module_meta(mod)
                    col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                    with col_a:
                        st.write(f"**{idx+1}. {mod}**")
                        questions = storage.load_module(mod)
                        timer_txt = f"⏱️ {meta['time_limit_minutes']} menit" if meta["time_limit_minutes"] else "⏱️ Tanpa batas"
                        st.caption(f"📝 {len(questions)} soal | {timer_txt} | 🎯 Passing: {meta['passing_grade']}")
                    with col_b:
                        if st.button("👁️ Lihat", key=f"view_{mod}"):
                            with st.expander(f"Soal di {mod}", expanded=True):
                                for i, q in enumerate(questions, 1):
                                    q = storage.normalize_question(q)
                                    st.markdown(f"**Q{i} [{q['type']}]:** {q['question']}")
                                    if q["type"] != "essay":
                                        st.write(f"✅ Jawaban: {q['answer']}")
                                    st.caption(f"💡 {q.get('explanation','')}")
                                    st.divider()
                    with col_c:
                        if st.button("⚙️ Setting", key=f"cfg_{mod}"):
                            st.session_state[f"show_cfg_{mod}"] = not st.session_state.get(f"show_cfg_{mod}", False)
                    with col_d:
                        if st.button("🗑️", key=f"del_{mod}"):
                            storage.delete_module(mod)
                            st.success(f"Modul '{mod}' dihapus!")
                            st.rerun()

                    if st.session_state.get(f"show_cfg_{mod}", False):
                        with st.container(border=True):
                            new_limit = st.number_input(
                                f"⏱️ Batas waktu (menit, 0=tanpa batas) — {mod}",
                                min_value=0, value=meta["time_limit_minutes"], key=f"limit_{mod}",
                            )
                            new_pass = st.number_input(
                                f"🎯 Passing grade — {mod}",
                                min_value=0, max_value=100, value=meta["passing_grade"], key=f"pass_{mod}",
                            )
                            if st.button("💾 Simpan Setting", key=f"save_cfg_{mod}"):
                                storage.save_module_meta(mod, {
                                    "time_limit_minutes": int(new_limit),
                                    "passing_grade": int(new_pass),
                                    "created_at": meta.get("created_at", datetime.now().isoformat()),
                                })
                                st.success("Setting disimpan!")
                                st.rerun()

        with col2:
            st.markdown("#### Buat Modul Baru")
            new_module_name = st.text_input("Nama Modul Baru", placeholder="contoh: Python Dasar")
            if st.button("➕ Buat Modul"):
                if new_module_name:
                    storage.save_module(new_module_name, [])
                    st.success(f"✅ Modul '{new_module_name}' berhasil dibuat!")
                    st.rerun()
                else:
                    st.error("Nama modul tidak boleh kosong!")

    # ---------------- TAB 2: UPLOAD SOAL ----------------
    with tab2:
        st.subheader("📤 Upload/Tambah Soal")
        modules = storage.get_all_modules()

        if not modules:
            st.warning("⚠️ Buat modul terlebih dahulu di tab 'Kelola Modul'")
        else:
            selected_module = st.selectbox("Pilih Modul", modules, key="upload_module")

            st.markdown("---")
            st.markdown("#### Method 1: Manual Input")

            question_type = st.radio(
                "Tipe Soal",
                ["single", "multiple", "essay"],
                format_func=lambda x: {
                    "single": "🔘 Pilihan Tunggal",
                    "multiple": "☑️ Pilihan Ganda (bisa >1 jawaban benar)",
                    "essay": "✍️ Essay (dinilai manual)",
                }[x],
                horizontal=True,
                key="qtype_radio",
            )

            with st.form("manual_question_form"):
                question = st.text_area("❓ Pertanyaan", placeholder="Apa fungsi print() di Python?")

                new_q = None

                if question_type in ("single", "multiple"):
                    col1, col2 = st.columns(2)
                    with col1:
                        option_a = st.text_input("A.", placeholder="Menampilkan output")
                        option_b = st.text_input("B.", placeholder="Menghitung angka")
                    with col2:
                        option_c = st.text_input("C.", placeholder="Menyimpan data")
                        option_d = st.text_input("D.", placeholder="Menghapus variabel")

                    options = [option_a, option_b, option_c, option_d]

                    if question_type == "single":
                        correct_answer = st.selectbox("✅ Jawaban yang Benar", options)
                    else:
                        correct_answer = st.multiselect("✅ Jawaban yang Benar (bisa pilih lebih dari 1)", options)

                    explanation = st.text_area("💡 Penjelasan", placeholder="print() digunakan untuk menampilkan output ke layar")
                    submit_btn = st.form_submit_button("💾 Simpan Soal")

                    if submit_btn:
                        opts_filled = all(options) if question_type == "single" else all(options)
                        ans_filled = bool(correct_answer) if question_type == "multiple" else bool(correct_answer)
                        if question and opts_filled and ans_filled and explanation:
                            existing_questions = storage.load_module(selected_module)
                            new_q = {
                                "type": question_type,
                                "question": question,
                                "options": options,
                                "answer": correct_answer,
                                "explanation": explanation,
                            }
                            existing_questions.append(new_q)
                            storage.save_module(selected_module, existing_questions)
                            st.success(f"✅ Soal berhasil ditambahkan ke '{selected_module}'!")
                            st.rerun()
                        else:
                            st.error("❌ Semua field wajib diisi, dan minimal 1 jawaban benar dipilih!")

                else:  # essay
                    model_answer = st.text_area("📝 Kunci Jawaban / Model Jawaban (referensi guru saat menilai)", placeholder="Jawaban ideal / poin-poin yang diharapkan")
                    explanation = st.text_area("💡 Penjelasan", placeholder="Penjelasan konsep untuk soal ini")
                    submit_btn = st.form_submit_button("💾 Simpan Soal")

                    if submit_btn:
                        if question and explanation:
                            existing_questions = storage.load_module(selected_module)
                            new_q = {
                                "type": "essay",
                                "question": question,
                                "model_answer": model_answer,
                                "explanation": explanation,
                            }
                            existing_questions.append(new_q)
                            storage.save_module(selected_module, existing_questions)
                            st.success(f"✅ Soal essay berhasil ditambahkan ke '{selected_module}'!")
                            st.rerun()
                        else:
                            st.error("❌ Pertanyaan dan penjelasan wajib diisi!")

            st.markdown("---")
            st.markdown("#### Method 2: Upload JSON")
            st.info("""
            **Format JSON (mendukung 3 tipe soal):**
            ```json
            [
                {
                    "type": "single",
                    "question": "Apa itu variabel?",
                    "options": ["Tempat menyimpan data", "Fungsi", "Loop", "Kondisi"],
                    "answer": "Tempat menyimpan data",
                    "explanation": "Variabel adalah wadah untuk menyimpan data"
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
            *Catatan: soal tanpa field `type` akan dianggap `single` (kompatibel dengan format v1 lama).*
            """)

            uploaded_file = st.file_uploader("Upload file JSON", type=["json"], key="json_uploader")
            if uploaded_file:
                try:
                    import json as _json
                    json_data = _json.load(uploaded_file)
                    if isinstance(json_data, list):
                        st.success(f"✅ File valid! Ditemukan {len(json_data)} soal")
                        if st.button("📥 Import ke Modul"):
                            existing = storage.load_module(selected_module)
                            existing.extend(json_data)
                            storage.save_module(selected_module, existing)
                            st.success(f"✅ {len(json_data)} soal berhasil diimport!")
                            st.rerun()
                    else:
                        st.error("Format JSON salah! Harus berupa array/list")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ---------------- TAB 3: HASIL & REVIEW ----------------
    with tab3:
        st.subheader("📊 Hasil Ujian & Review Soal Essay")
        all_results = storage.get_all_student_results()

        if not all_results:
            st.info("Belum ada siswa yang mengerjakan ujian")
        else:
            pending_count = sum(1 for r in all_results if r.get("status") == "Menunggu Review")
            if pending_count:
                st.warning(f"⚠️ Ada **{pending_count}** hasil yang menunggu penilaian soal essay!")

            col1, col2, col3 = st.columns(3)
            with col1:
                filter_module = st.selectbox("Filter by Modul", ["Semua"] + storage.get_all_modules(), key="filter_mod")
            with col2:
                filter_status = st.selectbox("Filter Status", ["Semua", "Selesai", "Menunggu Review"], key="filter_status")
            with col3:
                sort_by = st.selectbox("Urutkan by", ["Terbaru", "Nilai Tertinggi", "Nilai Terendah"])

            filtered_results = all_results
            if filter_module != "Semua":
                filtered_results = [r for r in filtered_results if r["module"] == filter_module]
            if filter_status != "Semua":
                filtered_results = [r for r in filtered_results if r.get("status", "Selesai") == filter_status]

            if sort_by == "Nilai Tertinggi":
                filtered_results.sort(key=lambda x: x["score"], reverse=True)
            elif sort_by == "Nilai Terendah":
                filtered_results.sort(key=lambda x: x["score"])
            else:
                filtered_results.sort(key=lambda x: x["timestamp"], reverse=True)

            email_config = storage.load_email_config()

            for result in filtered_results:
                status = result.get("status", "Selesai")
                status_icon = "🟡" if status == "Menunggu Review" else "🟢"
                header = f"{status_icon} {result['name']} | {result['student_id']} | {result['module']} | Nilai: {result['score']} | {status}"

                with st.expander(header):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nilai", f"{result['score']}/100")
                    with col2:
                        graded = [d for d in result["details"] if d.get("score") is not None]
                        benar = sum(1 for d in graded if d.get("is_correct"))
                        st.metric("Benar (auto)", f"{benar}/{len(graded)}")
                    with col3:
                        timestamp = datetime.fromisoformat(result["timestamp"])
                        st.write(f"**Waktu:**\n{timestamp.strftime('%d/%m/%Y %H:%M')}")

                    st.markdown("##### Detail Jawaban:")
                    essay_scores_input = {}
                    for i, detail in enumerate(result["details"]):
                        qtype = detail.get("type", "single")
                        st.markdown(f"**Q{i+1} [{qtype}]:** {detail['question']}")

                        if qtype == "essay":
                            st.write(f"**Jawaban Siswa:** {detail['user_answer'] or '_(kosong)_'}")
                            if detail.get("correct_answer"):
                                st.caption(f"📌 Kunci/Model jawaban guru: {detail['correct_answer']}")
                            if detail.get("needs_review"):
                                score_key = f"essay_{result['student_id']}_{result['module']}_{i}"
                                essay_scores_input[i] = st.slider(
                                    f"🎯 Beri nilai soal essay #{i+1} (0-100)",
                                    0, 100, 60, key=score_key,
                                )
                            else:
                                st.success(f"✅ Sudah dinilai: {detail['score']}/100")
                        else:
                            user_ans = detail["user_answer"]
                            correct_ans = detail["correct_answer"]
                            icon = "✅" if detail["is_correct"] else "❌"
                            st.write(f"{icon} Jawaban siswa: {', '.join(user_ans) if isinstance(user_ans, list) else user_ans}")
                            if not detail["is_correct"]:
                                st.write(f"Jawaban benar: {', '.join(correct_ans) if isinstance(correct_ans, list) else correct_ans}")
                            st.caption(f"Skor soal: {detail['score']}/100")

                        if detail.get("explanation"):
                            st.caption(f"💡 {detail['explanation']}")
                        st.divider()

                    if essay_scores_input:
                        if st.button("💾 Simpan Nilai Essay", key=f"save_essay_{result['student_id']}_{result['module']}"):
                            new_details, final_score, new_status = scoring.apply_essay_grades(
                                result["details"], essay_scores_input
                            )
                            storage.save_student_result(
                                result["student_id"], result["name"], result["module"],
                                final_score, new_details, email=result.get("email"), status=new_status,
                            )
                            st.success(f"✅ Nilai essay disimpan! Nilai akhir: {final_score}/100 ({new_status})")

                            # Regenerate & simpan ulang PDF laporan
                            pdf_bytes = pdf_utils.create_pdf_report(
                                result["name"], result["student_id"], result["module"],
                                final_score, new_details, status=new_status,
                            )
                            pdf_path = f"{storage.REPORT_DIR}/{result['student_id']}_{result['module']}.pdf"
                            with open(pdf_path, "wb") as f:
                                f.write(pdf_bytes)

                            # Auto kirim email kalau sudah final & fitur aktif
                            if new_status == "Selesai" and email_config.get("enabled") and result.get("email"):
                                ok, msg = email_utils.send_result_email(
                                    email_config, result["email"], result["name"], result["module"],
                                    final_score, new_status, pdf_bytes,
                                    pdf_filename=f"Laporan_{result['student_id']}.pdf",
                                )
                                st.info(f"📧 {msg}")
                            st.rerun()

                    # Download PDF laporan
                    pdf_bytes = pdf_utils.create_pdf_report(
                        result["name"], result["student_id"], result["module"],
                        result["score"], result["details"], status=status,
                    )
                    dl_col1, dl_col2, dl_col3 = st.columns(3)
                    with dl_col1:
                        st.download_button(
                            "📄 Download PDF Laporan", pdf_bytes,
                            f"Report_{result['student_id']}_{result['module']}.pdf",
                            key=f"pdf_{result['student_id']}_{result['module']}",
                        )
                    with dl_col2:
                        meta = storage.load_module_meta(result["module"])
                        if status == "Selesai" and result["score"] >= meta["passing_grade"]:
                            cert_bytes = pdf_utils.create_certificate(
                                result["name"], result["student_id"], result["module"],
                                result["score"], meta["passing_grade"],
                            )
                            st.download_button(
                                "🏆 Download Sertifikat", cert_bytes,
                                f"Sertifikat_{result['student_id']}_{result['module']}.pdf",
                                key=f"cert_{result['student_id']}_{result['module']}",
                            )
                        else:
                            st.caption("🏆 Sertifikat tersedia jika nilai ≥ passing grade")
                    with dl_col3:
                        if st.button("📧 Kirim Email", key=f"email_{result['student_id']}_{result['module']}"):
                            ok, msg = email_utils.send_result_email(
                                email_config, result.get("email"), result["name"], result["module"],
                                result["score"], status, pdf_bytes,
                                pdf_filename=f"Laporan_{result['student_id']}.pdf",
                            )
                            (st.success if ok else st.error)(msg)

                    if st.button("🔓 Reset Session Siswa (izinkan ulang)", key=f"resetsess_{result['student_id']}_{result['module']}"):
                        storage.reset_student_session(result["student_id"], result["module"])
                        st.success("Session direset. Siswa bisa mengerjakan modul ini lagi.")
                        st.rerun()

    # ---------------- TAB 4: STATISTIK & LEADERBOARD ----------------
    with tab4:
        st.subheader("📈 Statistik Kelas")
        all_results = storage.get_all_student_results()
        finished_results = [r for r in all_results if r.get("status", "Selesai") == "Selesai"]

        if not all_results:
            st.info("Belum ada data untuk statistik")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ujian", len(all_results))
            with col2:
                unique_students = len(set(r["student_id"] for r in all_results))
                st.metric("Total Siswa", unique_students)
            with col3:
                avg_score = sum(r["score"] for r in finished_results) / len(finished_results) if finished_results else 0
                st.metric("Rata-rata Nilai", f"{avg_score:.1f}")
            with col4:
                passing = sum(1 for r in finished_results if r["score"] >= 60)
                passing_rate = (passing / len(finished_results) * 100) if finished_results else 0
                st.metric("Tingkat Kelulusan", f"{passing_rate:.1f}%")

            st.markdown("---")
            try:
                import plotly.express as px
                scores = [r["score"] for r in finished_results]
                if scores:
                    fig = px.histogram(
                        x=scores, nbins=10, title="Distribusi Nilai",
                        labels={"x": "Nilai", "y": "Jumlah Siswa"},
                        color_discrete_sequence=["#667eea"],
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.caption("(Grafik distribusi butuh library plotly)")

            st.markdown("##### Statistik per Modul")
            module_stats = {}
            for r in finished_results:
                module_stats.setdefault(r["module"], []).append(r["score"])
            for mod, scores in module_stats.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{mod}**")
                with col2:
                    st.metric("Rata-rata", f"{sum(scores)/len(scores):.1f}")
                with col3:
                    st.metric("Jumlah", len(scores))

            st.markdown("---")
            st.markdown("### 🏆 Leaderboard")
            lb_module = st.selectbox("Modul", ["Semua"] + storage.get_all_modules(), key="guru_lb_module")
            leaderboard = storage.get_leaderboard(lb_module, top_n=20)
            if not leaderboard:
                st.info("Belum ada data leaderboard untuk modul ini.")
            else:
                medals = ["🥇", "🥈", "🥉"]
                for i, r in enumerate(leaderboard):
                    medal = medals[i] if i < 3 else f"#{i+1}"
                    st.write(f"{medal} **{r['name']}** ({r['student_id']}) — {r['module']} — **{r['score']}/100**")

    # ---------------- TAB 5: PENGATURAN EMAIL ----------------
    with tab5:
        st.subheader("✉️ Pengaturan Email Notifikasi")
        st.markdown("""
        Gunakan **Gmail App Password** (bukan password akun biasa):
        1. Aktifkan 2-Step Verification di akun Gmail pengirim
        2. Buat App Password di `myaccount.google.com/apppasswords`
        3. Masukkan App Password itu di form bawah ini
        """)

        cfg = storage.load_email_config()
        with st.form("email_config_form"):
            enabled = st.checkbox("Aktifkan pengiriman email otomatis", value=cfg.get("enabled", False))
            sender_email = st.text_input("Email Pengirim", value=cfg.get("sender_email", ""))
            app_password = st.text_input("App Password", value=cfg.get("app_password", ""), type="password")
            smtp_host = st.text_input("SMTP Host", value=cfg.get("smtp_host", "smtp.gmail.com"))
            smtp_port = st.number_input("SMTP Port", value=cfg.get("smtp_port", 587))

            saved = st.form_submit_button("💾 Simpan Konfigurasi")
            if saved:
                storage.save_email_config({
                    "enabled": enabled,
                    "sender_email": sender_email,
                    "app_password": app_password,
                    "smtp_host": smtp_host,
                    "smtp_port": int(smtp_port),
                })
                st.success("✅ Konfigurasi email disimpan!")

        st.markdown("---")
        test_email = st.text_input("Kirim email test ke:", placeholder="alamat@email.com")
        if st.button("📧 Kirim Email Test"):
            ok, msg = email_utils.send_test_email(storage.load_email_config(), test_email)
            (st.success if ok else st.error)(msg)

        st.caption("⚠️ Catatan: app password disimpan sebagai plain text di `config/email_config.json` "
                    "pada server ini — jangan gunakan password akun utama, dan jangan commit folder `config/` ke Git publik.")

    # ---------------- TAB 6: BACKUP & RESTORE ----------------
    with tab6:
        st.subheader("💾 Backup & Restore Database")

        st.markdown("#### 📦 Backup")
        st.write("Backup akan berisi semua modul, soal, hasil siswa, session, laporan PDF, dan konfigurasi email.")
        if st.button("📦 Buat Backup Sekarang"):
            zip_path = storage.create_backup_zip()
            with open(zip_path, "rb") as f:
                st.download_button(
                    "⬇️ Download File Backup (.zip)", f.read(),
                    file_name=os.path.basename(zip_path), mime="application/zip",
                )
            st.success(f"✅ Backup dibuat: {os.path.basename(zip_path)}")

        st.markdown("---")
        st.markdown("#### ♻️ Restore")
        st.warning("⚠️ Restore akan **menimpa/menggabungkan** data yang ada di folder modules, data, sessions, reports, config dengan isi backup. Pastikan file backup berasal dari sumber terpercaya.")
        restore_file = st.file_uploader("Upload file backup (.zip)", type=["zip"], key="restore_uploader")
        if restore_file and st.button("♻️ Restore Sekarang"):
            restored = storage.restore_backup_zip(restore_file)
            st.success(f"✅ Berhasil restore folder: {', '.join(restored) if restored else '(tidak ada)'}")
            st.rerun()

    # ---------------- TAB 7: EXPORT EXCEL ----------------
    with tab7:
        st.subheader("📥 Export Hasil ke Excel")
        all_results = storage.get_all_student_results()
        if not all_results:
            st.info("Belum ada data hasil siswa untuk diexport.")
        else:
            st.write(f"Total data: **{len(all_results)}** hasil ujian dari **{len(set(r['student_id'] for r in all_results))}** siswa.")
            buffer = excel_utils.export_results_to_excel(all_results)
            st.download_button(
                "📥 Download Excel (.xlsx)", buffer,
                file_name=excel_utils.excel_filename(),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.caption("File berisi 2 sheet: **Ringkasan** (nilai per siswa) dan **Detail Jawaban** (per soal).")

# ==========================================================
# ================== SISWA INTERFACE ======================
# ==========================================================
elif st.session_state.role == "👦 Siswa":
    st.header("👦 Portal Siswa")

    # ---------- LOGIN SISWA ----------
    if not st.session_state.student_id:
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("📝 Nama Lengkap", placeholder="Nama Anda")
            student_email = st.text_input("📧 Email (opsional, untuk notifikasi hasil)", placeholder="nama@email.com")
        with col2:
            student_id = st.text_input("🆔 ID Siswa", placeholder="Contoh: SIS001")

        if st.button("🚀 Masuk", type="primary"):
            if student_name and student_id:
                st.session_state.student_id = student_id
                st.session_state.student_name = student_name
                st.session_state.student_email = student_email or None
                st.success(f"Selamat datang, {student_name}!")
                st.rerun()
            else:
                st.error("Nama dan ID wajib diisi!")
        st.stop()

    st.success(f"👋 Halo, **{st.session_state.student_name}**! (ID: {st.session_state.student_id})")

    tab1, tab2, tab3 = st.tabs(["📝 Kerjakan Quiz", "📊 Hasil Saya", "🏆 Leaderboard"])

    # ---------------- TAB 1: KERJAKAN QUIZ ----------------
    with tab1:
        st.subheader("📝 Pilih Quiz")
        modules = storage.get_all_modules()
        if not modules:
            st.warning("Belum ada modul tersedia. Hubungi guru Anda!")
            st.stop()

        st.markdown("#### Modul Tersedia:")
        for module in modules:
            meta = storage.load_module_meta(module)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**📚 {module}**")
                questions = storage.load_module(module)
                timer_txt = f"⏱️ {meta['time_limit_minutes']} menit" if meta["time_limit_minutes"] else "⏱️ Tanpa batas waktu"
                st.caption(f"{len(questions)} soal | {timer_txt}")
            with col2:
                already_done = storage.check_student_session(st.session_state.student_id, module)
                if already_done:
                    st.success("✅ Selesai")
                else:
                    st.info("❌ Belum")
            with col3:
                if already_done:
                    st.button("🔒 Locked", disabled=True, key=f"start_{module}")
                else:
                    if st.button("🚀 Mulai", key=f"start_{module}", type="primary"):
                        questions = [storage.normalize_question(q) for q in storage.load_module(module)]
                        random.shuffle(questions)
                        questions_order = [q["question"] for q in questions]
                        start_time = datetime.now()
                        storage.create_student_session(st.session_state.student_id, module, questions_order, start_time)
                        st.session_state.current_quiz = {
                            "module": module, "questions": questions, "answers": {},
                            "time_limit": meta["time_limit_minutes"],
                        }
                        st.session_state.quiz_start_time = start_time.isoformat()
                        st.session_state.quiz_submitted = False
                        st.rerun()

        # ---------- QUIZ INTERFACE ----------
        if st.session_state.current_quiz and not st.session_state.quiz_submitted:
            st.markdown("---")
            quiz = st.session_state.current_quiz
            st.markdown(f"### 📝 Quiz: {quiz['module']}")
            st.warning("⚠️ **PERHATIAN:** Setiap modul hanya bisa dikerjakan 1 kali! Pastikan jawaban Anda sudah benar sebelum submit.")

            remaining = timer_utils.time_remaining_seconds(st.session_state.quiz_start_time, quiz.get("time_limit", 0))
            time_up = remaining is not None and remaining <= 0
            if remaining is not None:
                timer_utils.render_countdown_widget(remaining, key="quiz")
                if time_up:
                    st.error("⏰ Waktu habis! Jawaban akan otomatis disubmit dengan apa yang sudah terisi.")

            questions = quiz["questions"]

            with st.form("quiz_form"):
                for i, q in enumerate(questions):
                    st.markdown(f"**Soal {i+1} [{q['type']}]:**")
                    st.write(q["question"])

                    if q["type"] == "single":
                        answer = st.radio("Pilih jawaban:", q["options"], key=f"q_{i}", index=None)
                    elif q["type"] == "multiple":
                        st.caption("☑️ Bisa pilih lebih dari 1 jawaban")
                        answer = []
                        cols = st.columns(2)
                        for oi, opt in enumerate(q["options"]):
                            with cols[oi % 2]:
                                if st.checkbox(opt, key=f"q_{i}_opt_{oi}"):
                                    answer.append(opt)
                    else:  # essay
                        answer = st.text_area("✍️ Jawaban Anda:", key=f"q_{i}", height=100)

                    if answer:
                        quiz["answers"][i] = answer
                    st.divider()

                submitted = st.form_submit_button("✅ Submit Jawaban", type="primary")

                if submitted or time_up:
                    unanswered = [i for i, q in enumerate(questions) if i not in quiz["answers"] or quiz["answers"][i] in (None, [], "")]
                    if unanswered and not time_up:
                        st.error("❌ Jawab semua soal terlebih dahulu!")
                    else:
                        details = []
                        for i, q in enumerate(questions):
                            user_ans = quiz["answers"].get(i)
                            details.append(scoring.build_detail(q, user_ans))

                        score, status = scoring.compute_overall(details)

                        storage.save_student_result(
                            st.session_state.student_id, st.session_state.student_name,
                            quiz["module"], score, details,
                            email=st.session_state.student_email, status=status,
                        )
                        storage.complete_student_session(st.session_state.student_id, quiz["module"])

                        pdf_bytes = pdf_utils.create_pdf_report(
                            st.session_state.student_name, st.session_state.student_id,
                            quiz["module"], score, details, status=status,
                        )
                        pdf_filename = f"{storage.REPORT_DIR}/{st.session_state.student_id}_{quiz['module']}.pdf"
                        with open(pdf_filename, "wb") as f:
                            f.write(pdf_bytes)

                        # Kirim email kalau fitur aktif & sudah final
                        email_cfg = storage.load_email_config()
                        if email_cfg.get("enabled") and st.session_state.student_email:
                            email_utils.send_result_email(
                                email_cfg, st.session_state.student_email,
                                st.session_state.student_name, quiz["module"], score, status,
                                pdf_bytes, pdf_filename=f"Laporan_{st.session_state.student_id}.pdf",
                            )

                        st.session_state.quiz_submitted = True
                        st.session_state.last_result = {"score": score, "details": details, "pdf": pdf_bytes, "status": status}
                        st.rerun()

        # ---------- HASIL SETELAH SUBMIT ----------
        if st.session_state.quiz_submitted and "last_result" in st.session_state:
            st.markdown("---")
            st.success("🎉 Quiz berhasil disubmit!")
            result = st.session_state.last_result

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Nilai Anda", f"{result['score']}/100")
            with col2:
                graded = [d for d in result["details"] if d.get("score") is not None]
                correct_count = sum(1 for d in graded if d.get("is_correct"))
                st.metric("✅ Jawaban Benar (auto)", f"{correct_count}/{len(graded)}")
            with col3:
                if result["status"] == "Menunggu Review":
                    st.info("MENUNGGU REVIEW ESSAY ⏳")
                elif result["score"] >= 80:
                    st.success("LUAR BIASA! 🌟")
                elif result["score"] >= 60:
                    st.info("BAGUS! 👍")
                else:
                    st.warning("SEMANGAT BELAJAR! 💪")

            st.download_button(
                "📄 Download Laporan PDF", result["pdf"],
                f"Laporan_{st.session_state.student_id}.pdf", mime="application/pdf",
            )

            st.markdown("---")
            st.markdown("### 💡 Review & Pembahasan")
            for i, detail in enumerate(result["details"], 1):
                qtype = detail.get("type", "single")
                if qtype == "essay" and detail.get("needs_review"):
                    st.info(f"**Soal {i}: ⏳ MENUNGGU DINILAI GURU**")
                elif detail.get("is_correct"):
                    st.success(f"**Soal {i}: ✅ BENAR**")
                else:
                    st.error(f"**Soal {i}: ❌ SALAH / PERLU DIPERBAIKI**")

                st.write(f"**Pertanyaan:** {detail['question']}")
                ua = detail["user_answer"]
                st.write(f"**Jawaban Anda:** {', '.join(ua) if isinstance(ua, list) else ua}")

                if qtype != "essay" and not detail.get("is_correct"):
                    ca = detail["correct_answer"]
                    st.write(f"**Jawaban Benar:** {', '.join(ca) if isinstance(ca, list) else ca}")

                if detail.get("explanation"):
                    with st.expander("💡 Lihat Penjelasan"):
                        st.info(detail["explanation"])
                st.divider()

            if st.button("🔄 Kembali ke Daftar Quiz"):
                st.session_state.current_quiz = None
                st.session_state.quiz_submitted = False
                if "last_result" in st.session_state:
                    del st.session_state.last_result
                st.rerun()

    # ---------------- TAB 2: HASIL SAYA ----------------
    with tab2:
        st.subheader("📊 Riwayat Hasil Saya")
        my_results = storage.get_student_results(st.session_state.student_id)

        if not my_results:
            st.info("Anda belum mengerjakan quiz apapun")
        else:
            finished = [r for r in my_results if r.get("status", "Selesai") == "Selesai"]
            total_quizzes = len(my_results)
            avg_score = sum(r["score"] for r in finished) / len(finished) if finished else 0
            best_score = max((r["score"] for r in finished), default=0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Quiz", total_quizzes)
            with col2:
                st.metric("Rata-rata Nilai", f"{avg_score:.1f}")
            with col3:
                st.metric("Nilai Terbaik", best_score)

            st.markdown("---")
            for result in sorted(my_results, key=lambda x: x["timestamp"], reverse=True):
                timestamp = datetime.fromisoformat(result["timestamp"])
                status = result.get("status", "Selesai")
                status_icon = "🟡" if status == "Menunggu Review" else "🟢"
                with st.expander(f"📚 {result['module']} | Nilai: {result['score']} | {status_icon} {status} | {timestamp.strftime('%d/%m/%Y %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Nilai", f"{result['score']}/100")
                    with col2:
                        graded = [d for d in result["details"] if d.get("score") is not None]
                        correct = sum(1 for d in graded if d.get("is_correct"))
                        st.metric("Benar (auto)", f"{correct}/{len(graded)}")

                    st.markdown("#### 💡 Pembahasan Soal")
                    for i, detail in enumerate(result["details"], 1):
                        qtype = detail.get("type", "single")
                        if qtype == "essay" and detail.get("needs_review"):
                            status_icon2 = "⏳"
                        else:
                            status_icon2 = "✅" if detail.get("is_correct") else "❌"
                        st.markdown(f"**{status_icon2} Soal {i}:** {detail['question']}")
                        ua = detail["user_answer"]
                        st.write(f"Jawaban Anda: {', '.join(ua) if isinstance(ua, list) else ua}")
                        if qtype != "essay" and not detail.get("is_correct"):
                            ca = detail["correct_answer"]
                            st.write(f"**Jawaban Benar:** :green[{', '.join(ca) if isinstance(ca, list) else ca}]")
                        if detail.get("explanation"):
                            with st.expander("💡 Penjelasan"):
                                st.info(detail["explanation"])
                        st.divider()

                    dl_col1, dl_col2 = st.columns(2)
                    pdf_file = f"{storage.REPORT_DIR}/{st.session_state.student_id}_{result['module']}.pdf"
                    with dl_col1:
                        if os.path.exists(pdf_file):
                            with open(pdf_file, "rb") as f:
                                st.download_button(
                                    "📄 Download PDF", f.read(),
                                    f"Laporan_{result['module']}.pdf", key=f"download_{result['module']}",
                                )
                    with dl_col2:
                        meta = storage.load_module_meta(result["module"])
                        if status == "Selesai" and result["score"] >= meta["passing_grade"]:
                            cert_bytes = pdf_utils.create_certificate(
                                st.session_state.student_name, st.session_state.student_id,
                                result["module"], result["score"], meta["passing_grade"],
                            )
                            st.download_button(
                                "🏆 Download Sertifikat", cert_bytes,
                                f"Sertifikat_{result['module']}.pdf", key=f"cert_{result['module']}",
                            )

    # ---------------- TAB 3: LEADERBOARD ----------------
    with tab3:
        st.subheader("🏆 Leaderboard")
        lb_module = st.selectbox("Pilih Modul", ["Semua"] + storage.get_all_modules(), key="siswa_lb_module")
        leaderboard = storage.get_leaderboard(lb_module, top_n=20)
        if not leaderboard:
            st.info("Belum ada data leaderboard untuk modul ini.")
        else:
            medals = ["🥇", "🥈", "🥉"]
            for i, r in enumerate(leaderboard):
                medal = medals[i] if i < 3 else f"#{i+1}"
                is_me = r["student_id"] == st.session_state.student_id
                line = f"{medal} **{r['name']}** ({r['student_id']}) — {r['module']} — **{r['score']}/100**"
                if is_me:
                    st.success(line + "  ⭐ *(Anda)*")
                else:
                    st.write(line)

# ================== INFO PAGE (BELUM LOGIN) ==================
else:
    st.info("👆 Silakan pilih role (Siswa atau Guru) untuk melanjutkan")
    st.markdown("---")
    st.markdown("## 🌟 Fitur Lengkap Mini LMS v2.0")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 👦 Untuk Siswa:
        - ✅ Login dengan ID unik + email opsional
        - 📝 Quiz: pilihan tunggal, pilihan ganda, & essay
        - ⏱️ Timer per quiz (jika diaktifkan guru)
        - 🔒 Anti-contek: Soal acak, 1 modul = 1x pengerjaan
        - 📊 Lihat hasil, riwayat, dan pembahasan
        - 🏆 Leaderboard antar siswa
        - 📄 Download laporan PDF & 🎖️ Sertifikat kelulusan
        - 📧 Notifikasi hasil via email (jika diaktifkan)
        """)
    with col2:
        st.markdown("""
        ### 👩‍🏫 Untuk Guru:
        - ➕ Kelola modul (timer, passing grade)
        - 📤 Upload soal: manual/JSON, 3 tipe soal
        - 📊 Lihat hasil semua siswa & nilai essay manual
        - 📈 Statistik kelas & Leaderboard
        - 🎖️ Terbitkan sertifikat otomatis untuk yang lulus
        - 📧 Kirim notifikasi email ke siswa
        - 💾 Backup & restore seluruh database
        - 📥 Export semua hasil ke Excel
        """)

    st.markdown("---")
    st.markdown("""
    ### 🔐 Anti-Contek System:
    1. **Soal Acak**: Setiap siswa dapat urutan soal berbeda
    2. **Session Lock**: Siswa hanya bisa mengerjakan 1x per modul
    3. **Timer**: Batas waktu opsional per modul
    4. **Individual Report**: Hasil tersimpan terpisah per siswa
    5. **Review Terkontrol**: Pembahasan hanya muncul setelah submit
    """)

# ================== FOOTER ==================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Advanced Mini LMS v2.0</strong> | Sistem Pembelajaran Koding untuk Anak</p>
        <p>Built with ❤️ using Streamlit & Python 🐍</p>
    </div>
    """, unsafe_allow_html=True)
