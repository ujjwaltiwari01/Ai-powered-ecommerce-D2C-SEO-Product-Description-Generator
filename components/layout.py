"""Main layout components for the application."""
import streamlit as st
from utils.state import SessionState

def render_header():
    """Render the page header."""
    st.title("🚀 AI Product Description Generator")
    st.markdown(
        "Generate optimized product descriptions for multiple marketplaces "
        "with AI-powered precision."
    )

def render_progress_bar():
    """Render the progress bar based on current step."""
    current_step = int(st.session_state.get('current_step', 1))
    max_steps = int(st.session_state.get('max_steps', 3))
    max_steps = max(1, max_steps)
    step_clamped = max(1, min(current_step, max_steps))
    progress = step_clamped / max_steps
    
    st.progress(progress)
    st.caption(f"Step {step_clamped} of {max_steps}")

def render_content():
    """Render the main content area based on current step."""
    current_step = st.session_state.get('current_step', 1)
    
    if current_step == 1:
        render_product_info_form()
    elif current_step == 2:
        render_marketplace_selection()
    else:
        render_results()

def render_product_info_form():
    """Render the product information form."""
    st.header("1. Product Information")
    
    with st.form("product_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic Information
            st.subheader("Basic Information")
            brand_name = st.text_input("Brand Name", key="brand_name")
            product_name = st.text_input("Product Name", key="product_name")
            
            # Category Selection
            categories = [
                "Electronics", "Fashion", "Home & Kitchen", "Beauty & Personal Care",
                "Books", "Toys & Games", "Sports & Outdoors", "Automotive",
                "Grocery", "Health & Household", "Pet Supplies", "Office Products",
                "Baby", "Clothing & Accessories", "Shoes & Jewelry", "Tools & Home Improvement"
            ]
            category = st.selectbox("Category", [""] + sorted(categories), key="category")
            
            # Target Audience
            st.subheader("Target Audience")
            target_audience = st.text_area(
                "Describe your ideal customer",
                placeholder="E.g., Tech-savvy professionals aged 25-40...",
                key="target_audience"
            )
        
        with col2:
            # Image Upload
            st.subheader("Product Image (Optional)")
            uploaded_image = st.file_uploader(
                "Upload a product image",
                type=["jpg", "jpeg", "png", "webp"],
                key="product_image"
            )
            
            if uploaded_image is not None:
                st.image(uploaded_image, caption="Uploaded Product Image", use_column_width=True)
            
            # Audio Note (Optional)
            st.subheader("Speak about your product (Optional)")
            audio_note_live = None
            try:
                from st_audiorec import st_audiorec
                audio_note_live = st_audiorec()
                if audio_note_live:
                    st.session_state.audio_note_live = audio_note_live
            except Exception:
                st.info("Microphone recording requires the 'streamlit-audiorec' package. Please install it to enable live recording.")
        
        # Product Details
        st.subheader("Product Details")
        col1, col2 = st.columns(2)
        
        with col1:
            price = st.number_input("Price (Optional)", min_value=0.0, step=0.01, key="price")
            currency = st.selectbox(
                "Currency",
                ["USD", "INR", "EUR", "GBP", "AED", "Other"],
                key="currency"
            )
        
        with col2:
            sku = st.text_input("SKU (Optional)", key="sku")
            asin = st.text_input("ASIN (Optional)", key="asin")
        
        # Product Description
        description = st.text_area(
            "Product Description",
            placeholder="Detailed product description for all marketplaces...",
            key="description",
            height=120,
        )

        # Key Features
        st.subheader("Key Features & Benefits")
        
        # Dynamic features list
        if 'features' not in st.session_state:
            st.session_state.features = [""]
        
        for i, feature in enumerate(st.session_state.features):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.session_state.features[i] = st.text_input(
                    f"Feature {i+1}",
                    value=feature,
                    key=f"feature_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                if st.form_submit_button(f"Remove {i+1} ❌"):
                    st.session_state.features.pop(i)
                    st.rerun()
        
        if st.form_submit_button("➕ Add Another Feature"):
            st.session_state.features.append("")
            st.rerun()
        
        # Unique Selling Proposition
        usp = st.text_area(
            "Unique Selling Proposition (USP)",
            placeholder="What makes your product unique?",
            key="usp"
        )
        
        # Submit button
        submitted = st.form_submit_button("Continue to Marketplace Selection")
        
        if submitted:
            # Validate form
            if not all([brand_name, product_name, category, target_audience]):
                st.error("Please fill in all required fields.")
            elif not any(st.session_state.features):
                st.error("Please add at least one feature.")
            else:
                # Save form data
                form_data = {
                    'basic_info': {
                        'brand_name': brand_name,
                        'product_name': product_name,
                        'category': category,
                        'description': description,
                        'target_audience': target_audience,
                        'price': price if price > 0 else None,
                        'currency': currency,
                        'sku': sku,
                        'asin': asin,
                        'usp': usp
                    },
                    'features': [f for f in st.session_state.features if f],
                    'media': {
                        'image': uploaded_image,
                        'audio': audio_note_live
                    }
                }
                
                SessionState.update_form_data('product_info', form_data)

                st.session_state.current_step = 2
                st.rerun()

def render_marketplace_selection():
    """Render the marketplace selection form."""
    st.header("2. Select Marketplaces")
    
    # Marketplace categories
    marketplace_categories = {
        "Indian Marketplaces": [
            ("Amazon India", "amazon_in"),
            ("Flipkart", "flipkart"),
            ("Meesho", "meesho"),
            ("Myntra (Fashion)", "myntra"),
            ("Ajio (Fashion)", "ajio"),
            ("Nykaa (Beauty)", "nykaa"),
            ("JioMart (Optional)", "jiomart")
        ],
        "US Marketplaces": [
            ("Amazon US", "amazon_us"),
            ("Walmart", "walmart")
        ],
        "UAE / GCC": [
            ("Noon", "noon"),
            ("Amazon UAE", "amazon_ae")
        ],
        "Global Platforms": [
            ("Shopify", "shopify"),
            ("Etsy", "etsy"),
            ("Instagram Caption", "instagram"),
            ("Facebook Marketplace", "facebook"),
            ("Google Shopping Feed", "google_shopping")
        ]
    }
    
    # Display marketplace selection
    selected_marketplaces = []
    
    for category, marketplaces in marketplace_categories.items():
        st.subheader(category)
        
        # Create columns for better layout
        cols = st.columns(3)
        
        for i, (name, key) in enumerate(marketplaces):
            with cols[i % 3]:
                if st.checkbox(name, key=f"marketplace_{key}"):
                    selected_marketplaces.append({"name": name, "key": key})
    
    # Navigation buttons
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("← Back"):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("Generate Descriptions 🚀", type="primary"):
            if not selected_marketplaces:
                st.error("Please select at least one marketplace.")
            else:
                # Save selected marketplaces
                SessionState.update_form_data('marketplace_info', {
                    'selected_marketplaces': selected_marketplaces
                })
                # Also set into session for generator
                st.session_state.selected_marketplaces = selected_marketplaces
                # Signal app to generate
                st.session_state.marketplace_form_submitted = True
                st.rerun()

def render_results():
    """Render the generated content results."""
    st.header("🎉 Generated Descriptions")
    
    # Show selected marketplaces
    marketplaces = SessionState.get_form_data('marketplace_info', 'selected_marketplaces', [])
    
    if not marketplaces:
        st.warning("No marketplaces selected. Please go back and select at least one marketplace.")
        if st.button("← Back to Marketplace Selection"):
            st.session_state.current_step = 2
            st.rerun()
        return
    
    generated = st.session_state.get('successful_generations') or st.session_state.get('generated_content', {})
    tabs = st.tabs([mp['name'] for mp in marketplaces])
    for (marketplace, tab) in zip(marketplaces, tabs):
        with tab:
            key = marketplace['key']
            data = generated.get(key, {}) if isinstance(generated, dict) else {}
            st.subheader(f"{marketplace['name']} Description")
            if not data or not data.get('success', False):
                st.info("No generated content available yet. Use Regenerate to try again.")
            else:
                title = data.get('title') or 'Generated Title'
                desc = data.get('description') or ''
                bullets = data.get('bullet_points') or []
                specs = data.get('specifications') or {}

                # Title box
                with st.container(border=True):
                    st.markdown("**Title**")
                    st.write(title)

                # Description box
                with st.container(border=True):
                    st.markdown("**Description**")
                    st.write(desc)

                # Key Features box
                if bullets:
                    with st.container(border=True):
                        st.markdown("**Key Features**")
                        for bp in bullets:
                            st.markdown(f"- {bp}")

                # Specifications box
                if specs:
                    with st.container(border=True):
                        st.markdown("**Specifications**")
                        for k, v in specs.items():
                            st.markdown(f"- **{k}:** {v}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("← Back to Marketplaces"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate All"):
            # Trigger generation again using current selections
            st.session_state.marketplace_form_submitted = True
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        # Prepare JSON data for download
        import json
        json_data = json.dumps(st.session_state.get('successful_generations', {}), ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 Download All as JSON",
            data=json_data,
            file_name="product_descriptions.json",
            mime="application/json"
        )

def render_layout():
    """Main layout renderer."""
    render_header()
    render_progress_bar()
    render_content()
