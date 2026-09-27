# =======================================================
# Resume ADTS (ATS-like) Analyzer - Clean Version
# Features:
# - Resume Upload (PDF / DOCX)
# - Department-wise scoring (CSE, ECE, EEE, Mech)
# - Aptitude, Soft Skills, Technical, Domain scoring
# - Clean Chart (no emoji warnings)
# - Emoji only in text outputs (safe)
# - Improvement advice
# - Confidence message ("Selected!" if score >= 70)
# - 5-question Quiz
# =======================================================

!pip install -q python-docx PyPDF2 matplotlib

import re, random, io
from google.colab import files
import PyPDF2, docx
import matplotlib.pyplot as plt

# ---------------- File Extract ----------------
def extract_text_from_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def get_resume_text():
    print("📂 Upload your resume (PDF or DOCX)")
    uploaded = files.upload()
    filename = list(uploaded.keys())[0]
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(filename)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(filename)
    else:
        raise ValueError("Only PDF/DOCX supported")

# ---------------- Keyword Packs ----------------
DOMAIN_KEYWORDS = {
    "cse": {
        "domain": ["machine learning","ai","artificial intelligence","deep learning","database","cloud","cybersecurity","web development","blockchain"],
        "tech": ["python","java","c++","html","css","javascript","react","node","sql"]
    },
    "ece": {
        "domain": ["vlsi","embedded","signal processing","fpga","microcontroller","analog","digital circuits","communication"],
        "tech": ["verilog","vhdl","matlab","c","c++","arduino","xilinx"]
    },
    "eee": {
        "domain": ["power systems","electrical machines","control systems","switchgear","hvac","power electronics","smart grid","renewable energy"],
        "tech": ["pscad","matlab","simulink","etap","labview","arduino","c"]
    },
    "mech": {
        "domain": ["thermodynamics","manufacturing","solid mechanics","cad","cam","design","automobile","fluid mechanics"],
        "tech": ["solidworks","ansys","autocad","catia","matlab"]
    }
}

APTITUDE = ["analytical","reasoning","problem solving","mathematics","logical"]
SOFT_SKILLS = ["communication","teamwork","leadership","creativity","adaptability"]

# ---------------- Quiz Bank ----------------
QUIZ = [
    {"q":"Which data structure uses FIFO?", "options":["Stack","Queue","Tree","Graph"], "ans":2},
    {"q":"Which language is best for AI/ML?", "options":["C","Python","HTML","SQL"], "ans":2},
    {"q":"Ohm’s law states V = ?","options":["I/R","IR","I*R","V/I"], "ans":3},
    {"q":"Which CAD software is used in Mech?", "options":["Photoshop","SolidWorks","MS Word","After Effects"], "ans":2},
    {"q":"What is teamwork?", "options":["Working alone","Working in group","Time management","None"], "ans":2},
    {"q":"SQL is used for?", "options":["Operating System","Databases","Hardware","Networking"], "ans":2},
    {"q":"Which uses renewable energy?", "options":["Coal","Diesel","Solar","Nuclear"], "ans":3},
    {"q":"Which skill is a soft skill?", "options":["Python","C++","Leadership","Matlab"], "ans":3},
]

# ---------------- Analyzer ----------------
def analyze_resume(text, domain_choice="auto"):
    text_low = text.lower()
    scores = {"aptitude":0,"soft":0,"technical":0,"domain":0}

    # domain auto detect
    if domain_choice=="auto":
        best, count = "cse",0
        for d in DOMAIN_KEYWORDS:
            hits = sum(1 for w in DOMAIN_KEYWORDS[d]["domain"]+DOMAIN_KEYWORDS[d]["tech"] if w in text_low)
            if hits>count: best, count = d,hits
        domain_choice = best

    # scoring
    scores["aptitude"] = sum(5 for k in APTITUDE if k in text_low)
    scores["soft"] = sum(5 for k in SOFT_SKILLS if k in text_low)
    scores["domain"] = sum(5 for k in DOMAIN_KEYWORDS[domain_choice]["domain"] if k in text_low)
    scores["technical"] = sum(5 for k in DOMAIN_KEYWORDS[domain_choice]["tech"] if k in text_low)

    # cap each at 25
    for k in scores: scores[k] = min(scores[k],25)

    total = sum(scores.values())
    return scores,total,domain_choice

# ---------------- Improvement Tips ----------------
def give_advice(scores):
    tips=[]
    if scores["aptitude"]<15: tips.append("📐 Add more problem solving / reasoning skills.")
    if scores["soft"]<15: tips.append("🧑‍🤝‍🧑 Mention teamwork, leadership, or communication examples.")
    if scores["technical"]<15: tips.append("💻 List more programming/software tools with projects.")
    if scores["domain"]<15: tips.append("📡 Highlight domain-specific projects or internships.")
    if not tips: tips=["🌟 Excellent! Resume already looks strong."]
    return tips

# ---------------- Chart ----------------
def show_chart(scores,total):
    labels = ["Aptitude","Soft Skills","Technical","Domain"]  # Clean labels
    vals = list(scores.values())
    plt.bar(labels,vals,color=['blue','green','red','orange'])
    plt.ylim(0,25)
    # Removed emoji to prevent font warning
    plt.title(f"Resume Analysis — Total Score: {total}/100")
    plt.show()

# ---------------- Quiz ----------------
def run_quiz():
    print("\n📝 Confidence Quiz (5 Questions)")
    qs=random.sample(QUIZ,5)
    score=0
    for i,q in enumerate(qs,1):
        print(f"\nQ{i}: {q['q']}")
        for idx,opt in enumerate(q["options"],1):
            print(f"{idx}. {opt}")
        ans=int(input("Enter your choice (1-4): "))
        if ans==q["ans"]:
            print("✅ Correct")
            score+=1
        else:
            print(f"❌ Wrong. Correct: {q['options'][q['ans']-1]}")
    print(f"\n📖 Quiz Completed! You got {score}/5 correct.")
    if score>=4: print("💪 Great! You're confident for interviews.")
    elif score>=2: print("👍 Decent, keep practicing.")
    else: print("🙂 Don't worry, keep improving and try again!")

# ---------------- Run ----------------
text = get_resume_text()
scores,total,domain = analyze_resume(text,"auto")

print("\n📊 Resume Analysis Results:")
print(f"📘 Aptitude Skills: {scores['aptitude']}/25")
print(f"🧑‍🤝‍🧑 Soft Skills: {scores['soft']}/25")
print(f"💻 Technical Skills: {scores['technical']}/25")
print(f"📡 Domain Knowledge ({domain.upper()}): {scores['domain']}/25")
print(f"🎯 Total ATS Score: {total}/100")

if total>=70:
    print("\n✅ Your Resume is Strong! 🎉 It would likely be selected. Keep it up!")
else:
    print("\n💡 Your Resume Needs Improvement. Suggestions:")
    for tip in give_advice(scores):
        print("-",tip)

show_chart(scores,total)
run_quiz()
