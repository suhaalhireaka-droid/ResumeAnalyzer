# pages/1_Applicant.py
import streamlit as st
import utils
import plotly.graph_objects as go
from datetime import datetime
from auth import logout

st.set_page_config(page_title="Applicant Portal", page_icon="👔", layout="wide")

# ========== AUTHENTICATION CHECK ==========
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("👋 Hey! Please sign in first to access your dashboard.")
    st.switch_page("pages/3_Login.py")

# ========== STYLING ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    [data-testid="stSidebar"] {
        background-color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    .skill-tag {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .skill-match { background: #d4edda; color: #155724; }
    .skill-missing { background: #f8d7da; color: #721c24; }
    
    .upload-area {
        border: 2px dashed #ddd;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: #fafafa;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #f5f7ff;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'applicant_analysis' not in st.session_state:
    st.session_state.applicant_analysis = None

# ========== HEADER ==========
user_name = st.session_state.user.get("name", "there")
uid = st.session_state.user.get("uid", "")

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid #eee; margin-bottom: 2rem;">
    <div>
        <h1 style="font-size: 2rem; font-weight: 700; color: #1a1a2e; margin: 0;">👔 Your Dashboard</h1>
        <p style="color: #666; margin: 0.25rem 0 0 0;">Welcome back, {user_name}! Let's improve your resume.</p>
    </div>
    <span style="color: #888;">👤 {user_name}</span>
</div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 💡 How This Works")
    st.markdown("""
    1. **Paste a job** you're interested in
    2. **Upload your resume** (PDF)
    3. **Get your match score** instantly
    4. **See what skills match** and what's missing
    5. **Follow the tips** to improve your resume
    
    It's like having a career coach in your pocket! 🎯
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 What You'll See")
    st.markdown("""
    - ✅ Your match percentage
    - ✅ Skills the employer wants
    - ✅ What you're missing
    - ✅ Specific tips to improve
    """)
    
    st.markdown("---")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()

# ========== MAIN FORM ==========
if st.session_state.applicant_analysis is None:
    st.markdown("### 📋 Let's See How You Match Up")
    st.markdown("Paste any job description below and upload your resume. I'll tell you exactly how well you fit and what you can improve.")
    
    with st.form("applicant_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📄 The Job You Want")
            job_desc = st.text_area(
                "Paste the full job description here",
                height=250,
                placeholder="e.g., We are looking for a Senior Software Engineer with experience in Python, cloud architecture, and team leadership...",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("#### 📎 Your Resume")
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload your resume",
                type="pdf",
                label_visibility="collapsed"
            )
            if uploaded_file:
                st.success(f"✅ Ready to analyze: {uploaded_file.name}")
            else:
                st.markdown("📄 Click or drag your PDF here")
                st.caption("We only accept PDF files — they're the most reliable format.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🔍 Analyze My Resume", use_container_width=True)
        
        if submitted:
            if not job_desc:
                st.warning("📋 Please paste a job description first — I need something to compare your resume to!")
            elif not uploaded_file:
                st.warning("📎 Please upload your resume — I can't analyze what I can't see!")
            else:
                with st.spinner("🔍 Analyzing your resume... I'm comparing it to the job description..."):
                    resume_text = utils.extract_text_from_pdf(uploaded_file)
                    
                    if not resume_text or len(resume_text) < 50:
                        st.error("🤔 I couldn't read much text from your PDF. It might be a scanned image. Try uploading a text-based PDF for best results.")
                    else:
                        analysis = utils.get_resume_analysis(resume_text, job_desc)
                        st.session_state.applicant_analysis = analysis
                        st.session_state.applicant_job_desc = job_desc
                        
                        # Save to database so HR can find you
                        success = utils.save_applicant_data(uid, resume_text, analysis, uploaded_file.name)
                        
                        if success:
                            st.success("✅ Analysis complete! Your resume has been saved to your profile.")
                        else:
                            st.info("✅ Analysis complete! (Note: Your results weren't saved to the cloud, but you can still see them here.)")
                        
                        st.rerun()

# ========== RESULTS DISPLAY ==========
else:
    analysis = st.session_state.applicant_analysis
    score = analysis['match_score']
    
    # Determine score category with friendly language
    if score >= 80:
        score_color = "#28a745"
        score_emoji = "🎉"
        score_message = "Outstanding match!"
        score_detail = "You're an excellent fit for this role. Your resume aligns really well with what they're looking for."
    elif score >= 65:
        score_color = "#4A90E2"
        score_emoji = "👍"
        score_message = "Strong match!"
        score_detail = "You're a good fit. A few tweaks to your resume could make you even stronger."
    elif score >= 50:
        score_color = "#f39c12"
        score_emoji = "🔧"
        score_message = "Decent match, room to grow"
        score_detail = "You have some relevant experience, but there are gaps you should address before applying."
    else:
        score_color = "#dc3545"
        score_emoji = "💪"
        score_message = "This one needs work"
        score_detail = "Your resume doesn't align well with this job. Don't worry — check out the tips below to improve!"
    
    # Score Display
    st.markdown(f"""
    <div class="result-card" style="text-align: center;">
        <span style="font-size: 3rem;">{score_emoji}</span>
        <div style="font-size: 3rem; font-weight: 800; color: {score_color}; margin: 0.5rem 0;">{score:.1f}%</div>
        <div style="font-size: 1.3rem; font-weight: 600; color: #1a1a2e;">{score_message}</div>
        <p style="color: #666; margin-top: 0.5rem;">{score_detail}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Gauge Chart
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={'suffix': "%", 'font': {'size': 32}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': score_color, 'thickness': 0.2},
                'steps': [
                    {'range': [0, 50], 'color': "#f8d7da"},
                    {'range': [50, 75], 'color': "#fff3cd"},
                    {'range': [75, 100], 'color': "#d4edda"}
                ]
            },
            title={'text': "Your Match Score", 'font': {'size': 16}}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Skills Section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Skills You Have")
        st.markdown("*These skills from the job description appear in your resume:*")
        if analysis['matching_skills']:
            for skill in analysis['matching_skills']:
                st.markdown(f'<span class="skill-tag skill-match">✓ {skill}</span>', unsafe_allow_html=True)
        else:
            st.info("I didn't find any exact skill matches. Try adding keywords from the job description to your resume.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Skills You're Missing")
        st.markdown("*These are in the job description but missing from your resume:*")
        if analysis['missing_keywords']:
            for keyword in analysis['missing_keywords']:
                st.markdown(f'<span class="skill-tag skill-missing">✗ {keyword}</span>', unsafe_allow_html=True)
        else:
            st.success("Great news! You're not missing any critical keywords from this job description.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Improvement Tips
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### 💡 How to Improve Your Resume")
    st.markdown("*Here's what I suggest to boost your match score:*")
    st.info(analysis.get('improvement_tips', 'Focus on adding keywords from the job description and highlighting relevant experience.'))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Try Another Job", use_container_width=True):
            st.session_state.applicant_analysis = None
            st.rerun()
    with col3:
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.applicant_analysis = None
            logout()