"""
app.py — Streamlit frontend
Run: streamlit run app.py
"""

import os
import json
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # load .env locally

from backend.generator import generate_script
from exports.exporter import script_to_pdf_bytes

st.set_page_config(page_title="Microlearning Script Creator", layout="centered")

st.title("🎬 Microlearning Explainer Script Creator")
st.markdown("Create 1–2 minute explainer video scripts (narration + scene visuals).")

with st.form("inputs"):
    topic = st.text_input("Topic", placeholder="e.g., Quantum Computing, Tax Basics, Climate Change")
    audience = st.selectbox("Target audience", ["general public", "school students", "professionals", "kids (ELI10)"])
    difficulty = st.selectbox("Difficulty level", ["beginner", "intermediate"])
    tone = st.selectbox("Style / Tone", ["informal", "funny", "formal", "motivational"])
    language = st.selectbox("Language", ["English", "Hindi", "Spanish"])
    target_seconds = st.slider("Target total length (seconds)", min_value=60, max_value=120, value=90, step=5)
    submitted = st.form_submit_button("Generate Script")

if submitted:
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        with st.spinner("Generating script — contacting Gemini Flash..."):
            try:
                script = generate_script(
                    topic=topic,
                    audience=audience,
                    difficulty=difficulty,
                    tone=tone,
                    language=language,
                    target_seconds=target_seconds,
                )
            except Exception as e:
                st.error(f"Failed to generate script: {e}")
                st.stop()

        st.success("Script generated!")
        st.markdown(f"### {script.get('title','Untitled')}")
        st.write(f"**Estimated total length:** {script.get('total_seconds','?')} seconds")

        for s in script.get("scenes", []):
            with st.expander(f"Scene {s.get('scene')}: {s.get('heading')} ({s.get('est_seconds')}s)"):
                st.markdown(f"**Narration:**\n\n{s.get('narration')}")
                st.markdown("**Visuals suggestions:**")
                for v in s.get("visuals", []):
                    st.write(f"- {v}")

        # PDF export
        pdf_bytes = script_to_pdf_bytes(script)
        st.download_button(
            label="Download script as PDF",
            data=pdf_bytes,
            file_name=f"{topic[:30].strip().replace(' ','_')}_script.pdf",
            mime="application/pdf"
        )
