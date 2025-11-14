"""
Form components for the AI Product Description Generator.
"""
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import base64

# Import utilities
from utils.file_utils import (
    validate_file_type, 
    SUPPORTED_IMAGE_TYPES, 
    SUPPORTED_AUDIO_TYPES,
    get_file_extension
)

class ProductForm:
    """Handles the product form UI and data collection."""
    
    def __init__(self):
        """Initialize the product form with default values."""
        if 'product_data' not in st.session_state:
            st.session_state.product_data = {
                'basic_info': {
                    'brand_name': '',
                    'product_name': '',
                    'category': '',
                    'description': '',
                    'target_audience': '',
                    'price': 0.0,
                    'currency': 'USD',
                    'usp': ''
                },
                'features': [],
                'specifications': {},
                'images': [],
                'audios': [],
                'selected_marketplaces': []
            }
    
    def render(self) -> Dict[str, Any]:
        """
        Render the product form and return the collected data.
        
        Returns:
            Dict containing the form data
        """
        st.header("Product Information")
        
        # Basic Information
        with st.expander("Basic Information", expanded=True):
            cols = st.columns(2)
            with cols[0]:
                st.session_state.product_data['basic_info']['brand_name'] = st.text_input(
                    "Brand Name",
                    value=st.session_state.product_data['basic_info']['brand_name'],
                    help="The brand or manufacturer of the product"
                )
                
                st.session_state.product_data['basic_info']['product_name'] = st.text_input(
                    "Product Name *",
                    value=st.session_state.product_data['basic_info']['product_name'],
                    help="The name of the product (required)"
                )
                
                st.session_state.product_data['basic_info']['category'] = st.text_input(
                    "Category",
                    value=st.session_state.product_data['basic_info']['category'],
                    help="e.g., Electronics, Fashion, Home & Kitchen"
                )
            
            with cols[1]:
                st.session_state.product_data['basic_info']['price'] = st.number_input(
                    "Price",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=st.session_state.product_data['basic_info']['price'],
                    help="Product price in the selected currency"
                )
                
                st.session_state.product_data['basic_info']['currency'] = st.selectbox(
                    "Currency",
                    ["USD", "INR", "EUR", "GBP"],
                    index=["USD", "INR", "EUR", "GBP"].index(
                        st.session_state.product_data['basic_info']['currency']
                    ) if st.session_state.product_data['basic_info']['currency'] else 0
                )
        
        # Product Description
        st.subheader("Product Details")
        st.session_state.product_data['basic_info']['description'] = st.text_area(
            "Product Description *",
            value=st.session_state.product_data['basic_info']['description'],
            height=150,
            help="Detailed description of the product (required)"
        )
        
        st.session_state.product_data['basic_info']['usp'] = st.text_area(
            "Unique Selling Proposition (USP)",
            value=st.session_state.product_data['basic_info']['usp'],
            height=80,
            help="What makes this product unique?"
        )
        
        # Features
        st.subheader("Product Features")
        st.write("Add key features or specifications (one per line):")
        
        features = st.text_area(
            "Features (one per line)",
            value="\n".join(st.session_state.product_data['features']),
            height=100,
            help="List the key features or specifications of the product"
        )
        st.session_state.product_data['features'] = [f.strip() for f in features.split('\n') if f.strip()]
        
        # Marketplaces
        st.subheader("Target Marketplaces")
        st.write("Select the marketplaces you want to generate descriptions for:")
        
        marketplace_options = [
            {"key": "amazon_in", "name": "Amazon India"},
            {"key": "amazon_us", "name": "Amazon US"},
            {"key": "flipkart", "name": "Flipkart"},
            {"key": "meesho", "name": "Meesho"},
            {"key": "myntra", "name": "Myntra"},
            {"key": "ajio", "name": "Ajio"},
            {"key": "nykaa", "name": "Nykaa"},
            {"key": "walmart", "name": "Walmart"},
            {"key": "noon", "name": "Noon"},
            {"key": "shopify", "name": "Shopify"},
            {"key": "etsy", "name": "Etsy"},
            {"key": "instagram", "name": "Instagram"},
            {"key": "facebook", "name": "Facebook Marketplace"},
            {"key": "google_shopping", "name": "Google Shopping"}
        ]
        
        selected_marketplaces = []
        cols = st.columns(3)
        for i, marketplace in enumerate(marketplace_options):
            with cols[i % 3]:
                if st.checkbox(
                    marketplace["name"],
                    key=f"marketplace_{marketplace['key']}",
                    value=marketplace["key"] in [m["key"] for m in st.session_state.product_data['selected_marketplaces']]
                ):
                    selected_marketplaces.append(marketplace)
        
        st.session_state.product_data['selected_marketplaces'] = selected_marketplaces
        
        # Media Uploads
        st.subheader("Media Uploads")
        
        # Image Upload
        uploaded_image = st.file_uploader(
            "Upload Product Image (optional)",
            type=[ext.replace('.', '') for ext in SUPPORTED_IMAGE_TYPES],
            accept_multiple_files=False
        )
        
        if uploaded_image is not None:
            if validate_file_type(uploaded_image, SUPPORTED_IMAGE_TYPES):
                st.session_state.product_data['images'].append(uploaded_image)
                st.success("Image uploaded successfully!")
            else:
                st.error(f"Unsupported file type. Please upload one of: {', '.join(SUPPORTED_IMAGE_TYPES)}")
        
        # Audio Upload
        uploaded_audio = st.file_uploader(
            "Upload Product Audio Description (optional)",
            type=[ext.replace('.', '') for ext in SUPPORTED_AUDIO_TYPES],
            accept_multiple_files=False
        )
        
        if uploaded_audio is not None:
            if validate_file_type(uploaded_audio, SUPPORTED_AUDIO_TYPES):
                st.session_state.product_data['audios'].append(uploaded_audio)
                st.success("Audio uploaded successfully!")
            else:
                st.error(f"Unsupported file type. Please upload one of: {', '.join(SUPPORTED_AUDIO_TYPES)}")
        
        return st.session_state.product_data

# Marketplace configurations
MARKETPLACES = [
    {"key": "amazon_in", "name": "Amazon India"},
    {"key": "amazon_us", "name": "Amazon US"},
    {"key": "flipkart", "name": "Flipkart"},
    {"key": "meesho", "name": "Meesho"},
    {"key": "myntra", "name": "Myntra"},
    {"key": "ajio", "name": "Ajio"},
    {"key": "nykaa", "name": "Nykaa"},
    {"key": "walmart", "name": "Walmart"},
    {"key": "noon", "name": "Noon"},
    {"key": "shopify", "name": "Shopify"},
    {"key": "etsy", "name": "Etsy"},
    {"key": "instagram", "name": "Instagram"},
    {"key": "facebook", "name": "Facebook Marketplace"},
    {"key": "google_shopping", "name": "Google Shopping"},
]

# Categories for product type
CATEGORIES = [
    "Electronics", "Fashion", "Home & Kitchen", "Beauty & Personal Care", 
    "Books", "Toys & Games", "Sports & Fitness", "Automotive", "Grocery", "Other"
]

# Currencies
CURRENCIES = ["USD", "INR", "EUR", "GBP", "AED", "SAR"]

# Tone options
TONES = ["Professional", "Casual", "Friendly", "Luxury", "Informative", "Persuasive"]

# Language options
LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "Hindi"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "ar", "name": "Arabic"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
]

def render_product_form() -> bool:
    """Render the product information form."""
    with st.form("product_form"):
        st.subheader("Product Information")
        
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Product Name", 
                key="product_name", 
                help="Enter the name of your product",
                value=st.session_state.get('product_name', '')
            )
            
            st.text_input(
                "Brand Name", 
                key="brand_name", 
                help="Enter the brand name",
                value=st.session_state.get('brand_name', '')
            )
            
            st.selectbox(
                "Category", 
                options=[""] + CATEGORIES, 
                key="category", 
                help="Select a category",
                index=CATEGORIES.index(st.session_state.get('category', '')) + 1 if st.session_state.get('category') in CATEGORIES else 0
            )
        
        with col2:
            if st.button("Generate Descriptions 🚀", type="primary"):
                if not selected_marketplaces:
                    st.error("Please select at least one marketplace.")
                    return None
                
                return {
                    "selected_marketplaces": selected_marketplaces
                }
        
        return None
