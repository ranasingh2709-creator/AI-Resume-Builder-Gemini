import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# Paste your Gemini API key here
API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #1f2937;
}
.subtitle {
    font-size: 18px;
    color: #4b5563;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📄 AI Resume Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Create an internship-ready resume using Gemini AI</div>', unsafe_allow_html=True)

st.sidebar.title("🚀 Project Info")
st.sidebar.write("Built using:")
st.sidebar.write("✅ Python")
st.sidebar.write("✅ Streamlit")
st.sidebar.write("✅ Gemini API")
st.sidebar.write("✅ ReportLab PDF")

st.sidebar.info("Fill your details, choose a target role, generate your resume, and download it as PDF.")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")

with col2:
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
    career_goal = st.text_area("Career Goal")

def create_pdf(resume_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    x = 45
    y = height - 45

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, "AI Generated Resume")
    y -= 30

    pdf.setFont("Helvetica", 10)

    for line in resume_text.split("\n"):
        if y < 45:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 45

        if line.strip().isupper():
            pdf.setFont("Helvetica-Bold", 11)
        else:
            pdf.setFont("Helvetica", 10)

        pdf.drawString(x, y, line[:100])
        y -= 15

    pdf.save()
    buffer.seek(0)
    return buffer

if st.button("✨ Generate Professional Resume"):
    if name == "" or skills == "" or projects == "":
        st.warning("Please fill at least Name, Skills, and Projects.")
    else:
        prompt = f"""
        Create a clean, professional, internship-ready resume for the role of {role}.

        Use this exact structure:

        NAME
        CONTACT
        PROFESSIONAL SUMMARY
        EDUCATION
        TECHNICAL SKILLS
        PROJECTS
        EXPERIENCE / CERTIFICATIONS
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
        Career Goal: {career_goal}

        Rules:
        - Make it suitable for a first-year B.Tech CSE Data Science student.
        - Keep it professional and realistic.
        - Do not add fake achievements.
        - Use strong resume language.
        - Make projects sound impressive but truthful.
        - Keep formatting clean.
        """

        with st.spinner("Generating your professional resume..."):
            response = model.generate_content(prompt)
            resume_text = response.text

        st.success("Resume generated successfully!")

        st.markdown("## 📄 Generated Resume")
        st.markdown(f'<div class="card">{resume_text}</div>', unsafe_allow_html=True)

        pdf_file = create_pdf(resume_text)

        st.download_button(
            label="📥 Download Resume as PDF",
            data=pdf_file,
            file_name="AI_Resume_Builder_Output.pdf",
            mime="application/pdf"
        )
