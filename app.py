"""
AI Marketplace Product Description Engine
Streamlit-based web application for generating product descriptions optimized for various marketplaces.
"""
import os
import json
import logging
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables (override system/user env so project .env wins)
load_dotenv(override=True)

# Set page config
st.set_page_config(
    page_title="AI Product Description Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components after setting page config
from components.layout import render_layout
from components.sidebar import render_sidebar
from components.forms import ProductForm
from utils.state import initialize_session_state, SessionState
from utils.ai_services import ai_service
from services.marketplace_service import marketplace_service
from utils.file_utils import process_image_upload, validate_file_type, SUPPORTED_IMAGE_TYPES, SUPPORTED_AUDIO_TYPES

# Initialize session state
initialize_session_state()

# Logger
logger = logging.getLogger(__name__)

# Initialize services
if 'ai_service' not in st.session_state:
    st.session_state.ai_service = ai_service

if 'marketplace_service' not in st.session_state:
    st.session_state.marketplace_service = marketplace_service

def process_image():
    """Process the uploaded image using AI."""
    if 'uploaded_image' in st.session_state and st.session_state.uploaded_image is not None:
        with st.spinner("Analyzing image..."):
            # Process the image
            image_data = st.session_state.uploaded_image.read()
            
            # Analyze the image
            result = st.session_state.ai_service.analyze_image(image_data)
            
            if result["success"]:
                st.session_state.image_analysis = result["analysis"]
                
                # Update form fields with extracted data if available
                try:
                    analysis_data = json.loads(result["analysis"])
                    if 'product_name' in analysis_data and not st.session_state.get('product_name'):
                        st.session_state.product_name = analysis_data['product_name']
                    if 'brand_name' in analysis_data and not st.session_state.get('brand_name'):
                        st.session_state.brand_name = analysis_data['brand_name']
                    if 'features' in analysis_data and not st.session_state.get('features'):
                        st.session_state.features = analysis_data['features']
                except json.JSONDecodeError:
                    # If the response isn't JSON, just show it as is
                    st.session_state.image_analysis = result["analysis"]
            else:
                st.error(f"Error analyzing image: {result.get('error', 'Unknown error')}")


def process_audio():
    """Process the uploaded audio using Whisper."""
    live_obj = st.session_state.get('audio_note_live')
    file_obj = st.session_state.get('audio_note')
    if live_obj is not None or file_obj is not None:
        with st.spinner("Transcribing audio..."):
            if live_obj is not None:
                if isinstance(live_obj, (bytes, bytearray)):
                    audio_bytes = bytes(live_obj)
                    file_ext = 'wav'
                else:
                    audio_bytes = live_obj.getvalue() if hasattr(live_obj, 'getvalue') else getattr(live_obj, 'read', lambda: b'')()
                    mime = getattr(live_obj, 'type', None)
                    if mime and '/' in mime:
                        file_ext = mime.split('/')[-1]
                    else:
                        file_ext = 'wav'
            else:
                audio_bytes = file_obj.read()
                name = getattr(file_obj, 'name', '') or ''
                file_ext = name.split('.')[-1] if '.' in name else None
            
            result = st.session_state.ai_service.transcribe_audio(audio_bytes, file_ext)
            
            if result["success"]:
                st.session_state.audio_transcript = result["text"]
                
                # If we have features in the transcript, update the features
                if 'features' not in st.session_state or not st.session_state.features:
                    # Simple heuristic to extract features from transcript
                    lines = [line.strip() for line in result["text"].split('\n') if line.strip()]
                    st.session_state.features = lines[:5]  # Take first 5 lines as features
            else:
                st.error(f"Error transcribing audio: {result.get('error', 'Unknown error')}")


def _export_as_markdown(content: dict) -> str:
    """Convert content to Markdown format."""
    markdown = f"# {content.get('title', '')}\n\n"
    markdown += f"{content.get('description', '')}\n\n"
    
    if content.get('bullet_points'):
        markdown += "## Key Features\n"
        markdown += "\n".join([f"- {bp}" for bp in content["bullet_points"]]) + "\n\n"
    
    if content.get('specifications'):
        markdown += "## Specifications\n"
        for key, value in content["specifications"].items():
            markdown += f"- **{key}:** {value}\n"
        markdown += "\n"
    
    if content.get('keywords'):
        markdown += f"## SEO Keywords\n{', '.join(content['keywords'])}\n"
    
    return markdown

def _export_as_json(content: dict) -> str:
    """Convert content to JSON format."""
    import json
    return json.dumps(content, indent=2, ensure_ascii=False)

def _copy_to_clipboard(content: str) -> bool:
    """Copy content to clipboard."""
    try:
        import pyperclip
        pyperclip.copy(content)
        return True
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {str(e)}")
        return False

def generate_descriptions():
    """Generate product descriptions for selected marketplaces."""
    if 'selected_marketplaces' not in st.session_state or not st.session_state.selected_marketplaces:
        st.error("Please select at least one marketplace.")
        return False
    
    try:
        # Read the full product_info section from session state
        all_forms = getattr(st.session_state, 'form_data', {})
        form_data = all_forms.get('product_info', {}) if isinstance(all_forms, dict) else {}
        basic = form_data.get('basic_info', {}) if isinstance(form_data, dict) else {}
        features_fd = form_data.get('features', []) if isinstance(form_data, dict) else []
        # Prepare product info
        product_info = {
            "basic_info": {
                "brand_name": (st.session_state.get('brand_name') or basic.get('brand_name') or '').strip(),
                "product_name": (st.session_state.get('product_name') or basic.get('product_name') or '').strip(),
                "category": (st.session_state.get('category') or basic.get('category') or '').strip(),
                "description": (st.session_state.get('description') or basic.get('description') or '').strip(),
                "target_audience": (st.session_state.get('target_audience') or basic.get('target_audience') or '').strip(),
                "price": None,  # set below after computing
                "currency": (st.session_state.get('currency') or basic.get('currency') or 'USD'),
                "usp": (st.session_state.get('usp') or basic.get('usp') or '').strip(),
                "material_care": st.session_state.get('material_care', '').strip(),
                "usage_instructions": st.session_state.get('usage_instructions', '').strip(),
                "ingredients": st.session_state.get('ingredients', '').strip(),
                "additional_notes": st.session_state.get('additional_notes', '').strip()
            },
            "features": [f.strip() for f in (st.session_state.get('features') or features_fd or []) if f and str(f).strip()],
            "usps": [f.strip() for f in st.session_state.get('usps', []) if f.strip()],
            "specifications": st.session_state.get('specifications', {})
        }

        # Resolve price from session or saved form data
        price_candidate = st.session_state.get('price')
        if price_candidate in (None, "", 0):
            price_candidate = basic.get('price')
        try:
            product_info["basic_info"]["price"] = float(price_candidate) if price_candidate not in (None, "") else None
        except Exception:
            product_info["basic_info"]["price"] = None
        
        # Validate required fields
        if not product_info["basic_info"]["product_name"]:
            st.error("Product name is required.")
            return False
            
        if not product_info["basic_info"]["description"]:
            st.error("Product description is required.")
            return False
            
        if not product_info["features"]:
            st.error("Please add at least one product feature.")
            return False
        
        # Get selected marketplaces
        marketplace_keys = [m['key'] for m in st.session_state.selected_marketplaces]

        # Pre-validate price if any selected marketplace requires it
        templates = getattr(st.session_state.marketplace_service, 'MARKETPLACE_TEMPLATES', {})
        any_requires_price = any(
            templates.get(k, {}).get('requires_price') for k in marketplace_keys
        )
        if any_requires_price and not product_info["basic_info"].get("price"):
            st.error("Price is required for one or more selected marketplaces. Please enter a valid price in Step 1.")
            return False
        
        # Generate content for each marketplace
        with st.spinner("Generating descriptions..."):
            result = st.session_state.marketplace_service.generate_all_marketplace_content(
                product_info, 
                marketplace_keys
            )
            
            if result.get("success", False):
                st.session_state.generated_content = result.get("results", {})
                
                # Check for any failed generations
                failed = [k for k, v in st.session_state.generated_content.items() 
                         if not v.get("success", False)]
                
                if failed and len(failed) == len(marketplace_keys):
                    # All generations failed
                    error_msg = "Failed to generate content for all marketplaces. "
                    error_msg += "Please check your input and try again."
                    st.error(error_msg)
                    return False
                elif failed:
                    # Some generations failed
                    st.warning(
                        f"Generated content with {len(failed)} errors. "
                        f"Failed for: {', '.join(failed)}"
                    )
                
                # Store successful generations
                st.session_state.successful_generations = {
                    k: v for k, v in st.session_state.generated_content.items()
                    if v.get("success", False)
                }
                
                # Move to results step
                st.session_state.current_step = 3
                st.rerun()
                return True
            else:
                error_msg = result.get("error", "Unknown error occurred while generating content.")
                st.error(f"Error: {error_msg}")
                return False
                
    except ValueError as ve:
        st.error(f"Invalid input value: {str(ve)}")
        return False
    except Exception as e:
        logger.exception("Error generating descriptions")
        st.error(f"An unexpected error occurred: {str(e)}")
        return False


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Set callbacks
    if 'uploaded_image' in st.session_state and st.session_state.uploaded_image is not None:
        process_image()
    
    if (st.session_state.get('audio_note') is not None) or (st.session_state.get('audio_note_live') is not None):
        process_audio()
    
    # Handle form submissions
    if st.session_state.get('current_step') == 1 and 'product_form_submitted' in st.session_state:
        if st.session_state.product_form_submitted:
            st.session_state.current_step = 2
            st.rerun()
    
    if st.session_state.get('current_step') == 2 and 'marketplace_form_submitted' in st.session_state:
        if st.session_state.marketplace_form_submitted:
            generate_descriptions()
    
    # Render UI
    render_sidebar()
    render_layout()
    
    # Debug session state
    if st.session_state.get('debug', False):
        with st.sidebar.expander("Debug Info"):
            st.json({k: v for k, v in st.session_state.items() if k != 'uploaded_image' and k != 'audio_note'})

if __name__ == "__main__":
    main()
