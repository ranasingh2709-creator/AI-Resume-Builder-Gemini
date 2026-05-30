import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #fdf2f8);
}
.hero {
    padding: 35px;
    border-radius: 25px;
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.card {
    padding: 25px;
    border-radius: 18px;
    background-color: white;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    color: #111827;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🚀 AI Resume Builder</h1>
    <p>Create ATS-friendly, internship-ready resumes using Gemini AI</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("📌 Project Info")
st.sidebar.success("Python")
st.sidebar.success("Streamlit")
st.sidebar.success("Gemini API")
st.sidebar.success("ReportLab PDF")
st.sidebar.info("Generate resume, check ATS score, and download PDF.")

theme = st.sidebar.radio("Choose Resume Style", ["Modern", "Minimal", "Professional"])

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 Personal Details")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")
    photo = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])

    if photo:
        st.image(photo, width=140)

with col2:
    st.markdown("### 🎯 Resume Details")
    role = st.selectbox(
        "Target Role",
        [
            "Software Developer Intern",
            "AI Intern",
            "Machine Learning Intern",
            "Data Science Intern",
            "Frontend Developer Intern"
        ]
    )

    education = st.text_area("Education")
    skills = st.text_area("Technical Skills")
    projects = st.text_area("Projects")
    experience = st.text_area("Experience / Internship / Certificates")
    achievements = st.text_area("Achievements")
    career_goal = st.text_area("Career Goal")


def calculate_ats_score(skills, projects, education, experience, achievements):
    score = 35

    if skills.strip():
        score += 15
    if projects.strip():
        score += 20
    if education.strip():
        score += 10
    if experience.strip():
        score += 10
    if achievements.strip():
        score += 5
    if len(skills.split()) >= 8:
        score += 5

    return min(score, 100)


def create_pdf(resume_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    x = 45
    y = height - 45

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, "AI Generated Resume")
    y -= 30

    for line in resume_text.split("\n"):
        wrapped_lines = textwrap.wrap(line, width=90)

        if not wrapped_lines:
            y -= 10

        for wrapped_line in wrapped_lines:
            if y < 50:
                pdf.showPage()
                y = height - 50

            if wrapped_line.strip().isupper():
                pdf.setFont("Helvetica-Bold", 11)
            else:
                pdf.setFont("Helvetica", 10)

            pdf.drawString(x, y, wrapped_line)
            y -= 15

    pdf.save()
    buffer.seek(0)
    return buffer


if st.button("✨ Generate Professional Resume"):
    if not API_KEY:
        st.error("Gemini API key missing. Add GEMINI_API_KEY in Streamlit Secrets.")
    elif not name or not skills or not projects:
        st.warning("Please fill at least Full Name, Technical Skills, and Projects.")
    else:
        prompt = f"""
        Create a clean, professional, ATS-friendly resume for the role of {role}.

        Resume template style: {theme}

        Use this exact structure:

        NAME
        CONTACT
        PROFESSIONAL SUMMARY
        EDUCATION
        TECHNICAL SKILLS
        PROJECTS
        EXPERIENCE / CERTIFICATIONS
        ACHIEVEMENTS
        CAREER OBJECTIVE

        User details:
        Name: {name}
        Email: {email}
        Phone: {phone}
        LinkedIn: {linkedin}
        GitHub: {github}
        Education: {education}
        Skills: {skills}
        Projects: {projects}
        Experience / Certifications: {experience}
        Achievements: {achievements}
        Career Goal: {career_goal}

        Rules:
        - Use the actual email and phone number given by the user.
        - Do not write [Your Email], [Your Phone], or placeholders.
        - Make it suitable for an incoming second-year B.Tech CSE Data Science student.
        - Do not add fake achievements.
        - Use strong but realistic resume language.
        - Keep the format recruiter-friendly and ATS-friendly.
        """

        with st.spinner("Generating your professional resume..."):
            response = model.generate_content(prompt)
            resume_text = response.text

        ats_score = calculate_ats_score(
            skills,
            projects,
            education,
            experience,
            achievements
        )

        st.success("Resume generated successfully!")

        st.markdown("## 📊 ATS Resume Score")
        st.progress(ats_score / 100)
        st.success(f"ATS Score: {ats_score}/100")

        if ats_score < 75:
            st.info("Tip: Add more skills, projects, certifications, and measurable achievements.")
        elif ats_score < 90:
            st.info("Good resume. Improve it further with stronger project impact.")
        else:
            st.info("Excellent resume strength for internship applications.")

        st.markdown("## 📄 Resume Preview")
        st.markdown(f'<div class="card">{resume_text}</div>', unsafe_allow_html=True)

        pdf_file = create_pdf(resume_text)

        st.download_button(
            label="📥 Download Resume as PDF",
            data=pdf_file,
            file_name="AI_Resume_Builder_Output.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>Built with ❤️ using Python, Streamlit, Gemini API and ReportLab</p>",
    unsafe_allow_html=True
)
