"""Sidebar component for the application."""
import streamlit as st
from utils.state import SessionState

def render_sidebar():
    """Render the sidebar with settings and navigation."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Language selection
        languages = {
            'en': 'English',
            'hi': 'हिंदी',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'ar': 'العربية',
            'ja': '日本語',
            'zh': '中文',
            'pt': 'Português',
            'ru': 'Русский'
        }
        
        selected_lang = st.selectbox(
            "🌍 Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            key="language_selector"
        )
        SessionState.set_ai_setting('language', selected_lang)
        
        # Tone selection
        tone_options = {
            'professional': 'Professional',
            'casual': 'Casual',
            'friendly': 'Friendly',
            'authoritative': 'Authoritative',
            'enthusiastic': 'Enthusiastic'
        }
        
        selected_tone = st.selectbox(
            "🎭 Tone",
            options=list(tone_options.keys()),
            format_func=lambda x: tone_options[x],
            key="tone_selector"
        )
        SessionState.set_ai_setting('tone', selected_tone)
        
        # Creativity level
        creativity = st.slider(
            "✨ Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make the output more creative but less predictable."
        )
        SessionState.set_ai_setting('creativity', creativity)
        
        # Model selection
        model_options = {
            'gpt-4-1106-preview': 'GPT-4 Turbo (Best Quality)',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo (Faster & Cheaper)'
        }
        
        selected_model = st.selectbox(
            "🤖 Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            key="model_selector"
        )
        SessionState.set_ai_setting('model', selected_model)
        
        # Add some space
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        if st.button("🔄 Reset Form"):
            st.session_state.clear()
            SessionState.initialize()
            st.rerun()
            
        # Debug toggle
        if st.checkbox("🐞 Debug Mode"):
            st.session_state.debug = not st.session_state.get('debug', False)
        
        # Version info
        st.markdown("---")
        st.caption("v1.0.0 | AI Product Description Engine")
