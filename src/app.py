import streamlit as st
from rag_pipeline import ask_question
from campaign_generator import generate_linkedin_post, generate_cold_email, generate_landing_hero, generate_paid_ad
from scoring_engine import score_campaign

# PAGE SETUP
st.set_page_config(page_title="NexFlow AI Growth Engine", layout="wide")

# DARK THEME
st.markdown("""
<style>
    body { background-color: #0B0F19; }
    .main { background-color: #0B0F19; }
    .hero-title { font-size: 48px; font-weight: 800; color: #FFFFFF; }
    .hero-subtitle { font-size: 18px; color: #9CA3AF; }
    .divider { height: 1px; background: linear-gradient(90deg, transparent, #1F2937, transparent); margin: 30px 0; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    .stTabs [aria-selected="true"] { color: #FFFFFF; border-bottom: 3px solid #3B82F6; }
    div.stButton > button { background: #3B82F6; color: white; font-weight: 700; border-radius: 8px; padding: 0.7em 1.4em; border: none; }
    div.stButton > button:hover { background: #2563EB; }
    .card { background: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1F2937; margin-bottom: 15px; }
    pre { background-color: #111827 !important; border-radius: 12px; padding: 15px !important; border: 1px solid #1F2937; }
    .source-item { background: #111827; padding: 10px 14px; border-radius: 8px; border: 1px solid #1F2937; margin-bottom: 8px; color: #D1D5DB; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<div class="hero-title">NexFlow AI Growth Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Persona-Driven Strategy. Automated Campaign Execution.</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# SESSION STATE (repeat rokne ke liye)
if 'strategy' not in st.session_state:
    st.session_state.strategy = None
if 'score_result' not in st.session_state:
    st.session_state.score_result = None
if 'generated' not in st.session_state:
    st.session_state.generated = False

# SIDEBAR
st.sidebar.header("Campaign Configuration")

persona = st.sidebar.selectbox("Target Persona", ["Enterprise CMO", "Startup Founder", "Marketing Manager"])

campaign_type = st.sidebar.selectbox("Campaign Type", ["Awareness", "Lead Generation", "Product Launch", "Retargeting", "Event Promotion"])

industry = st.sidebar.selectbox("Target Industry", ["B2B SaaS", "FinTech", "Manufacturing", "Logistics", "Professional Services"])

region = st.sidebar.selectbox("Target Region", ["DACH", "Europe", "United States", "Global"])

budget_level = st.sidebar.selectbox("Budget Level", ["Low Budget", "Mid-Range Budget", "Enterprise Budget"])

channel_focus = st.sidebar.selectbox("Primary Channel Focus", ["LinkedIn Only", "Email Only", "Multi-Channel"])

tone_preference = st.sidebar.selectbox("Tone Preference", ["Bold & Aggressive", "Executive & Strategic", "Conversational", "Analytical"])

customer_details = st.sidebar.text_area(
    "Customer Details (optional)",
    placeholder="e.g., Name: XYZ, Vision: Scale e-commerce, Market: North India, Competitors: Zoho",
    height=100
)

if st.sidebar.button("Generate Campaign", type="primary"):
    st.session_state.generated = True
    st.session_state.strategy = None  # reset
    st.rerun()

# TABS
tabs = ["Strategy", "Sources"]

if channel_focus in ["LinkedIn Only", "Multi-Channel"]:
    tabs.insert(1, "LinkedIn Post")

if channel_focus in ["Email Only", "Multi-Channel"]:
    tabs.insert(-1, "Cold Email")

if channel_focus == "Multi-Channel":
    tabs.insert(-1, "Landing Hero")
    tabs.insert(-1, "Paid Ad")

tab_objects = st.tabs(tabs)
tab_dict = dict(zip(tabs, tab_objects))

# GENERATION
if st.session_state.generated:

    query = f"""
Campaign Type: {campaign_type}
Target Industry: {industry}
Target Region: {region}
Budget Level: {budget_level}
Primary Channel Focus: {channel_focus}
Tone Preference: {tone_preference}
Customer Details: {customer_details}
"""

    if st.session_state.strategy is None:
        with st.spinner("Generating..."):
            try:
                strategy = ask_question(user_query=query, persona=persona)
                st.session_state.strategy = strategy
            except Exception as e:
                st.error(f"Generation error: {str(e)}")

    strategy = st.session_state.strategy

    if strategy:
        campaign_config = {"persona": persona, "industry": industry}

        score_result = score_campaign(strategy, campaign_config)

        refinement_count = 0
        while score_result["total_score"] < 75 and refinement_count < 2:
            st.info(f"Refining... (attempt {refinement_count + 1})")
            try:
                refinement_query = query + f"""
Previous score low ({score_result['total_score']}/100).
Improve significantly.
"""
                strategy = ask_question(user_query=refinement_query, persona=persona)
                score_result = score_campaign(strategy, campaign_config)
                refinement_count += 1
            except Exception as e:
                st.error(f"Refinement failed: {str(e)}")
                break

        st.session_state.strategy = strategy
        st.session_state.score_result = score_result

        st.success(f"Final Score: {score_result['total_score']}/100 (after {refinement_count} refinements)")

        # Assets
        linkedin_post = generate_linkedin_post(strategy) if "LinkedIn Post" in tabs else None
        cold_email = generate_cold_email(strategy) if "Cold Email" in tabs else None
        landing_hero = generate_landing_hero(strategy) if "Landing Hero" in tabs else None
        paid_ad = generate_paid_ad(strategy) if "Paid Ad" in tabs else None

        # DISPLAY
        with tab_dict["Strategy"]:
            score = score_result['total_score']

            # Color logic
            if score >= 80:
                color = "#22c55e"
                label = "Excellent"
            elif score >= 60:
                color = "#eab308"
                label = "Good"
            elif score >= 40:
                color = "#f97316"
                label = "Needs Improvement"
            else:
                color = "#ef4444"
                label = "Poor"

            # Compact Score Card
            st.markdown(f"""
            <div style="background: #1e293b; padding: 20px; border-radius: 12px; text-align: center; margin: 15px 0;">
                <h3 style="margin: 0; color: #e2e8f0; font-size: 22px;">Campaign Quality</h3>
                <div style="font-size: 52px; font-weight: bold; color: {color}; margin: 10px 0;">
                    {score}/100
                </div>
                <div style="font-size: 18px; color: {color}; margin-bottom: 15px;">
                    {label}
                </div>
                <div style="background: #334155; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div style="background: {color}; width: {score}%; height: 100%; transition: width 0.8s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Breakdown (compact bars)
            if "breakdown" in score_result:
                st.subheader("Score Breakdown", divider="gray")
                cols = st.columns(2)
                i = 0
                for key, val in score_result["breakdown"].items():
                    if key != "total":
                        percent = min(val / 20 * 100, 100)
                        bar_color = "#22c55e" if percent >= 75 else "#eab308" if percent >= 50 else "#f97316" if percent >= 25 else "#ef4444"

                        with cols[i % 2]:
                            st.markdown(f"**{key.replace('_', ' ').title()}** ({val} pts)")
                            st.progress(percent / 100)
                            st.caption(f"{percent:.0f}%")
                        i += 1

            # Main content (ek baar hi)
            st.markdown(f"""
            <div class="card">
                <h3>Key Insight</h3>
                <p>{strategy.get("key_insight", "No insight generated")}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <h3>Value Proposition</h3>
                <p>{strategy.get("value_proposition", "No value prop")}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <h3>Strategic Angle</h3>
                <p>{strategy.get("strategic_campaign_angle", "No angle generated")}</p>
            </div>
            """, unsafe_allow_html=True)

            if "supporting_proof_points" in strategy and strategy["supporting_proof_points"]:
                proof_html = "<ul>" + "".join(f"<li>{p}</li>" for p in strategy["supporting_proof_points"]) + "</ul>"
                st.markdown(f"""
                <div class="card">
                    <h3>Supporting Proof Points</h3>
                    {proof_html}
                </div>
                """, unsafe_allow_html=True)

        # Other tabs
        if linkedin_post:
            with tab_dict["LinkedIn Post"]:
                st.code(linkedin_post, language="markdown")

        if cold_email:
            with tab_dict["Cold Email"]:
                st.code(cold_email, language="markdown")

        if landing_hero:
            with tab_dict["Landing Hero"]:
                st.code(landing_hero, language="markdown")

        if paid_ad:
            with tab_dict["Paid Ad"]:
                st.code(paid_ad, language="markdown")

        with tab_dict["Sources"]:
            st.subheader("Retrieved Knowledge Sources")
            for s in strategy.get("sources", []):
                st.markdown(f"""
                <div class="source-item">
                    **{s['source']}** ({s['category']})
                </div>
                """, unsafe_allow_html=True)