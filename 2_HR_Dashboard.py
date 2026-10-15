# pages/2_HR_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import utils
from auth import login_required, logout, is_hr

st.set_page_config(page_title="HR Dashboard", page_icon="🏢", layout="wide")

# ========== AUTHENTICATION CHECK ==========
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("👋 Hey! Please sign in first to access the HR dashboard.")
    st.switch_page("pages/3_Login.py?role=hr")

if not is_hr():
    st.error("🚫 This dashboard is for HR professionals only. Applicants should use the Applicant Portal.")
    st.stop()

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
    [data-testid="stSidebar"] .stTextArea textarea {
        color: #1a1a2e !important;
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    
    .candidate-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
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

# ========== HEADER ==========
user_name = st.session_state.user.get("name", "there")

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid #eee; margin-bottom: 2rem;">
    <div>
        <h1 style="font-size: 2rem; font-weight: 700; color: #1a1a2e; margin: 0;">🏢 Hiring Dashboard</h1>
        <p style="color: #666; margin: 0.25rem 0 0 0;">Welcome back, {user_name}. Let's find the best talent.</p>
    </div>
    <span style="color: #888;">👤 {user_name} (HR)</span>
</div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 📋 Your Job Description")
    st.markdown("*Paste the job you're hiring for. Applicants will be ranked against this.*")
    
    job_desc = st.text_area(
        "Job Description",
        height=300,
        placeholder="e.g., We are seeking a Senior Data Analyst with 5+ years experience in Python, SQL, and Tableau...",
        label_visibility="collapsed"
    )
    
    if job_desc:
        uid = st.session_state.user["uid"]
        utils.save_job_description(uid, job_desc)
        st.success("✅ Job description saved!")
    
    st.markdown("---")
    
    st.markdown("### 📊 What You'll See")
    st.markdown("""
    - 📈 Score distribution
    - 🏅 Ranked candidates
    - ✅ Matching skills
    - ⚠️ Missing keywords
    - 📝 AI summaries
    """)
    
    st.markdown("---")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()

# ========== MAIN DASHBOARD ==========
if not job_desc:
    # Friendly empty state
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
        <h2 style="color: #1a1a2e; margin-bottom: 0.5rem;">Ready to Find Great Candidates?</h2>
        <p style="color: #666; margin-bottom: 0.5rem;">Start by pasting your job description in the sidebar 👈</p>
        <p style="color: #888; font-size: 0.9rem;">Once you do, I'll show you all applicants ranked by how well they match.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("---")
    
    # Load applicants
    with st.spinner("🔍 Looking for candidates..."):
        applicants = utils.get_all_applicants()
    
    if not applicants:
        # No applicants yet
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
            <h2 style="color: #1a1a2e; margin-bottom: 0.5rem;">No Applicants Yet</h2>
            <p style="color: #666; margin-bottom: 0.5rem;">Your job description is saved! Now share the app with candidates.</p>
            <p style="color: #888; font-size: 0.9rem;">When applicants upload their resumes, they'll appear here automatically.</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Rescore all applicants against current job
        for applicant in applicants:
            resume_text = ""
            try:
                resumes_ref = utils.db.collection("users").document(applicant["uid"]).collection("resumes").stream()
                for resume in resumes_ref:
                    resume_text = resume.to_dict().get("resume_text", "")
                    break
            except:
                pass
            
            if resume_text:
                new_score = utils.score_resume_local(resume_text, job_desc)
                applicant["match_score"] = new_score
        
        # Create DataFrame and sort
        df = pd.DataFrame(applicants)
        df = df.sort_values(by="match_score", ascending=False).reset_index(drop=True)
        
        # ===== KEY METRICS =====
        st.subheader("📊 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        avg_score = df['match_score'].mean()
        top_score = df['match_score'].max()
        strong_matches = len(df[df['match_score'] >= 70])
        total = len(df)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{total}</div>
                <div style="color: #666; font-size: 0.9rem;">Total Applicants</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{avg_score:.1f}%</div>
                <div style="color: #666; font-size: 0.9rem;">Average Match</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #28a745;">{top_score:.1f}%</div>
                <div style="color: #666; font-size: 0.9rem;">Best Match</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #28a745;">{strong_matches}</div>
                <div style="color: #666; font-size: 0.9rem;">Strong Fit (≥70%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== CHARTS =====
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 How Candidates Score")
            
            if len(df) >= 3:
                fig = px.histogram(
                    df, x="match_score", nbins=min(10, len(df)),
                    title="Score Distribution",
                    color_discrete_sequence=["#667eea"],
                    labels={"match_score": "Match Score (%)", "count": "Number of Candidates"}
                )
                fig.update_layout(bargap=0.1, showlegend=False)
            else:
                fig = px.bar(
                    df, x="name", y="match_score",
                    title="Individual Scores",
                    color="match_score",
                    color_continuous_scale="Blues",
                    text="match_score",
                    labels={"name": "Candidate", "match_score": "Match Score (%)"}
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(yaxis=dict(range=[0, 100]), showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏅 Candidate Rankings")
            
            if len(df) > 0:
                rank_df = df.sort_values("match_score", ascending=True).tail(15)
                
                fig = px.bar(
                    rank_df, x="match_score", y="name",
                    orientation='h',
                    title="Top Candidates",
                    color="match_score",
                    color_continuous_scale="RdYlGn",
                    text="match_score",
                    labels={"name": "", "match_score": "Match Score (%)"}
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(xaxis=dict(range=[0, 100]), showlegend=False, yaxis={'categoryorder': 'total ascending'})
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ===== CANDIDATE DETAILS =====
        st.subheader("📋 Review Each Candidate")
        
        for i, row in df.iterrows():
            score = row['match_score']
            
            if score >= 70:
                score_color = "#28a745"
                score_label = "Strong Match"
            elif score >= 50:
                score_color = "#f39c12"
                score_label = "Potential Fit"
            else:
                score_color = "#dc3545"
                score_label = "Not a Match"
            
            with st.expander(f"#{i+1} | {row['name']} | {score:.1f}% — {score_label}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📧 Email:** {row.get('email', 'Not provided')}")
                    st.markdown(f"**📄 Resume File:** {row.get('filename', 'Unknown')}")
                    
                    st.markdown("**📝 AI Summary:**")
                    st.info(row.get('hr_summary', 'No summary available.'))
                    
                    st.markdown("**✅ Skills They Have:**")
                    skills = row.get('matching_skills', [])
                    if isinstance(skills, str):
                        skills = [s.strip() for s in skills.split(",") if s.strip()]
                    if skills:
                        for skill in skills[:5]:
                            st.markdown(f"<span style='background:#d4edda;color:#155724;padding:4px 10px;border-radius:20px;margin:2px;display:inline-block;font-size:0.85rem;'>✓ {skill}</span>", unsafe_allow_html=True)
                    else:
                        st.caption("No matching skills identified")
                    
                    st.markdown("**⚠️ Skills They're Missing:**")
                    missing = row.get('missing_keywords', [])
                    if isinstance(missing, str):
                        missing = [m.strip() for m in missing.split(",") if m.strip()]
                    if missing:
                        for kw in missing[:5]:
                            st.markdown(f"<span style='background:#f8d7da;color:#721c24;padding:4px 10px;border-radius:20px;margin:2px;display:inline-block;font-size:0.85rem;'>✗ {kw}</span>", unsafe_allow_html=True)
                    else:
                        st.caption("No missing keywords identified")
                
                with col2:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        number={'suffix': "%"},
                        title={'text': score_label},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': score_color},
                            'steps': [
                                {'range': [0, 50], 'color': "#f8d7da"},
                                {'range': [50, 75], 'color': "#fff3cd"},
                                {'range': [75, 100], 'color': "#d4edda"}
                            ]
                        }
                    ))
                    fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"⭐ Save", key=f"save_{i}", use_container_width=True):
                            st.toast(f"✅ {row['name']} saved to your shortlist!", icon="⭐")
                    with col_b:
                        if st.button(f"👎 Skip", key=f"skip_{i}", use_container_width=True):
                            st.toast(f"👎 {row['name']} removed from view.", icon="👋")
        
        # ===== EXPORT =====
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            export_df = df[["name", "email", "match_score", "filename"]]
            export_df.columns = ["Name", "Email", "Match Score", "Resume File"]
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Report (CSV)",
                csv,
                "candidate_rankings.csv",
                "text/csv",
                use_container_width=True
            )