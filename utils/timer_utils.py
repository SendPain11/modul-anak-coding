# ==========================================================
# timer_utils.py - Bantuan untuk timer per quiz
# ==========================================================
from datetime import datetime, timedelta
import streamlit.components.v1 as components


def time_remaining_seconds(start_time_iso, limit_minutes):
    """Return None jika tanpa limit, atau sisa detik (bisa negatif kalau habis)."""
    if not limit_minutes or limit_minutes <= 0:
        return None
    start = datetime.fromisoformat(start_time_iso)
    deadline = start + timedelta(minutes=limit_minutes)
    remaining = (deadline - datetime.now()).total_seconds()
    return remaining


def render_countdown_widget(remaining_seconds, key="timer"):
    """Tampilkan countdown visual (JS, client-side) - hanya visual,
    penegakan waktu tetap dicek di server saat submit."""
    if remaining_seconds is None:
        return
    total = max(0, int(remaining_seconds))
    html = f"""
    <div id="countdown_{key}" style="
        font-size: 28px; font-weight: bold; text-align:center;
        padding: 10px; border-radius: 10px; background:#fff3cd; color:#7a5b00;
        border: 2px solid #ffe08a; margin-bottom: 10px;">
        ⏱️ Sisa Waktu: <span id="time_{key}">--:--</span>
    </div>
    <script>
    let remaining_{key} = {total};
    function tick_{key}() {{
        if (remaining_{key} <= 0) {{
            document.getElementById("time_{key}").innerText = "00:00";
            return;
        }}
        let m = Math.floor(remaining_{key} / 60);
        let s = remaining_{key} % 60;
        document.getElementById("time_{key}").innerText =
            String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0');
        remaining_{key} -= 1;
        setTimeout(tick_{key}, 1000);
    }}
    tick_{key}();
    </script>
    """
    components.html(html, height=70)
