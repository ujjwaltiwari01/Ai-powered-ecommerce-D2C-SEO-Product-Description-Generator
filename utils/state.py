"""Session state management for the application."""
import streamlit as st
from typing import Dict, Any, Optional, List

class SessionState:
    """Manages the application's session state."""

    @staticmethod
    def initialize():
        """Initialize the session state with default values."""
        if 'initialized' not in st.session_state:
            # App state
            st.session_state.initialized = True
            st.session_state.current_step = 1
            st.session_state.max_steps = 3
            
            # Form data
            st.session_state.form_data = {
                'product_info': {},
                'marketplace_info': {}
            }
            
            # AI settings
            st.session_state.ai_settings = {
                'language': 'en',
                'tone': 'professional',
                'creativity': 0.7,
                'model': 'gpt-4-1106-preview',
                'vision_model': 'gpt-4-vision-preview'
            }
            
            # UI state
            st.session_state.ui = {
                'active_tab': 'product_info',
                'show_preview': False,
                'is_processing': False
            }
            
            # Results
            st.session_state.results = {}
            st.session_state.generated_content = {}
    
    @staticmethod
    def update_form_data(section: str, data: Dict[str, Any]):
        """Update form data in the session state."""
        if section not in st.session_state.form_data:
            st.session_state.form_data[section] = {}
        st.session_state.form_data[section].update(data)
    
    @staticmethod
    def get_form_data(section: str, key: str, default: Any = None) -> Any:
        """Get a value from form data."""
        return st.session_state.form_data.get(section, {}).get(key, default)
    
    @staticmethod
    def set_ui_state(key: str, value: Any):
        """Update UI state."""
        st.session_state.ui[key] = value
    
    @staticmethod
    def get_ui_state(key: str, default: Any = None) -> Any:
        """Get a UI state value."""
        return st.session_state.ui.get(key, default)
    
    @staticmethod
    def set_ai_setting(key: str, value: Any):
        """Update AI settings."""
        st.session_state.ai_settings[key] = value
    
    @staticmethod
    def get_ai_setting(key: str, default: Any = None) -> Any:
        """Get an AI setting value."""
        return st.session_state.ai_settings.get(key, default)
    
    @staticmethod
    def set_generated_content(marketplace: str, content_type: str, content: Any):
        """Store generated content."""
        if marketplace not in st.session_state.generated_content:
            st.session_state.generated_content[marketplace] = {}
        st.session_state.generated_content[marketplace][content_type] = content
    
    @staticmethod
    def get_generated_content(marketplace: str, content_type: str, default: Any = None) -> Any:
        """Get generated content."""
        return st.session_state.generated_content.get(marketplace, {}).get(content_type, default)

# Alias for backward compatibility
initialize_session_state = SessionState.initialize
