import streamlit as st
import json
import re
import urllib.parse
import google.generativeai as genai

st.set_page_config(page_title="Moonshadow Generator", page_icon="🌙", layout="centered")

st.title("🌙 Moonshadow YouTube Caption Generator")
st.write("Paste YouTube transcript text below to generate ready-to-tweet posts!")

# Sidebar API Key Input (Prefilled with Streamlit Secret if available)
default_key = st.secrets.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key", value=default_key, type="password")

# Inputs
transcript_input = st.text_area(
    "Paste Transcript / Video Quotes Here", 
    height=200, 
    placeholder="Copy and paste transcript text from YouTube here..."
)

hashtags = st.text_input("Campaign Hashtags", value="#Moonshadow #MoonshadowSeries")
vibe = st.selectbox("Tone / Focus", [
    "Pure Fan Hype & Key Moments",
    "Theory & Plot Suspense",
    "Funny & Meme Quotes",
    "Emotional & Character Dynamic"
])

if st.button("🔥 Generate X Captions", type="primary"):
    if not api_key.strip():
        st.error("Please enter your Gemini API key in the sidebar or save it in Streamlit Secrets.")
    elif not transcript_input.strip():
        st.warning("Please paste transcript text or context from the video.")
    else:
        with st.spinner("Processing transcript with Gemini..."):
            try:
                # 1. Configure the API key FIRST
                genai.configure(api_key=api_key.strip())

                # 2. Safely find an available model OR fall back to gemini-2.5-flash
                selected_model = "gemini-2.5-flash"
                try:
                    available = [
                        m.name for m in genai.list_models() 
                        if 'generateContent' in m.supported_generation_methods
                    ]
                    # Find any available flash model in the account
                    flash_model = next((m for m in available if "flash" in m), None)
                    if flash_model:
                        selected_model = flash_model
                except Exception:
                    # If listing models fails, use the primary current endpoint directly
                    selected_model = "gemini-2.5-flash"

                model = genai.GenerativeModel(selected_model)

                clean_context = transcript_input[:8000]

                prompt = f"""
                You are a social media trend strategist for the TV series 'Moonshadow'.
                Based on the provided YouTube video transcript context, generate 5 short, punchy posts for X (Twitter).

                Guidelines:
                - Keep each post under 220 characters.
                - Match tone: {vibe}.
                - Directly reference quotes, moments, or character dynamics from the text.
                - Always include these hashtags: {hashtags}.
                - Output strictly a valid JSON array of strings containing the 5 posts. Do not include markdown code blocks or extra text.

                Video Context:
                {clean_context}
                """

                response = model.generate_content(prompt)
                raw_content = response.text.strip()

                clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_content, flags=re.MULTILINE)
                captions = json.loads(clean_json)

                st.markdown("---")
                st.subheader("🎉 Ready-to-Post Captions")

                for idx, caption in enumerate(captions, 1):
                    st.markdown(f"**Post #{idx}**")
                    st.code(caption, language=None)
                    
                    encoded_text = urllib.parse.quote(caption)
                    tweet_url = f"https://x.com/intent/tweet?text={encoded_text}"
                    st.link_button("🚀 Tweet this caption", tweet_url)
                    st.write("")

            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
