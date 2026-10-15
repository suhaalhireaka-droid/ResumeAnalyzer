# pages/3_Login.py
import streamlit as st
import os
from dotenv import load_dotenv
import requests
from auth import save_user_to_firestore
import time

load_dotenv()

st.set_page_config(page_title="Sign In", page_icon="🔐", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .login-card {
        max-width: 480px;
        margin: 4rem auto;
        padding: 3rem 2.5rem;
        border-radius: 24px;
        background: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        text-align: center;
    }
    .login-card .icon-circle {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
        color: white;
    }
    .login-card h1 { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.5rem; }
    .login-card .role-badge { display: inline-block; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1.5rem; }
    .badge-applicant { background: #e8f0fe; color: #4A90E2; }
    .badge-recruiter { background: #f0e8fe; color: #7B68EE; }
    .login-card p { color: #666; line-height: 1.6; margin-bottom: 2rem; }
    .google-btn {
        display: flex; align-items: center; justify-content: center; gap: 12px;
        width: 100%; padding: 14px 24px; background: white; border: 2px solid #e0e0e0;
        border-radius: 12px; font-size: 1rem; font-weight: 600; color: #333;
        cursor: pointer; transition: all 0.2s; text-decoration: none;
    }
    .google-btn:hover { border-color: #667eea; background: #f8f9ff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15); }
    .google-btn img { width: 24px; height: 24px; }
    .footer-text { margin-top: 2rem; color: #aaa; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"

# ── DEBUG: show everything ──
query_params = st.query_params
st.write("Query params:", dict(query_params))
st.write("Session state:", dict(st.session_state))

url_state_role = query_params.get("state", None)
role = st.session_state.get("login_role", None) or url_state_role

if url_state_role and not st.session_state.get("login_role"):
    st.session_state.login_role = url_state_role

st.write("Role resolved to:", role)

if role is None:
    st.warning("Please select your role from the home page first.")
    if st.button("🏠 Go to Home"):
        st.switch_page("home.py")
    st.stop()

# ── DEBUG: show everything ──
query_params = st.query_params
st.write("Query params:", dict(query_params))
st.write("Session state:", dict(st.session_state))

url_state_role = query_params.get("state", None)
role = st.session_state.get("login_role", None) or url_state_role

if url_state_role and not st.session_state.get("login_role"):
    st.session_state.login_role = url_state_role

st.write("Role resolved to:", role)

if role is None:
    st.warning("Please select your role from the home page first.")
    if st.button("🏠 Go to Home"):
        st.switch_page("home.py")
    st.stop()

# ── Read query params first, before anything else ──
query_params = st.query_params
url_state_role = query_params.get("state", None)

# Role: prefer session state, fall back to URL state param (survives Google redirect)
role = st.session_state.get("login_role", None) or url_state_role

# If we got role from URL, persist it back into session state
if url_state_role and not st.session_state.get("login_role"):
    st.session_state.login_role = url_state_role

if role is None:
    st.warning("Please select your role from the home page first.")
    if st.button("🏠 Go to Home"):
        st.switch_page("home.py")
    st.stop()

# ── Helper functions ──
def get_google_auth_url():
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": role
    }
    return auth_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    return response.json()

def get_user_info(access_token):
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(userinfo_url, headers=headers)
    return response.json()

# ── Callback: Google redirected back with a code ──
if "code" in query_params:
    code = query_params["code"]

    try:
        token_data = exchange_code_for_token(code)

        if "error" in token_data:
            st.error(f"Google returned an error: {token_data['error']}")

        elif "access_token" in token_data:
            user_info = get_user_info(token_data["access_token"])

            if "email" in user_info:
                st.session_state.user = {
                    "uid": user_info.get("sub", ""),
                    "email": user_info.get("email", ""),
                    "name": user_info.get("name", "User"),
                    "picture": user_info.get("picture", "")
                }
                st.session_state.role = role

                try:
                    success, message = save_user_to_firestore(st.session_state.user, role)
                    st.success(message)
                except Exception as e:
                    st.warning(f"Saved locally but database error: {e}")

                st.balloons()
                time.sleep(1.5)

                if role == "hr":
                    st.switch_page("pages/2_HR_Dashboard.py")
                else:
                    st.switch_page("pages/1_Applicant.py")

            else:
                st.error("Couldn't get your email from Google. Please try again.")

        else:
            st.error("No access token received from Google. Please try again.")

    except Exception as e:
        st.error(f"Something went wrong during sign-in: {e}")

# ── No code in URL: show the login page ──
else:
    role_emoji = "👔" if role == "applicant" else "🏢"
    role_label = "Job Seeker" if role == "applicant" else "Hiring Manager"
    badge_class = "badge-applicant" if role == "applicant" else "badge-recruiter"
    welcome_text = (
        "Get personalized feedback on your resume and see how well you match any job."
        if role == "applicant"
        else "Post job descriptions and see ranked applicants instantly. No more manual screening."
    )

    st.markdown(f"""
    <div class="login-card">
        <div class="icon-circle">{role_emoji}</div>
        <h1>Welcome!</h1>
        <span class="role-badge {badge_class}">{role_label}</span>
        <p>{welcome_text}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        google_url = get_google_auth_url()
        st.markdown(f"""
        <a href="{google_url}" style="text-decoration: none;">
            <div class="google-btn">
                <img src="https://www.google.com/favicon.ico" alt="Google">
                Continue with Google
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-text" style="text-align: center;">
        <p>By signing in, you agree to our Terms of Service.</p>
        <p>🔒 Your data is safe with us. We never share your information.</p>
    </div>
    """, unsafe_allow_html=True)