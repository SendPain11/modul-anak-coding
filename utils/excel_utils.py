# ==========================================================
# excel_utils.py - Export hasil ujian siswa ke file Excel (.xlsx)
# ==========================================================
from io import BytesIO
from datetime import datetime
import pandas as pd


def export_results_to_excel(results):
    """
    results: list of dict hasil siswa (dari storage.get_all_student_results())
    Return: BytesIO berisi file .xlsx dengan 2 sheet:
      - Ringkasan: 1 baris per siswa per modul
      - Detail Jawaban: 1 baris per soal
    """
    ringkasan_rows = []
    detail_rows = []

    for r in results:
        ringkasan_rows.append({
            "Nama": r.get("name"),
            "ID Siswa": r.get("student_id"),
            "Email": r.get("email") or "-",
            "Modul": r.get("module"),
            "Nilai": r.get("score"),
            "Status": r.get("status", "Selesai"),
            "Waktu Submit": r.get("timestamp"),
        })
        for i, d in enumerate(r.get("details", []), 1):
            detail_rows.append({
                "Nama": r.get("name"),
                "ID Siswa": r.get("student_id"),
                "Modul": r.get("module"),
                "No Soal": i,
                "Tipe": d.get("type", "single"),
                "Pertanyaan": d.get("question"),
                "Jawaban Siswa": ", ".join(d["user_answer"]) if isinstance(d.get("user_answer"), list) else d.get("user_answer"),
                "Jawaban Benar": ", ".join(d["correct_answer"]) if isinstance(d.get("correct_answer"), list) else d.get("correct_answer"),
                "Skor Soal": d.get("score"),
                "Benar?": d.get("is_correct"),
            })

    df_ringkasan = pd.DataFrame(ringkasan_rows)
    df_detail = pd.DataFrame(detail_rows)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        (df_ringkasan if not df_ringkasan.empty else pd.DataFrame([{"Info": "Belum ada data"}])).to_excel(
            writer, sheet_name="Ringkasan", index=False
        )
        (df_detail if not df_detail.empty else pd.DataFrame([{"Info": "Belum ada data"}])).to_excel(
            writer, sheet_name="Detail Jawaban", index=False
        )
    buffer.seek(0)
    return buffer


def excel_filename():
    return f"Hasil_Ujian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
