# -*- coding: utf-8 -*-
import streamlit as st
import os
from google import genai
from google.genai.errors import APIError

# --- Configuration & Styling ---
st.set_page_config(layout="wide", page_title="B2B Content AI Generator MVP")

# Custom CSS for a professional look
st.markdown(
    """
    <style>
    .main-header {
        font-size: 36px !important;
        font-weight: 700;
        color: #007bff; /* Blue for branding */
        margin-bottom: 5px;
    }
    textarea, .stSelectbox {
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True
)
st.markdown('<p class="main-header">Product Update AI Generator</p>', unsafe_allow_html=True)
st.markdown('### Input & Settings')

# --- 1. AI Function: Content Generation ---
def generate_content_with_ai(tech_input, platform, tone, brand_notes, style_sample):
    """
    Calls Gemini API to generate professional content based on inputs.
    """
    try:
        client = genai.Client()

        # Build the prompt
        prompt = f"""
        You are an expert B2B SaaS marketing copywriter. Your task is to transform raw technical changelog entries into engaging, value-driven marketing content.

        **Goal:** Convert the technical log into a professional, high-value content piece for the platform: {platform}.
        **Tone:** {tone}.
        **Brand Notes (if provided):** {brand_notes if brand_notes else 'None provided, focus on general B2B professionalism.'}
        **Style Sample (MUST use this style):**
        ---
        {style_sample}
        ---

        **Raw Technical Log to Convert:**
        {tech_input}

        **Instructions:**
        1. Extract the core customer value from the technical log.
        2. Write a compelling title (maximum 10 words).
        3. Write the full content body, focusing on benefits, not features.
        4. ONLY output the title and content body, using the following exact format:
           TITLE: [Your Title Here]
           CONTENT: [Your Generated Content Body Here]
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        # Parse the output
        output_text = response.text.strip()
        
        # Split title and content based on the defined format
        if "TITLE:" in output_text and "CONTENT:" in output_text:
            title_line = [line for line in output_text.split('\n') if line.startswith('TITLE:')][0]
            content_start_index = output_text.find("CONTENT:") + len("CONTENT:")
            
            generated_title = title_line.replace("TITLE:", "").strip()
            generated_text = output_text[content_start_index:].strip()
            
            return generated_text, generated_title
        else:
            return f"ERROR: AI output format is incorrect. Raw output: {output_text}", "Parsing Error"

    except APIError as e:
        return f"ERROR: Gemini API Error: {e}", "API Error"
    except Exception as e:
        # Generic error fallback for unexpected issues
        return f"ERROR: An unknown error occurred during AI generation. {e}", "Unknown Error"

# --- 2. Streamlit UI: Inputs ---

col_input, col_output = st.columns([0.65, 0.35])

with col_input:
    st.subheader('1. Paste Your Technical Change Log')
    tech_input = st.text_area(
        'Enter Jira/GitHub Logs, Specs, or Bug Fixes here.',
        height=280,
        placeholder="Core Feature Update: Refactored data pipeline to reduce latency by 35% for Enterprise clients. \nBug Fix: Fixed critical currency formatting error for European users. \nNew API Endpoint: Added /api/v2/webhooks for better real-time event delivery."
    )

    st.subheader('2. Output Format & Tone Settings')
    
    col_plat, col_tone = st.columns(2)
    with col_plat:
        platform = st.selectbox(
            'Target Platform',
            ('Blog Post', 'Email Newsletter', 'Social Media Post', 'Internal Memo')
        )
    with col_tone:
        tone = st.selectbox(
            'Tone & Audience',
            ('Professional (SaaS, B2B)', 'Casual (Internal Team)', 'Excited (Product Launch)')
        )
        
    brand_notes = st.text_input(
        "Brand Notes (Optional)",
        placeholder="E.g.: Our core value is 'Collaboration First'",
    )

    # --- 3. Generate Button & Logic (Hard-coded Style) ---
    if st.button('✨ Generate Professional Content Now!'):
        
        # Hard-coded style sample to ensure stability
        fixed_style_sample = """
        Style Principle: Content must be positive, professional, and customer-value centric. Use verbs and numbers to highlight benefits.
        Example Style: In today's fast-moving digital environment, your team needs tools that simplify complexity. We have rebuilt the core architecture so you can achieve your goals with unprecedented speed and reliability.
        """
        
        if not tech_input:
            st.warning("Please enter technical update content before clicking generate!")
        else:
            with st.spinner('AI is generating professional copy based on top SaaS style...'):
                
                # Use the fixed style sample
                final_style_sample = fixed_style_sample

                # Call AI to generate content
                generated_text, generated_title = generate_content_with_ai(
                    tech_input, platform, tone, brand_notes, final_style_sample
                )
                
                # Check for parsing or API errors
                if "ERROR:" in generated_text:
                    st.error(generated_text)
                    st.session_state['generated_content'] = generated_text
                    st.session_state['generated_title'] = generated_title
                else:
                    st.success("Content generation successful! Review output on the right.")
                    # Store generated content in session state
                    st.session_state['generated_content'] = generated_text
                    st.session_state['generated_title'] = generated_title

# --- 4. Streamlit UI: Output & Preview ---
with col_output:
    st.markdown('<p style="font-size:24px; font-weight:600;">✨ Final Output</p>', unsafe_allow_html=True)

    # Initialize session state (using English placeholder to prevent ASCII error)
    if 'generated_content' not in st.session_state:
        st.session_state['generated_content'] = 'Click the button above to generate content.'
        st.session_state['generated_title'] = 'AI Content Preview'

    # Display the title
    st.markdown(f"**TITLE:** {st.session_state['generated_title']}", unsafe_allow_html=True)

    # Display the generated text in a text_area for user editing
    final_text = st.text_area(
        "Generated Content (Review & Edit)",
        value=st.session_state['generated_content'],
        height=450
    )

    st.markdown('---')
    st.subheader('One-Click Export')
    
    # Export Buttons
    col_copy, col_md = st.columns(2)
    with col_copy:
        st.button('Copy Text', help="Copies the final text to clipboard")
        # Note: Streamlit's simple button doesn't copy, this would need custom component
        st.caption("Content ready for copy after generation.")
    
    with col_md:
        st.download_button(
            label="Download Markdown",
            data=final_text,
            file_name=f"{st.session_state['generated_title'].replace(' ', '_').lower()}.md",
            mime="text/markdown"
        )