# ==========================================================
# scoring.py - Logika penilaian untuk 3 tipe soal:
# single (pilihan tunggal), multiple (pilihan ganda >1 jawaban),
# essay (dinilai manual oleh guru)
# ==========================================================


def grade_single(user_answer, correct_answer):
    is_correct = user_answer == correct_answer
    return (100 if is_correct else 0), is_correct


def grade_multiple(user_answers, correct_answers):
    """Partial credit: (benar_dipilih - salah_dipilih) / total_benar, min 0."""
    user_set = set(user_answers or [])
    correct_set = set(correct_answers or [])
    if not correct_set:
        return 0, False
    benar_dipilih = len(user_set & correct_set)
    salah_dipilih = len(user_set - correct_set)
    raw = (benar_dipilih - salah_dipilih) / len(correct_set)
    raw = max(0.0, min(1.0, raw))
    score = round(raw * 100)
    is_correct = user_set == correct_set
    return score, is_correct


def build_detail(q, user_answer):
    """Buat satu entri 'details' untuk satu soal, sesuai tipenya."""
    qtype = q.get("type", "single")

    if qtype == "single":
        score, is_correct = grade_single(user_answer, q.get("answer"))
        return {
            "type": "single",
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q.get("answer"),
            "is_correct": is_correct,
            "score": score,
            "explanation": q.get("explanation", ""),
            "needs_review": False,
        }

    if qtype == "multiple":
        score, is_correct = grade_multiple(user_answer, q.get("answer"))
        return {
            "type": "multiple",
            "question": q["question"],
            "user_answer": user_answer or [],
            "correct_answer": q.get("answer") or [],
            "is_correct": is_correct,
            "score": score,
            "explanation": q.get("explanation", ""),
            "needs_review": False,
        }

    # essay -> menunggu guru menilai manual
    return {
        "type": "essay",
        "question": q["question"],
        "user_answer": user_answer or "",
        "correct_answer": q.get("model_answer", q.get("answer", "")),
        "is_correct": None,
        "score": None,
        "explanation": q.get("explanation", ""),
        "needs_review": True,
    }


def compute_overall(details):
    """Hitung skor akhir (rata-rata tiap soal) & status submission."""
    if not details:
        return 0, "Selesai"

    pending = [d for d in details if d.get("needs_review")]
    graded = [d for d in details if not d.get("needs_review")]

    if pending:
        # Skor sementara hanya dari yang sudah otomatis ternilai
        partial = sum(d["score"] for d in graded) / len(details) if details else 0
        return round(partial), "Menunggu Review"

    total = sum(d["score"] for d in details) / len(details)
    return round(total), "Selesai"


def apply_essay_grades(details, essay_scores):
    """essay_scores: dict {index_soal: skor 0-100} dari guru.
    Mengembalikan (details_baru, skor_akhir, status_baru)."""
    new_details = []
    for i, d in enumerate(details):
        d = dict(d)
        if d.get("type") == "essay" and i in essay_scores:
            score = max(0, min(100, essay_scores[i]))
            d["score"] = score
            d["is_correct"] = score >= 60
            d["needs_review"] = False
        new_details.append(d)

    still_pending = any(d.get("needs_review") for d in new_details)
    final_score = round(sum(d["score"] for d in new_details) / len(new_details))
    status = "Menunggu Review" if still_pending else "Selesai"
    return new_details, final_score, status
