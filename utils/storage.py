# ==========================================================
# storage.py - Semua fungsi baca/tulis data (modul, soal,
# session, hasil, config) untuk Advanced Mini LMS v2
# ==========================================================
import os
import json
import shutil
from datetime import datetime

REPORT_DIR = "reports"
CERT_DIR = "certificates"
DATA_DIR = "data"
MODUL_DIR = "modules"
SESSION_DIR = "sessions"
CONFIG_DIR = "config"
BACKUP_DIR = "backups"

ALL_DIRS = [REPORT_DIR, CERT_DIR, DATA_DIR, MODUL_DIR, SESSION_DIR, CONFIG_DIR, BACKUP_DIR]


def ensure_dirs():
    for d in ALL_DIRS:
        os.makedirs(d, exist_ok=True)


# ================== MODUL & SOAL ==================

def default_module_meta():
    return {
        "time_limit_minutes": 0,   # 0 = tanpa batas waktu
        "passing_grade": 60,
        "created_at": datetime.now().isoformat(),
    }


def module_path(module_name):
    return f"{MODUL_DIR}/{module_name}.json"


def meta_path(module_name):
    return f"{MODUL_DIR}/{module_name}.meta.json"


def save_module(module_name, questions):
    """Simpan soal-soal modul (list of question dict)."""
    with open(module_path(module_name), "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    # Buat meta default kalau belum ada
    if not os.path.exists(meta_path(module_name)):
        save_module_meta(module_name, default_module_meta())


def load_module(module_name):
    path = module_path(module_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_module_meta(module_name, meta):
    with open(meta_path(module_name), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def load_module_meta(module_name):
    path = meta_path(module_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_module_meta()


def get_all_modules():
    if not os.path.exists(MODUL_DIR):
        return []
    files = [
        f.replace(".json", "") for f in os.listdir(MODUL_DIR)
        if f.endswith(".json") and not f.endswith(".meta.json")
    ]
    return sorted(files)


def delete_module(module_name):
    if os.path.exists(module_path(module_name)):
        os.remove(module_path(module_name))
    if os.path.exists(meta_path(module_name)):
        os.remove(meta_path(module_name))


# Normalisasi tipe soal lama (tanpa field "type") -> dianggap "single"
def normalize_question(q):
    q = dict(q)
    if "type" not in q:
        q["type"] = "single"
    if q["type"] == "multiple" and not isinstance(q.get("answer"), list):
        q["answer"] = [q.get("answer")] if q.get("answer") else []
    return q


# ================== SESSION (ANTI-CONTEK) ==================

def session_path(student_id, module_name):
    return f"{SESSION_DIR}/{student_id}_{module_name}.json"


def check_student_session(student_id, module_name):
    return os.path.exists(session_path(student_id, module_name))


def create_student_session(student_id, module_name, questions_order, start_time=None):
    data = {
        "student_id": student_id,
        "module": module_name,
        "questions_order": questions_order,
        "timestamp": datetime.now().isoformat(),
        "start_time": (start_time or datetime.now()).isoformat(),
        "completed": False,
    }
    with open(session_path(student_id, module_name), "w") as f:
        json.dump(data, f, indent=2)


def load_student_session(student_id, module_name):
    path = session_path(student_id, module_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def complete_student_session(student_id, module_name):
    path = session_path(student_id, module_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        data["completed"] = True
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def reset_student_session(student_id, module_name):
    """Hapus session + hasil supaya siswa bisa mengulang (dipakai guru)."""
    sp = session_path(student_id, module_name)
    rp = result_path(student_id, module_name)
    if os.path.exists(sp):
        os.remove(sp)
    if os.path.exists(rp):
        os.remove(rp)


# ================== HASIL SISWA ==================

def result_path(student_id, module_name):
    return f"{DATA_DIR}/{student_id}_{module_name}.json"


def save_student_result(student_id, name, module_name, score, details,
                         email=None, status="Selesai"):
    data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "module": module_name,
        "score": score,
        "details": details,
        "status": status,  # "Selesai" | "Menunggu Review"
        "timestamp": datetime.now().isoformat(),
    }
    with open(result_path(student_id, module_name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data


def get_student_results(student_id):
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    for filename in os.listdir(DATA_DIR):
        if filename.startswith(student_id + "_") and filename.endswith(".json"):
            with open(f"{DATA_DIR}/{filename}", "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results


def get_all_student_results():
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(f"{DATA_DIR}/{filename}", "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results


def get_leaderboard(module_name=None, top_n=10):
    """Ranking nilai tertinggi, opsional difilter per modul."""
    results = get_all_student_results()
    results = [r for r in results if r.get("status", "Selesai") == "Selesai"]
    if module_name and module_name != "Semua":
        results = [r for r in results if r["module"] == module_name]
    results.sort(key=lambda x: (-x["score"], x["timestamp"]))
    return results[:top_n]


# ================== KONFIGURASI (EMAIL, DLL) ==================

def config_path():
    return f"{CONFIG_DIR}/email_config.json"


def save_email_config(config):
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_email_config():
    if os.path.exists(config_path()):
        with open(config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "",
        "app_password": "",
        "enabled": False,
    }


# ================== BACKUP & RESTORE ==================

def create_backup_zip():
    """Zip semua folder data penting -> return path file zip."""
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{BACKUP_DIR}/backup_{ts}"
    staging = f"{BACKUP_DIR}/_staging_{ts}"
    os.makedirs(staging, exist_ok=True)
    for d in [MODUL_DIR, DATA_DIR, SESSION_DIR, REPORT_DIR, CERT_DIR, CONFIG_DIR]:
        if os.path.exists(d):
            shutil.copytree(d, f"{staging}/{d}", dirs_exist_ok=True)
    zip_path = shutil.make_archive(base_name, "zip", staging)
    shutil.rmtree(staging, ignore_errors=True)
    return zip_path


def restore_backup_zip(uploaded_file):
    """Extract zip upload ke folder-folder asal (merge/overwrite)."""
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_extract = f"{BACKUP_DIR}/_restore_{ts}"
    os.makedirs(tmp_extract, exist_ok=True)
    tmp_zip = f"{tmp_extract}.zip"
    with open(tmp_zip, "wb") as f:
        f.write(uploaded_file.getbuffer())
    shutil.unpack_archive(tmp_zip, tmp_extract, "zip")

    restored = []
    for d in [MODUL_DIR, DATA_DIR, SESSION_DIR, REPORT_DIR, CERT_DIR, CONFIG_DIR]:
        src = f"{tmp_extract}/{d}"
        if os.path.exists(src):
            shutil.copytree(src, d, dirs_exist_ok=True)
            restored.append(d)

    shutil.rmtree(tmp_extract, ignore_errors=True)
    os.remove(tmp_zip)
    return restored
