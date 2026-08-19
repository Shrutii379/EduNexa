"""
EduNexa — Academic Records & Analytics
A premium, single-file Streamlit dashboard for student management and
result analysis. Data persists to students.json / marks.json next to
this file, so the ledger survives restarts on hosts with a writable
filesystem (Streamlit Community Cloud resets storage on redeploy).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="EduNexa | Academic Records & Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

STUDENTS_DB = "students.json"
MARKS_DB = "marks.json"
SUBJECTS = ["Python", "Maths", "DBMS"]

GRADE_COLORS = {
    "A+": ("#C9A227", "#E8C874"),
    "A":  ("#B8952A", "#D9BB63"),
    "B":  ("#4C7EF3", "#7FA3F7"),
    "C":  ("#5FB0A0", "#8FCBC0"),
    "D":  ("#D98A3D", "#F0B36B"),
    "F":  ("#C1573F", "#E08268"),
    "-":  ("#3A4664", "#5A6786"),
}

DEPT_PALETTE = ["#C9A227", "#4C7EF3", "#5FB0A0", "#C1573F", "#8F7FE8", "#3FB0C9"]

# ----------------------------------------------------------------------
# DATA LAYER
# ----------------------------------------------------------------------
def load_json(path):
    p = Path(path)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return []
    return []


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=4))


if "students" not in st.session_state:
    st.session_state.students = load_json(STUDENTS_DB)
if "marks" not in st.session_state:
    st.session_state.marks = load_json(MARKS_DB)


def persist_students():
    save_json(STUDENTS_DB, st.session_state.students)


def persist_marks():
    save_json(MARKS_DB, st.session_state.marks)


def next_ids():
    return [s["Student_ID"] for s in st.session_state.students]


def find_student(student_id):
    for s in st.session_state.students:
        if s["Student_ID"] == student_id:
            return s
    return None


def find_marks(student_id):
    for m in st.session_state.marks:
        if m["Student_ID"] == student_id:
            return m
    return None


def grade_from_pct(pct):
    if pd.isna(pct):
        return "-"
    if pct >= 90:
        return "A+"
    if pct >= 80:
        return "A"
    if pct >= 70:
        return "B"
    if pct >= 60:
        return "C"
    if pct >= 50:
        return "D"
    return "F"


def get_data():
    """Merged students + marks ledger with Total / Percentage / Grade."""
    if not st.session_state.students:
        return pd.DataFrame()
    sdf = pd.DataFrame(st.session_state.students)
    if st.session_state.marks:
        mdf = pd.DataFrame(st.session_state.marks)
    else:
        mdf = pd.DataFrame(columns=["Student_ID"] + SUBJECTS)
    df = sdf.merge(mdf, on="Student_ID", how="left")
    for s in SUBJECTS:
        if s not in df.columns:
            df[s] = pd.NA

    marks_matrix = df[SUBJECTS].to_numpy(dtype="float64")
    with np.errstate(invalid="ignore"):
        df["Total"] = np.where(
            np.isnan(marks_matrix).any(axis=1), np.nan, np.nansum(marks_matrix, axis=1)
        )
        df["Percentage"] = np.nanmean(marks_matrix, axis=1)
    df["Grade"] = df["Percentage"].apply(grade_from_pct)
    return df


def get_topper():
    df = get_data().dropna(subset=["Percentage"])
    if df.empty:
        return None
    return df.loc[df["Percentage"].idxmax()]


def failed_students():
    df = get_data().dropna(subset=["Percentage"])
    return df[df["Percentage"] < 50]


def department_analysis():
    df = get_data().dropna(subset=["Percentage"])
    if df.empty:
        return pd.DataFrame()
    out = (
        df.groupby("Department")
        .agg(Students=("Student_ID", "count"), Avg_Percentage=("Percentage", "mean"))
        .reset_index()
        .sort_values("Avg_Percentage", ascending=False)
    )
    return out


def subject_analysis():
    df = get_data().dropna(subset=["Percentage"])
    if df.empty:
        return pd.DataFrame()
    rows = []
    for subj in SUBJECTS:
        s = df[subj].dropna()
        if s.empty:
            continue
        arr = s.to_numpy(dtype="float64")
        top_row = df.loc[s.idxmax()]
        rows.append(
            {
                "Subject": subj,
                "Average": round(float(np.mean(arr)), 2),
                "Highest": int(np.max(arr)),
                "Lowest": int(np.min(arr)),
                "Top_Scorer": top_row["Name"],
            }
        )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# STYLE
# ----------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
  --ink-900:#0E1626; --ink-800:#16213A; --ink-700:#1F2C4A;
  --line: rgba(201,162,39,0.18);
  --gold:#C9A227; --gold-light:#E8C874;
  --parchment:#F3ECD9; --muted:#9AA7C2;
  --sage:#5FB0A0; --brick:#C1573F; --azure:#4C7EF3;
}

html, body, [class*="css"]{ font-family:'Manrope', sans-serif; }
.stApp{
  background:
    radial-gradient(circle at 8% -10%, #17233F 0%, transparent 45%),
    radial-gradient(circle at 100% 0%, #14203A 0%, transparent 40%),
    var(--ink-900);
}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

h1,h2,h3{ font-family:'Fraunces', serif; color:var(--parchment); letter-spacing:.2px; }
p, span, label, div{ color:var(--parchment); }
small, .muted{ color:var(--muted) !important; }

/* ---- Masthead ---- */
.edunexa-mast{ display:flex; align-items:center; gap:16px; margin-bottom:.2rem; }
.edunexa-seal{
  width:52px; height:52px; border-radius:50%;
  background:conic-gradient(from 210deg, var(--gold), var(--gold-light), var(--gold));
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 6px 18px rgba(201,162,39,0.35);
  flex-shrink:0;
}
.edunexa-seal-inner{
  width:40px; height:40px; border-radius:50%; background:var(--ink-900);
  display:flex; align-items:center; justify-content:center;
  font-family:'Fraunces', serif; font-weight:700; font-size:16px; color:var(--gold-light);
}
.edunexa-title{ font-family:'Fraunces', serif; font-size:2.1rem; font-weight:600; margin:0; line-height:1.1; }
.edunexa-tagline{ font-family:'IBM Plex Mono', monospace; font-size:.78rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin-top:2px; }
.edunexa-rule{ height:1px; background:linear-gradient(90deg, var(--gold) 0%, rgba(201,162,39,0.08) 55%, transparent 100%);
  margin:.9rem 0 1.6rem 0; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg, var(--ink-800), var(--ink-900));
  border-right:1px solid var(--line);
}
section[data-testid="stSidebar"] .block-container{ padding-top:1.6rem; }
.sidebar-brand{ font-family:'Fraunces', serif; font-size:1.35rem; font-weight:600; margin-bottom:.1rem; }
.sidebar-sub{ font-family:'IBM Plex Mono', monospace; font-size:.7rem; color:var(--muted);
  letter-spacing:.12em; text-transform:uppercase; margin-bottom:1.4rem; }

section[data-testid="stSidebar"] div[role="radiogroup"] label{
  background:transparent; border:1px solid transparent; border-radius:12px;
  padding:10px 14px !important; margin-bottom:6px; transition:all .22s ease; cursor:pointer;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{
  background:rgba(201,162,39,0.08); border-color:var(--line);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(90deg, rgba(201,162,39,0.22), rgba(201,162,39,0.02));
  border-color:var(--gold); box-shadow:0 4px 14px rgba(201,162,39,0.15);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p{
  font-weight:600; font-size:.95rem; margin:0;
}

/* ---- Cards ---- */
.ledger-card{
  background:var(--ink-800); border:1px solid var(--line); border-radius:18px;
  padding:1.4rem 1.5rem; box-shadow:0 10px 30px rgba(0,0,0,0.25);
  animation:rise .45s ease; margin-bottom:1rem;
}
@keyframes rise{ from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:translateY(0);} }

.kpi-card{
  background:var(--ink-800); border:1px solid var(--line); border-radius:16px;
  padding:1.1rem 1.3rem; transition:all .25s ease; animation:rise .45s ease;
}
.kpi-card:hover{ transform:translateY(-4px); box-shadow:0 16px 32px rgba(0,0,0,.35); border-color:var(--gold); }
.kpi-label{ font-family:'IBM Plex Mono', monospace; font-size:.72rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); margin-bottom:.35rem; }
.kpi-value{ font-family:'Fraunces', serif; font-size:2rem; font-weight:600; color:var(--parchment); line-height:1; }
.kpi-sub{ font-size:.78rem; color:var(--muted); margin-top:.35rem; }

.entry-row{
  display:flex; align-items:center; gap:14px; padding:12px 14px; border-radius:12px;
  border:1px solid var(--line); background:var(--ink-700); margin-bottom:8px;
  transition:all .2s ease;
}
.entry-row:hover{ border-color:var(--gold); transform:translateX(3px); }
.avatar{
  width:38px; height:38px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-family:'Fraunces', serif; font-weight:600; font-size:.95rem; color:var(--ink-900);
}
.alert-row{
  border-left:3px solid var(--brick); background:rgba(193,87,63,0.08);
  border-radius:10px; padding:10px 14px; margin-bottom:8px;
}

/* ---- Buttons ---- */
.stButton>button, .stFormSubmitButton>button{
  background:linear-gradient(135deg, var(--gold), var(--gold-light));
  color:var(--ink-900) !important; font-weight:700; border:none; border-radius:10px;
  padding:.5rem 1.2rem; transition:all .2s ease;
}
.stButton>button:hover, .stFormSubmitButton>button:hover{
  transform:translateY(-2px); box-shadow:0 8px 20px rgba(201,162,39,0.35);
}
button[kind="secondary"]{ background:var(--ink-700) !important; color:var(--parchment) !important; }

/* ---- Tabs ---- */
button[data-baseweb="tab"]{ font-weight:600; color:var(--muted); }
button[data-baseweb="tab"][aria-selected="true"]{ color:var(--gold-light) !important; }
div[data-baseweb="tab-highlight"]{ background-color:var(--gold) !important; }
div[data-baseweb="tab-border"]{ background-color:var(--line) !important; }

/* ---- Inputs ---- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div{
  background:var(--ink-700) !important; border-radius:10px !important;
  border:1px solid var(--line) !important; color:var(--parchment) !important;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"]{ border-radius:14px; overflow:hidden; border:1px solid var(--line); }

/* ---- Metrics fallback ---- */
[data-testid="stMetric"]{
  background:var(--ink-800); border:1px solid var(--line); border-radius:14px; padding:.8rem 1rem;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# UI HELPERS
# ----------------------------------------------------------------------
def masthead(subtitle):
    st.markdown(
        f"""
        <div class="edunexa-mast">
          <div class="edunexa-seal"><div class="edunexa-seal-inner">EN</div></div>
          <div>
            <p class="edunexa-title">EduNexa</p>
            <p class="edunexa-tagline">{subtitle}</p>
          </div>
        </div>
        <div class="edunexa-rule"></div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def grade_seal(grade, size=110):
    c1, c2 = GRADE_COLORS.get(grade, GRADE_COLORS["-"])
    inner = size - 18
    font_size = round(size * 0.32)
    return f"""
    <div style="width:{size}px;height:{size}px;border-radius:50%;
        background:conic-gradient(from 220deg,{c1},{c2},{c1});
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 8px 24px rgba(0,0,0,0.35);">
      <div style="width:{inner}px;height:{inner}px;border-radius:50%;background:#0E1626;
          display:flex;align-items:center;justify-content:center;
          font-family:'Fraunces',serif;font-size:{font_size}px;font-weight:600;color:{c2};
          border:1px solid rgba(232,200,116,0.25);">
        {grade}
      </div>
    </div>
    """


def avatar_html(name, dept):
    initials = "".join([p[0] for p in name.split()[:2]]).upper() if name else "?"
    idx = abs(hash(dept)) % len(DEPT_PALETTE) if dept else 0
    color = DEPT_PALETTE[idx]
    return f'<div class="avatar" style="background:{color};">{initials}</div>'


def bar_row(label, value, max_value, color="var(--gold)"):
    """A single lightweight CSS bar — used instead of a charting library."""
    pct = 0 if max_value <= 0 else max(0, min(100, (value / max_value) * 100))
    st.markdown(
        f"""
        <div style="margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; font-size:.85rem; margin-bottom:4px;">
            <span>{label}</span><span class="muted">{value:.1f}</span>
          </div>
          <div style="background:var(--ink-700); border-radius:8px; height:10px; overflow:hidden; border:1px solid var(--line);">
            <div style="width:{pct:.1f}%; background:{color}; height:100%; border-radius:8px;"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(message):
    st.markdown(
        f"""<div class="ledger-card" style="text-align:center; color:var(--muted);">
        {message}</div>""",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# SIDEBAR NAV
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🎓 EduNexa</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Academic Records &amp; Analytics</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["Dashboard", "Students", "Marks", "Result Ledger", "Analysis"],
        label_visibility="collapsed",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"📚 {len(st.session_state.students)} students · 📝 {len(st.session_state.marks)} mark records")

# ----------------------------------------------------------------------
# PAGE: DASHBOARD
# ----------------------------------------------------------------------
if page == "Dashboard":
    masthead("Overview")

    df = get_data()
    total_students = len(st.session_state.students)
    scored = df.dropna(subset=["Percentage"]) if not df.empty else pd.DataFrame()
    avg_pct = round(scored["Percentage"].mean(), 1) if not scored.empty else 0
    pass_rate = round((scored["Percentage"] >= 50).mean() * 100, 1) if not scored.empty else 0
    dept_count = df["Department"].nunique() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Enrolled Students", total_students, "Active ledger entries")
    with c2:
        kpi_card("Average Percentage", f"{avg_pct}%", "Across all scored students")
    with c3:
        kpi_card("Pass Rate", f"{pass_rate}%", "Percentage ≥ 50")
    with c4:
        kpi_card("Departments", dept_count, "Distinct programs")

    st.write("")
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("#### Department standing")
        dept_df = department_analysis()
        if dept_df.empty:
            empty_state("No scored students yet — record marks to see department averages.")
        else:
            st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
            for i, row in dept_df.iterrows():
                color = DEPT_PALETTE[i % len(DEPT_PALETTE)]
                bar_row(row["Department"], row["Avg_Percentage"], 100, color)
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("#### Grade distribution")
        if scored.empty:
            empty_state("No results recorded yet.")
        else:
            counts = scored["Grade"].value_counts()
            st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
            for grade, count in counts.items():
                color = GRADE_COLORS.get(grade, GRADE_COLORS["-"])[0]
                bar_row(f"Grade {grade}", count, int(np.max(counts.to_numpy())), color)
            st.markdown("</div>", unsafe_allow_html=True)

    topper = get_topper()
    if topper is not None:
        st.write("")
        st.markdown("#### Top performer")
        tc1, tc2 = st.columns([0.18, 1])
        with tc1:
            st.markdown(grade_seal(topper["Grade"], 96), unsafe_allow_html=True)
        with tc2:
            st.markdown(
                f"""
                <div class="ledger-card" style="margin-top:4px;">
                  <div style="font-family:'Fraunces',serif; font-size:1.3rem;">{topper['Name']}</div>
                  <div class="muted">ID {topper['Student_ID']} · {topper['Department']}</div>
                  <div style="margin-top:6px;">Percentage: <b>{topper['Percentage']:.2f}%</b> · Total: <b>{int(topper['Total'])}/{len(SUBJECTS)*100}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ----------------------------------------------------------------------
# PAGE: STUDENTS
# ----------------------------------------------------------------------
elif page == "Students":
    masthead("Student Register")
    tabs = st.tabs(["➕ Add", "📖 Directory", "🔍 Search", "✏️ Update", "🗑️ Delete"])

    with tabs[0]:
        st.markdown("Enter a new entry into the student register.")
        with st.form("add_student_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            sid = c1.number_input("Student ID", min_value=1, step=1)
            name = c2.text_input("Full name")
            dept = c3.text_input("Department")
            submitted = st.form_submit_button("Add student")
        if submitted:
            if sid in next_ids():
                st.error(f"Student ID {sid} is already on the register.")
            elif not name.strip() or not dept.strip():
                st.error("Name and department can't be empty.")
            else:
                st.session_state.students.append(
                    {"Student_ID": int(sid), "Name": name.strip(), "Department": dept.strip()}
                )
                persist_students()
                st.success(f"{name.strip()} added to the register.")

    with tabs[1]:
        if not st.session_state.students:
            empty_state("The register is empty — add your first student to begin.")
        else:
            view = st.radio("View as", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")
            if view == "Table":
                st.dataframe(pd.DataFrame(st.session_state.students), use_container_width=True, hide_index=True)
            else:
                for s in sorted(st.session_state.students, key=lambda x: x["Student_ID"]):
                    st.markdown(
                        f"""
                        <div class="entry-row">
                          {avatar_html(s['Name'], s['Department'])}
                          <div>
                            <div style="font-weight:700;">{s['Name']}</div>
                            <div class="muted" style="font-family:'IBM Plex Mono',monospace; font-size:.8rem;">
                              ID {s['Student_ID']} · {s['Department']}
                            </div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with tabs[2]:
        if not st.session_state.students:
            empty_state("Nothing to search yet — the register is empty.")
        else:
            sid = st.selectbox("Student ID", next_ids(), key="search_id")
            s = find_student(sid)
            if s:
                st.markdown(
                    f"""
                    <div class="ledger-card">
                      <div style="display:flex; align-items:center; gap:14px;">
                        {avatar_html(s['Name'], s['Department'])}
                        <div>
                          <div style="font-family:'Fraunces',serif; font-size:1.2rem;">{s['Name']}</div>
                          <div class="muted">ID {s['Student_ID']} · {s['Department']}</div>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[3]:
        if not st.session_state.students:
            empty_state("Nothing to update yet — the register is empty.")
        else:
            sid = st.selectbox("Student ID", next_ids(), key="update_id")
            s = find_student(sid)
            with st.form("update_student_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Name", value=s["Name"])
                dept = c2.text_input("Department", value=s["Department"])
                submitted = st.form_submit_button("Save changes")
            if submitted:
                s["Name"] = name.strip() or s["Name"]
                s["Department"] = dept.strip() or s["Department"]
                persist_students()
                st.success("Register entry updated.")

    with tabs[4]:
        if not st.session_state.students:
            empty_state("Nothing to delete yet — the register is empty.")
        else:
            sid = st.selectbox("Student ID", next_ids(), key="delete_id")
            s = find_student(sid)
            st.warning(f"This permanently removes **{s['Name']}** (ID {sid}) from the register.")
            confirm = st.checkbox("I understand this can't be undone.")
            if st.button("Delete permanently", disabled=not confirm):
                st.session_state.students.remove(s)
                persist_students()
                st.session_state.marks = [m for m in st.session_state.marks if m["Student_ID"] != sid]
                persist_marks()
                st.success("Entry removed from the register.")
                st.rerun()

# ----------------------------------------------------------------------
# PAGE: MARKS
# ----------------------------------------------------------------------
elif page == "Marks":
    masthead("Marks Ledger")
    tabs = st.tabs(["➕ Add / Update", "📖 View all"])

    with tabs[0]:
        if not st.session_state.students:
            empty_state("Add students first — marks need a register entry to attach to.")
        else:
            sid = st.selectbox("Student ID", next_ids(), key="marks_id")
            s = find_student(sid)
            existing = find_marks(sid)
            st.caption(f"Recording for **{s['Name']}** · {s['Department']}")
            with st.form("marks_form"):
                c1, c2, c3 = st.columns(3)
                py = c1.number_input("Python", 0, 100, value=existing["Python"] if existing else 0)
                ma = c2.number_input("Maths", 0, 100, value=existing["Maths"] if existing else 0)
                db = c3.number_input("DBMS", 0, 100, value=existing["DBMS"] if existing else 0)
                submitted = st.form_submit_button("Save marks")
            if submitted:
                entry = {"Student_ID": int(sid), "Python": int(py), "Maths": int(ma), "DBMS": int(db)}
                if existing:
                    existing.update(entry)
                else:
                    st.session_state.marks.append(entry)
                persist_marks()
                st.success("Marks saved to the ledger.")

    with tabs[1]:
        if not st.session_state.marks:
            empty_state("No marks recorded yet.")
        else:
            st.dataframe(pd.DataFrame(st.session_state.marks), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------
# PAGE: RESULT LEDGER
# ----------------------------------------------------------------------
elif page == "Result Ledger":
    masthead("Result Card")
    if not st.session_state.students:
        empty_state("Add students and marks first to generate a result.")
    else:
        sid = st.selectbox("Student ID", next_ids(), key="result_id")
        s = find_student(sid)
        m = find_marks(sid)
        if not m:
            st.warning("No marks recorded for this student yet.")
        else:
            marks = {subj: m[subj] for subj in SUBJECTS}
            total = sum(marks.values())
            pct = total / len(SUBJECTS)
            grade = grade_from_pct(pct)

            head_l, head_r = st.columns([0.2, 1])
            with head_l:
                st.markdown(grade_seal(grade, 108), unsafe_allow_html=True)
            with head_r:
                st.markdown(
                    f"""
                    <div style="margin-top:6px;">
                      <div style="font-family:'Fraunces',serif; font-size:1.5rem;">{s['Name']}</div>
                      <div class="muted">ID {s['Student_ID']} · {s['Department']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
            for subj, score in marks.items():
                st.markdown(f"**{subj}** — {score}/100")
                st.progress(score / 100)
            st.markdown(
                f"""
                <div class="edunexa-rule"></div>
                <div style="display:flex; justify-content:space-between; font-family:'IBM Plex Mono',monospace;">
                  <span>Total: <b>{total}/{len(SUBJECTS)*100}</b></span>
                  <span>Percentage: <b>{pct:.2f}%</b></span>
                  <span>Grade: <b>{grade}</b></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PAGE: ANALYSIS
# ----------------------------------------------------------------------
elif page == "Analysis":
    masthead("Analysis")
    tabs = st.tabs(["🏆 Topper", "⚠️ Failed", "📘 Subjects", "🏛️ Departments", "📚 Full ledger"])

    with tabs[0]:
        topper = get_topper()
        if topper is None:
            empty_state("No scored students yet.")
        else:
            c1, c2 = st.columns([0.2, 1])
            with c1:
                st.markdown(grade_seal(topper["Grade"], 108), unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f"""
                    <div class="ledger-card" style="margin-top:4px;">
                      <div style="font-family:'Fraunces',serif; font-size:1.3rem;">{topper['Name']}</div>
                      <div class="muted">ID {topper['Student_ID']} · {topper['Department']}</div>
                      <div style="margin-top:6px;">Percentage: <b>{topper['Percentage']:.2f}%</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.balloons()

    with tabs[1]:
        failed = failed_students()
        if failed.empty:
            empty_state("No student is currently below the 50% pass mark.")
        else:
            for _, row in failed.iterrows():
                st.markdown(
                    f"""
                    <div class="alert-row">
                      <b>{row['Name']}</b> · ID {row['Student_ID']} · {row['Department']}
                      — <span style="color:var(--brick);">{row['Percentage']:.2f}%</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[2]:
        subj_df = subject_analysis()
        if subj_df.empty:
            empty_state("No scored students yet.")
        else:
            st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
            for i, row in subj_df.iterrows():
                color = DEPT_PALETTE[i % len(DEPT_PALETTE)]
                bar_row(row["Subject"], row["Average"], 100, color)
            st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(subj_df, use_container_width=True, hide_index=True)

    with tabs[3]:
        dept_df = department_analysis()
        if dept_df.empty:
            empty_state("No scored students yet.")
        else:
            st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
            for i, row in dept_df.iterrows():
                color = DEPT_PALETTE[i % len(DEPT_PALETTE)]
                bar_row(row["Department"], row["Avg_Percentage"], 100, color)
            st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(dept_df, use_container_width=True, hide_index=True)

    with tabs[4]:
        df = get_data()
        if df.empty:
            empty_state("No data recorded yet.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)