# home.py
import streamlit as st

# Handle Google OAuth callback
query_params = st.query_params
if "code" in query_params:
    import os, requests, time
    from dotenv import load_dotenv
    from auth import save_user_to_firestore
    load_dotenv()

    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:8501"

    code = query_params["code"]
    role = query_params.get("state", st.session_state.get("login_role", "applicant"))

    try:
        token_resp = requests.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }).json()

        if "access_token" in token_resp:
            user_resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_resp['access_token']}"}
            ).json()

            if "email" in user_resp:
                st.session_state.user = {
                    "uid": user_resp.get("sub", ""),
                    "email": user_resp.get("email", ""),
                    "name": user_resp.get("name", "User"),
                    "picture": user_resp.get("picture", "")
                }
                st.session_state.role = role
                save_user_to_firestore(st.session_state.user, role)
                st.query_params.clear()

                if role == "hr":
                    st.switch_page("pages/2_HR_Dashboard.py")
                else:
                    st.switch_page("pages/1_Applicant.py")
    except Exception as e:
        st.error(f"Login error: {e}")
        st.stop()
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Resume Analyzer", page_icon="🎯", layout="wide")

# ========== MODERN STYLING ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .hero {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 40px;
        margin-bottom: 3rem;
    }
    
    .hero h1 {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .hero p {
        font-size: 1.2rem;
        color: #666;
        margin: 1rem 0 0.5rem 0;
    }
    
    .hero-date {
        color: #aaa;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .role-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .role-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .role-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .role-icon {
        width: 80px;
        height: 80px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2.5rem;
    }
    
    .role-icon.applicant { background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%); color: white; }
    .role-icon.recruiter { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    
    .role-card h2 { font-size: 1.8rem; font-weight: 700; margin: 0 0 1rem 0; color: #1a1a2e; }
    .role-card p { color: #666; line-height: 1.6; margin-bottom: 1rem; }
    
    .role-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .badge-applicant { background: #4A90E2; color: white; }
    .badge-recruiter { background: #667eea; color: white; }
    
    .features { margin-top: 4rem; text-align: center; }
    .features h3 { font-size: 1.5rem; color: #1a1a2e; margin-bottom: 2rem; }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
    
    .feature-item {
        padding: 1.5rem;
        background: #fafafa;
        border-radius: 16px;
    }
    
    .feature-icon { font-size: 1.5rem; margin-bottom: 0.75rem; }
    .feature-item h4 { font-size: 1rem; font-weight: 600; color: #1a1a2e; margin: 0 0 0.5rem 0; }
    .feature-item p { font-size: 0.85rem; color: #888; margin: 0; }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border: none !important;
        font-size: 1rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ========== HERO SECTION ==========
current_date = datetime.now()

st.markdown(f"""
<div class="hero">
    <h1>🎯 Resume Analyzer</h1>
    <p>Your intelligent partner for smarter hiring and job applications</p>
    <p class="hero-date">{current_date.strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)

# ========== WELCOME MESSAGE ==========
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem; color: #555; font-size: 1.1rem;">
    <p>Whether you're <strong>looking for a job</strong> or <strong>looking for talent</strong>, we've got you covered.</p>
    <p style="font-size: 0.9rem; color: #888;">Choose your path below to get started 👇</p>
</div>
""", unsafe_allow_html=True)

# ========== ROLE SELECTION ==========
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="role-card">
        <div class="role-icon applicant">👔</div>
        <h2>I'm Looking for a Job</h2>
        <p>Upload your resume, match it with any job description, and get <strong>personalized tips</strong> to improve your chances.</p>
        <span class="role-badge badge-applicant">Job Seeker</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎯 Start as Applicant", key="applicant_btn", use_container_width=True):
        st.session_state.login_role = "applicant"
        st.switch_page("pages/3_Login.py")

with col2:
    st.markdown("""
    <div class="role-card">
        <div class="role-icon recruiter">🏢</div>
        <h2>I'm Hiring</h2>
        <p>Post your job description and see how applicants match — ranked, scored, and summarized. <strong>No more manual screening.</strong></p>
        <span class="role-badge badge-recruiter">Hiring Manager</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Start as HR", key="recruiter_btn", use_container_width=True):
        st.session_state.login_role = "hr"
        st.switch_page("pages/3_Login.py")

# ========== FEATURES SECTION ==========
st.markdown("""
<div class="features">
    <h3>✨ Why People Love This Tool</h3>
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <h4>AI That Understands Context</h4>
            <p>Not just keywords — we understand the meaning behind your experience</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <h4>Beautiful Visual Reports</h4>
            <p>See your match at a glance with intuitive charts and metrics</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <h4>Results in Seconds</h4>
            <p>Upload, click, done. No waiting around</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <h4>Your Data is Private</h4>
            <p>Nothing is shared without your permission</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown(f"""
<div style="text-align: center; margin-top: 4rem; padding: 2rem 0; border-top: 1px solid #f0f0f0;">
    <p style="color: #aaa; font-size: 0.85rem;">— © {current_date.year} Resume Analyzer · Built with ❤️ —</p>
</div>
""", unsafe_allow_html=True)