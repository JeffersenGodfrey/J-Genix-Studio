import streamlit as st
import os
from dotenv import load_dotenv
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground,
    generate_logo,
    get_logo_style_options,
    get_logo_type_options,
    get_color_scheme_options,
    validate_logo_prompt,
    get_logo_generation_tips,
    enhance_logo_prompt,
    extract_colors_from_image,
    create_brand_kit,
    apply_brand_to_prompt,
    save_brand_kit,
    load_brand_kit,
    get_available_brand_kits,
    validate_brand_kit,
    generate_marketing_copy,
    generate_multiple_copy_variations,
    validate_api_key,
    get_copy_type_options,
    get_tone_options,
    get_length_options,
    generate_marketing_copy_free,
    generate_multiple_copy_variations_free,
    get_copy_type_options_free,
    test_free_copywriter_connection
)
from PIL import Image
import io
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="J-Genix Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Load environment variables
load_dotenv()

# Get API key from environment or Streamlit secrets
def get_api_key():
    """Get API key from environment or Streamlit secrets"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud deployment)
        return st.secrets["BRIA_API_KEY"]
    except:
        # Fall back to environment variable (for local development)
        return os.getenv("BRIA_API_KEY")

api_key = get_api_key()



def initialize_session_state():
    """Initialize session state variables."""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('BRIA_API_KEY')
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'pending_urls' not in st.session_state:
        st.session_state.pending_urls = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = None
    # Logo generation specific state
    if 'original_logo_prompt' not in st.session_state:
        st.session_state.original_logo_prompt = ""
    if 'enhanced_logo_prompt' not in st.session_state:
        st.session_state.enhanced_logo_prompt = None
    if 'logo_enhancement_in_progress' not in st.session_state:
        st.session_state.logo_enhancement_in_progress = False
    if 'logo_enhancement_success' not in st.session_state:
        st.session_state.logo_enhancement_success = False

def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def apply_image_filter(image, filter_type):
    """Apply various filters to the image."""
    try:
        img = Image.open(io.BytesIO(image)) if isinstance(image, bytes) else Image.open(image)
        
        if filter_type == "Grayscale":
            return img.convert('L')
        elif filter_type == "Sepia":
            width, height = img.size
            pixels = img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = img.getpixel((x, y))[:3]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    img.putpixel((x, y), (min(tr, 255), min(tg, 255), min(tb, 255)))
            return img
        elif filter_type == "High Contrast":
            return img.point(lambda x: x * 1.5)
        elif filter_type == "Blur":
            return img.filter(Image.BLUR)
        else:
            return img
    except Exception as e:
        st.error(f"Error applying filter: {str(e)}")
        return None

def check_generated_images():
    """Check if pending images are ready and update the display."""
    if st.session_state.pending_urls:
        ready_images = []
        still_pending = []
        
        for url in st.session_state.pending_urls:
            try:
                response = requests.head(url)
                # Consider an image ready if we get a 200 response with any content length
                if response.status_code == 200:
                    ready_images.append(url)
                else:
                    still_pending.append(url)
            except Exception as e:
                still_pending.append(url)
        
        # Update the pending URLs list
        st.session_state.pending_urls = still_pending
        
        # If we found any ready images, update the display
        if ready_images:
            st.session_state.edited_image = ready_images[0]  # Display the first ready image
            if len(ready_images) > 1:
                st.session_state.generated_images = ready_images  # Store all ready images
            return True
            
    return False

def auto_check_images(status_container):
    """Automatically check for image completion a few times."""
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts and st.session_state.pending_urls:
        time.sleep(2)  # Wait 2 seconds between checks
        if check_generated_images():
            status_container.success("✨ Image ready!")
            return True
        attempt += 1
    return False

def main():
    st.title("J-Genix Studio")

    initialize_session_state()



    # Initialize active tab state
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0

    # Sidebar for API key
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Bria AI API Key:", value=st.session_state.api_key if st.session_state.api_key else "", type="password")
        if api_key:
            st.session_state.api_key = api_key

        # Free AI Copywriter info
        st.subheader("🆓 Free AI Copywriter")
        st.success("✅ **No setup required!** Free copywriter powered by Hugging Face models.")
        st.caption("Generate marketing copy for your images without any API keys or costs.")

    # Check if navigation was triggered - ensure in-app navigation
    if st.session_state.get('navigate_to_logo_tab'):
        # Clear navigation flag immediately to prevent loops
        st.session_state.navigate_to_logo_tab = False

        # Show navigation status
        st.success("🎯 **Successfully Navigated to Logo Generation Interface!**")
        st.info("✅ **Navigation completed in current browser window** - Create your company logo below")

        # Show navigation breadcrumb
        if st.session_state.get('navigation_source') == "brand_kit":
            st.caption("📍 **Navigation Path:** Brand Kit → Logo Generation | Use '← Back to Brand Kit' to return")

        # Add back navigation button
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("← Back to Brand Kit", key="back_to_brand_kit", help="Return to Brand Kit interface"):
                st.session_state.navigate_to_brand_kit_tab = True
                st.session_state.navigation_source = "logo_generation"
                st.rerun()

        with col_title:
            st.header("🏢 Logo Generation")

        st.markdown("**Create professional logos for your brand with AI-powered generation.**")
        st.markdown("---")

        # Display tips
        with st.expander("💡 Logo Generation Tips", expanded=False):
            tips = get_logo_generation_tips()
            for tip in tips:
                st.markdown(f"- {tip}")

        # Logo Generation Form (matching regular tab exactly)
        col1, col2 = st.columns([2, 1])

        with col1:
            # Company/Brand name and preferences input (matching regular tab)
            logo_prompt = st.text_area(
                "Enter your company name and preferences:",
                value="",
                height=100,
                key="direct_logo_prompt_input",
                help="Examples:\n• 'TechCorp software company'\n• 'GreenLeaf organic foods, modern and clean'\n• 'Stellar Fitness gym, bold and energetic, blue colors'\n• 'Artisan Coffee roasters, vintage feel, warm colors'"
            )

            # Initialize session state for logo enhancement
            if "direct_enhanced_logo_prompt" not in st.session_state:
                st.session_state.direct_enhanced_logo_prompt = ""
            if "direct_logo_enhancement_in_progress" not in st.session_state:
                st.session_state.direct_logo_enhancement_in_progress = False

            # Show enhanced prompt if available
            if st.session_state.direct_enhanced_logo_prompt:
                st.markdown("**Enhanced Logo Prompt:**")
                st.markdown(f"*{st.session_state.direct_enhanced_logo_prompt}*")
                st.caption(f"✅ Enhanced prompt ready ({len(st.session_state.direct_enhanced_logo_prompt)} characters)")

            # Enhance Logo Prompt button
            if st.button("✨ Enhance Logo Prompt", key="direct_enhance_logo_button",
                        disabled=st.session_state.direct_logo_enhancement_in_progress):
                if not logo_prompt:
                    st.warning("Please enter your company name and preferences to enhance.")
                elif not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar.")
                else:
                    st.session_state.direct_logo_enhancement_in_progress = True
                    with st.spinner("Enhancing logo prompt..."):
                        try:
                            result = enhance_logo_prompt(logo_prompt, st.session_state.api_key)
                            if result and result.strip() and result != logo_prompt:
                                st.session_state.direct_enhanced_logo_prompt = result.strip()
                                st.session_state.direct_logo_enhancement_in_progress = False
                                st.success("✨ Logo prompt enhanced successfully!")
                                st.rerun()
                            else:
                                st.session_state.direct_logo_enhancement_in_progress = False
                                st.info("Prompt is already well-optimized!")
                        except Exception as e:
                            st.session_state.direct_logo_enhancement_in_progress = False
                            st.error(f"Error enhancing logo prompt: {str(e)}")

        with col2:
            # Logo-specific options (matching regular tab exactly)
            st.subheader("Logo Options")

            # Logo style
            style_options = get_logo_style_options()
            logo_style = st.selectbox(
                "Logo Style",
                options=[opt["value"] for opt in style_options],
                format_func=lambda x: next(opt["label"] for opt in style_options if opt["value"] == x),
                help="Choose the overall style and feel of your logo",
                key="direct_logo_style"
            )

            # Show style description
            style_desc = next(opt["description"] for opt in style_options if opt["value"] == logo_style)
            st.caption(f"📝 {style_desc}")

            # Logo type
            type_options = get_logo_type_options()
            logo_type = st.selectbox(
                "Logo Type",
                options=[opt["value"] for opt in type_options],
                format_func=lambda x: next(opt["label"] for opt in type_options if opt["value"] == x),
                help="Choose the type of logo design",
                key="direct_logo_type"
            )

            # Show type description
            type_desc = next(opt["description"] for opt in type_options if opt["value"] == logo_type)
            st.caption(f"📝 {type_desc}")

            # Color scheme
            color_options = get_color_scheme_options()
            color_scheme = st.selectbox(
                "Color Scheme",
                options=[opt["value"] for opt in color_options],
                format_func=lambda x: next(opt["label"] for opt in color_options if opt["value"] == x),
                help="Choose the color palette for your logo",
                key="direct_color_scheme"
            )

            # Show color description
            color_desc = next(opt["description"] for opt in color_options if opt["value"] == color_scheme)
            st.caption(f"📝 {color_desc}")

            # Advanced options
            with st.expander("⚙️ Advanced Options"):
                num_logos = st.slider("Number of logo variations", 1, 4, 2, key="direct_num_logos")
                aspect_ratio = st.selectbox("Logo aspect ratio", ["1:1", "16:9", "4:3"], index=0, key="direct_aspect_ratio")
                ensure_variety = st.checkbox("Ensure unique designs", value=True,
                                           help="Randomize parameters to create unique logos each time",
                                           key="direct_ensure_variety")

        # Generate Logo button
        if st.button("🎨 Generate Logo", type="primary", key="direct_generate_logo_btn", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please enter your API key in the sidebar.")
                return

            if not logo_prompt:
                st.error("Please enter your company or brand name.")
                return

            # Use enhanced prompt if available, otherwise use original
            enhanced_prompt = st.session_state.direct_enhanced_logo_prompt.strip()
            if enhanced_prompt and len(enhanced_prompt) > 0:
                final_prompt = enhanced_prompt
                is_enhanced = True
            else:
                final_prompt = logo_prompt
                is_enhanced = False

            # Validate prompt before generation
            is_valid, validation_message = validate_logo_prompt(final_prompt, is_enhanced=is_enhanced)
            if not is_valid:
                st.error(f"Validation Error: {validation_message}")
                return

            with st.spinner("🎨 Creating your professional logo..."):
                try:
                    result = generate_logo(
                        prompt=final_prompt,
                        api_key=st.session_state.api_key,
                        logo_style=logo_style,
                        logo_type=logo_type,
                        color_scheme=color_scheme,
                        num_results=num_logos,
                        aspect_ratio=aspect_ratio,
                        sync=True,
                        ensure_variety=ensure_variety,
                        enhance_image=True,
                        content_moderation=True
                    )

                    if result and isinstance(result, dict):
                        # Try different response formats based on working Generate Image logic
                        logo_url = None

                        # Format 1: Direct URLs array (most common for Bria API)
                        if "urls" in result and result["urls"]:
                            logo_url = result["urls"][0]
                        # Format 2: Single result URL
                        elif "result_url" in result:
                            logo_url = result["result_url"]
                        # Format 3: Multiple result URLs
                        elif "result_urls" in result and result["result_urls"]:
                            logo_url = result["result_urls"][0]
                        # Format 4: Nested result structure
                        elif "result" in result:
                            result_data = result["result"]
                            if isinstance(result_data, list) and len(result_data) > 0:
                                first_item = result_data[0]
                                if isinstance(first_item, dict) and "urls" in first_item:
                                    logo_url = first_item["urls"][0]
                                elif isinstance(first_item, str):
                                    logo_url = first_item

                        if logo_url:
                            st.session_state.edited_image = logo_url
                            st.success("✨ Logo generated successfully!")

                            # Show navigation back to Brand Kit
                            st.success("💡 **Next Step:** Create a brand kit from this logo!")

                            col_nav1, col_nav2 = st.columns(2)
                            with col_nav1:
                                if st.button("🎯 Create Brand Kit from This Logo", key="nav_back_to_brand_kit", use_container_width=True):
                                    st.session_state.navigate_to_brand_kit_tab = True
                                    st.session_state.navigation_source = "logo_generation"
                                    st.rerun()

                            with col_nav2:
                                if st.button("← Back to Brand Kit", key="back_to_brand_kit_after_gen", use_container_width=True):
                                    st.session_state.navigate_to_brand_kit_tab = True
                                    st.session_state.navigation_source = "logo_generation"
                                    st.rerun()
                        else:
                            st.error("No valid logo URL found in the response.")
                    else:
                        st.error("Failed to generate logo. Please try again.")

                except Exception as e:
                    st.error(f"Error generating logo: {str(e)}")
                    if "api" in str(e).lower() or "token" in str(e).lower():
                        st.info("💡 Please check your API key and try again.")
                    elif "prompt" in str(e).lower():
                        st.info("💡 Try simplifying your prompt or using the enhancement feature.")
                    else:
                        st.info("💡 Please try again or contact support if the issue persists.")

        # Show generated logo if available
        if st.session_state.get('edited_image'):
            st.markdown("---")
            st.subheader("✨ Generated Logo")
            col_logo1, col_logo2 = st.columns([1, 2])
            with col_logo1:
                st.image(st.session_state.edited_image, caption="Your Logo", width=200)
            with col_logo2:
                st.success("✨ Logo generated successfully!")
                st.markdown("**Next Steps:**")
                st.markdown("• Create a brand kit from this logo")
                st.markdown("• Use in your marketing materials")
                st.markdown("• Download for offline use")

                # Navigation help
                with st.expander("🧭 Navigation Help", expanded=False):
                    st.markdown("**How to Navigate:**")
                    st.markdown("• Use '🎯 Create Brand Kit from This Logo' to go directly to brand kit creation")
                    st.markdown("• Use '← Back to Brand Kit' to return to the Brand Kit interface")
                    st.markdown("• Use '📋 Show All Tabs' to return to the main tab interface")
                    st.markdown("• All navigation happens in the same browser window")

        # Stop here - don't show the regular tabs
        return

    # Check if navigation to Brand Kit was triggered
    if st.session_state.get('navigate_to_brand_kit_tab'):
        st.session_state.navigate_to_brand_kit_tab = False
        st.success("🎯 **Navigated to Brand Kit!** Create your brand kit below.")

        # Show navigation breadcrumb
        if st.session_state.get('navigation_source') == "logo_generation":
            st.caption("📍 **Navigation Path:** Logo Generation → Brand Kit | Use '← Back to Logo Generation' to return")

        # Add navigation options for Brand Kit
        col_nav, col_title = st.columns([1, 4])
        with col_nav:
            # Show back navigation if we came from Logo Generation
            if st.session_state.get('navigation_source') == "logo_generation":
                if st.button("← Back to Logo Generation", key="back_to_logo_gen", help="Return to Logo Generation interface"):
                    st.session_state.navigate_to_logo_tab = True
                    st.session_state.navigation_source = "brand_kit"
                    st.rerun()
            else:
                # Show access to regular tabs
                if st.button("📋 Show All Tabs", key="show_all_tabs", help="Return to main tab interface"):
                    # Clear navigation flags to show regular tabs
                    st.session_state.navigate_to_logo_tab = False
                    st.session_state.navigate_to_brand_kit_tab = False
                    st.session_state.navigation_source = None
                    st.rerun()

        with col_title:
            st.header("🎯 Brand Kit Generator & Manager")

        st.markdown("Create and manage your brand identity with AI-powered color extraction and brand guidelines.")

        # Initialize brand kit session state
        if 'brand_kits' not in st.session_state:
            st.session_state.brand_kits = {}
        if 'active_brand_kit' not in st.session_state:
            st.session_state.active_brand_kit = None

        # Check if there's a generated logo
        if st.session_state.get('edited_image'):
            st.success("✅ Logo detected! Ready to create your brand kit.")

            # Brand Kit Creation Form
            col1, col2 = st.columns([2, 1])

            with col1:
                brand_name = st.text_input("Brand Name *", placeholder="Enter your brand name")
                brand_tagline = st.text_input("Tagline (optional)", placeholder="Your brand tagline")

                if brand_name and st.button("🎯 Create Brand Kit", type="primary", key="direct_brand_kit_create"):
                    with st.spinner("Creating brand kit and extracting colors..."):
                        try:
                            brand_kit = create_brand_kit(st.session_state.edited_image, brand_name, brand_tagline)
                            if brand_kit and save_brand_kit(brand_kit):
                                st.success(f"✨ Brand kit '{brand_name}' created successfully!")
                                st.balloons()
                            else:
                                st.error("Failed to create brand kit")
                        except Exception as e:
                            st.error(f"Error creating brand kit: {str(e)}")

            with col2:
                st.image(st.session_state.edited_image, caption="Your Logo", width=200)
        else:
            st.info("No logo detected. Please generate a logo first.")
            if st.button("🏢 Go to Logo Generation", key="nav_to_logo_from_brand_kit"):
                st.session_state.navigate_to_logo_tab = True
                st.rerun()

        # Stop here - don't show the regular tabs
        return

    # Regular tab interface with diverse, feature-specific emojis
    tab_names = [
        "🎨 Generate Image",      # Keep original - primary creative tool
        "🏢 Logo Generation",     # Company/business identity
        "🎯 Brand Kit",          # Brand targeting and guidelines
        "🖼️ Lifestyle Shot",     # Keep original - already unique
        "🔧 Generative Fill",    # Tool for filling/editing
        "🗑️ Erase Elements",     # Removal/deletion tool
        "📝 Free AI Copywriter"  # Free marketing copy generation
    ]

    # Create tabs
    tabs = st.tabs(tab_names)
    
    # Generate Images Tab
    with tabs[0]:
        st.header("🎨 Generate Images")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Prompt input
            prompt = st.text_area("Enter your prompt", 
                                value="",
                                height=100,
                                key="prompt_input")
            
            # Store original prompt in session state when it changes
            if "original_prompt" not in st.session_state:
                st.session_state.original_prompt = prompt
            elif prompt != st.session_state.original_prompt:
                st.session_state.original_prompt = prompt
                st.session_state.enhanced_prompt = None  # Reset enhanced prompt when original changes
            
            # Enhanced prompt display
            if st.session_state.get('enhanced_prompt'):
                st.markdown("**Enhanced Prompt:**")
                st.markdown(f"*{st.session_state.enhanced_prompt}*")
            
            # Enhance Prompt button
            if st.button("✨ Enhance Prompt", key="enhance_button"):
                if not prompt:
                    st.warning("Please enter a prompt to enhance.")
                else:
                    with st.spinner("Enhancing prompt..."):
                        try:
                            result = enhance_prompt(st.session_state.api_key, prompt)
                            if result:
                                st.session_state.enhanced_prompt = result
                                st.success("Prompt enhanced!")
                                st.rerun()  # Rerun to update the display
                        except Exception as e:
                            st.error(f"Error enhancing prompt: {str(e)}")
                            

        
        with col2:
            num_images = st.slider("Number of images", 1, 4, 1)
            aspect_ratio = st.selectbox("Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
            enhance_img = st.checkbox("Enhance image quality", value=True)
            
            # Style options
            st.subheader("Style Options")
            style = st.selectbox("Image Style", [
                "Realistic", "Artistic", "Cartoon", "Sketch",
                "Watercolor", "Oil Painting", "Digital Art"
            ])
        
        # Generate button
        if st.button("🎨 Generate Images", type="primary"):
            if not st.session_state.api_key:
                st.error("Please enter your API key in the sidebar.")
                return
                
            with st.spinner("🎨 Generating your masterpiece..."):
                try:
                    # Build final prompt with style
                    base_prompt = st.session_state.enhanced_prompt or prompt

                    # Add style to prompt if not realistic
                    if style and style != "Realistic":
                        styled_prompt = f"{base_prompt}, in {style.lower()} style"
                    else:
                        styled_prompt = base_prompt

                    # Apply brand styling if active brand kit exists
                    final_prompt = styled_prompt
                    if (st.session_state.get('active_brand_kit') and
                        st.session_state.get('apply_brand_automatically', True)):

                        original_prompt = final_prompt
                        final_prompt = apply_brand_to_prompt(final_prompt, st.session_state.active_brand_kit)

                        # Show brand application details
                        brand_kit = st.session_state.active_brand_kit
                        st.success(f"🎨 **Applied {brand_kit['brand_name']} Brand Styling**")

                        # Show applied colors
                        primary_color = brand_kit.get('primary_color', '')
                        secondary_color = brand_kit.get('secondary_color', '')
                        if primary_color or secondary_color:
                            color_info = []
                            if primary_color:
                                color_info.append(f"Primary: {primary_color}")
                            if secondary_color:
                                color_info.append(f"Secondary: {secondary_color}")
                            st.info(f"**Brand Colors Applied:** {' | '.join(color_info)}")

                        # Show enhanced prompt
                        with st.expander("🔍 View Enhanced Prompt", expanded=False):
                            st.markdown("**Original Prompt:**")
                            st.code(original_prompt)
                            st.markdown("**Brand-Enhanced Prompt:**")
                            st.code(final_prompt)

                    # Convert aspect ratio to proper format
                    result = generate_hd_image(
                        prompt=final_prompt,
                        api_key=st.session_state.api_key,
                        num_results=num_images,
                        aspect_ratio=aspect_ratio,  # Already in correct format (e.g. "1:1")
                        sync=True,  # Wait for results
                        enhance_image=enhance_img,
                        medium="art" if style != "Realistic" else "photography",
                        prompt_enhancement=False,  # We're already using our own prompt enhancement
                        content_moderation=True  # Enable content moderation by default
                    )
                    
                    if result:

                        if isinstance(result, dict):
                            image_url = None

                            # Try different response formats
                            if "urls" in result and result["urls"]:
                                image_url = result["urls"][0]
                            elif "result_url" in result:
                                image_url = result["result_url"]
                            elif "result_urls" in result and result["result_urls"]:
                                image_url = result["result_urls"][0]
                            elif "result" in result:
                                result_data = result["result"]
                                if isinstance(result_data, list) and len(result_data) > 0:
                                    first_item = result_data[0]
                                    if isinstance(first_item, dict) and "urls" in first_item:
                                        image_url = first_item["urls"][0]
                                    elif isinstance(first_item, str):
                                        image_url = first_item
                                elif isinstance(result_data, str):
                                    image_url = result_data

                            if image_url:
                                st.session_state.edited_image = image_url
                                st.success("🎨 Image generated successfully!")
                            else:
                                st.error("No valid image URL found in the API response. Please try again.")
                        else:
                            st.error("Invalid API response format.")
                    else:
                        st.error("No result received from the API.")
                            
                except Exception as e:
                    st.error(f"Error generating images: {str(e)}")

                    # Provide helpful error guidance
                    error_str = str(e).lower()
                    if "api" in error_str or "token" in error_str or "unauthorized" in error_str:
                        st.info("💡 **API Key Issue:** Please check your Bria AI API key in the sidebar.")
                    elif "prompt" in error_str or "invalid" in error_str:
                        st.info("💡 **Prompt Issue:** Try simplifying your prompt or using the enhancement feature.")
                    elif "timeout" in error_str or "connection" in error_str:
                        st.info("💡 **Connection Issue:** Please check your internet connection and try again.")
                    else:
                        st.info("💡 **General Error:** Please try again or contact support if the issue persists.")



    # Logo Generation Tab
    with tabs[1]:
        st.header("🏢 Logo Generation")
        st.markdown("Create professional, unique logos for your brand using AI technology.")

        # Display tips
        with st.expander("💡 Logo Generation Tips", expanded=False):
            tips = get_logo_generation_tips()
            for tip in tips:
                st.markdown(f"- {tip}")

        col1, col2 = st.columns([2, 1])
        with col1:
            # Company/Brand name and preferences input
            logo_prompt = st.text_area(
                "Enter your company name and preferences:",
                value="",
                height=100,
                key="logo_prompt_input",
                help="Examples:\n• 'TechCorp software company'\n• 'GreenLeaf organic foods, modern and clean'\n• 'Stellar Fitness gym, bold and energetic, blue colors'\n• 'Artisan Coffee roasters, vintage feel, warm colors'"
            )

            # Initialize session state for logo enhancement
            if "enhanced_logo_prompt" not in st.session_state:
                st.session_state.enhanced_logo_prompt = ""
            if "logo_enhancement_in_progress" not in st.session_state:
                st.session_state.logo_enhancement_in_progress = False
            if "logo_prompt_for_enhancement" not in st.session_state:
                st.session_state.logo_prompt_for_enhancement = ""

            # Clear enhanced prompt if user significantly changed the original prompt
            if logo_prompt != st.session_state.logo_prompt_for_enhancement:
                if abs(len(logo_prompt) - len(st.session_state.logo_prompt_for_enhancement)) > 20:
                    st.session_state.enhanced_logo_prompt = ""
                st.session_state.logo_prompt_for_enhancement = logo_prompt

            # Show enhanced prompt if available
            if st.session_state.enhanced_logo_prompt:
                st.markdown("**Enhanced Logo Prompt:**")
                st.markdown(f"*{st.session_state.enhanced_logo_prompt}*")
                st.caption(f"✅ Enhanced prompt ready ({len(st.session_state.enhanced_logo_prompt)} characters)")

            # Enhance Logo Prompt button
            if st.button("✨ Enhance Logo Prompt", key="enhance_logo_button",
                        disabled=st.session_state.logo_enhancement_in_progress):
                if not logo_prompt:
                    st.warning("Please enter your company name and preferences to enhance.")
                elif not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar.")
                else:
                    st.session_state.logo_enhancement_in_progress = True
                    with st.spinner("Enhancing logo prompt..."):
                        try:
                            result = enhance_logo_prompt(logo_prompt, st.session_state.api_key)
                            if result and result.strip() and result != logo_prompt:
                                # Store the enhanced prompt
                                st.session_state.enhanced_logo_prompt = result.strip()
                                st.session_state.logo_enhancement_in_progress = False
                                st.success("✨ Logo prompt enhanced successfully!")
                                st.rerun()
                            else:
                                st.session_state.logo_enhancement_in_progress = False
                                st.info("Prompt is already well-optimized!")
                        except Exception as e:
                            st.session_state.logo_enhancement_in_progress = False
                            st.error(f"Error enhancing logo prompt: {str(e)}")

            # Show enhancement status
            if st.session_state.logo_enhancement_in_progress:
                st.info("⏳ Enhancement in progress...")

        with col2:
            # Logo-specific options
            st.subheader("Logo Options")

            # Logo style
            style_options = get_logo_style_options()
            logo_style = st.selectbox(
                "Logo Style",
                options=[opt["value"] for opt in style_options],
                format_func=lambda x: next(opt["label"] for opt in style_options if opt["value"] == x),
                help="Choose the overall style and feel of your logo"
            )

            # Show style description
            style_desc = next(opt["description"] for opt in style_options if opt["value"] == logo_style)
            st.caption(f"📝 {style_desc}")

            # Logo type
            type_options = get_logo_type_options()
            logo_type = st.selectbox(
                "Logo Type",
                options=[opt["value"] for opt in type_options],
                format_func=lambda x: next(opt["label"] for opt in type_options if opt["value"] == x),
                help="Choose the type of logo design"
            )

            # Show type description
            type_desc = next(opt["description"] for opt in type_options if opt["value"] == logo_type)
            st.caption(f"📝 {type_desc}")

            # Color scheme
            color_options = get_color_scheme_options()
            color_scheme = st.selectbox(
                "Color Scheme",
                options=[opt["value"] for opt in color_options],
                format_func=lambda x: next(opt["label"] for opt in color_options if opt["value"] == x),
                help="Choose the color palette for your logo"
            )

            # Show color description
            color_desc = next(opt["description"] for opt in color_options if opt["value"] == color_scheme)
            st.caption(f"📝 {color_desc}")

            # Advanced options
            with st.expander("⚙️ Advanced Options"):
                num_logos = st.slider("Number of logo variations", 1, 4, 2)
                aspect_ratio = st.selectbox("Logo aspect ratio", ["1:1", "16:9", "4:3"], index=0)
                ensure_variety = st.checkbox("Ensure unique designs", value=True,
                                           help="Randomize parameters to create unique logos each time")

        # Generate Logo button
        if st.button("🎨 Generate Logo", type="primary", key="generate_logo_btn"):
            if not st.session_state.api_key:
                st.error("Please enter your API key in the sidebar.")
                return

            if not logo_prompt:
                st.error("Please enter your company or brand name.")
                return

            # Use enhanced prompt if available, otherwise use original
            enhanced_prompt = st.session_state.enhanced_logo_prompt.strip()
            if enhanced_prompt and len(enhanced_prompt) > 0:
                final_prompt = enhanced_prompt
                is_enhanced = True
            else:
                final_prompt = logo_prompt
                is_enhanced = False

            # Validate prompt before generation
            is_valid, validation_message = validate_logo_prompt(final_prompt, is_enhanced=is_enhanced)
            if not is_valid:
                st.error(f"Validation Error: {validation_message}")
                return

            with st.spinner("🎨 Creating your professional logo..."):
                try:
                    result = generate_logo(
                        prompt=final_prompt,
                        api_key=st.session_state.api_key,
                        logo_style=logo_style,
                        logo_type=logo_type,
                        color_scheme=color_scheme,
                        num_results=num_logos,
                        aspect_ratio=aspect_ratio,
                        sync=True,
                        ensure_variety=ensure_variety,
                        enhance_image=True,
                        content_moderation=True
                    )

                    if result and isinstance(result, dict):
                        # Try different response formats based on working Generate Image logic
                        logo_url = None

                        # Format 1: Direct URLs array (most common for Bria API)
                        if "urls" in result and result["urls"]:
                            logo_url = result["urls"][0]
                        # Format 2: Single result URL
                        elif "result_url" in result:
                            logo_url = result["result_url"]
                        # Format 3: Multiple result URLs
                        elif "result_urls" in result and result["result_urls"]:
                            logo_url = result["result_urls"][0]
                        # Format 4: Nested result structure
                        elif "result" in result:
                            result_data = result["result"]
                            if isinstance(result_data, list) and len(result_data) > 0:
                                first_item = result_data[0]
                                if isinstance(first_item, dict) and "urls" in first_item:
                                    logo_url = first_item["urls"][0]
                                elif isinstance(first_item, str):
                                    logo_url = first_item

                        if logo_url:
                            st.session_state.edited_image = logo_url
                            st.success("✨ Logo generated successfully!")

                            # Brand Kit navigation helper
                            st.success("💡 **Next Step:** Create a brand kit from this logo!")
                            if st.button("🎨 Go to Brand Kit Tab", key="nav_to_brand_kit", use_container_width=True):
                                st.session_state.navigate_to_brand_kit_tab = True
                                st.rerun()
                        else:
                            st.error("No valid logo URL found in the response.")
                    else:
                        st.error("Failed to generate logo. Please try again.")

                except Exception as e:
                    st.error(f"Error generating logo: {str(e)}")
                    if "api" in str(e).lower() or "token" in str(e).lower():
                        st.info("💡 Please check your API key and try again.")
                    elif "prompt" in str(e).lower():
                        st.info("💡 Try simplifying your prompt or using the enhancement feature.")
                    else:
                        st.info("💡 Please try again or contact support if the issue persists.")

    # Brand Kit Tab
    with tabs[2]:
        st.header("🎯 Brand Kit Generator & Manager")
        st.markdown("Create and manage your brand identity with AI-powered color extraction and brand guidelines.")

        # Initialize brand kit session state
        if 'brand_kits' not in st.session_state:
            st.session_state.brand_kits = {}
        if 'active_brand_kit' not in st.session_state:
            st.session_state.active_brand_kit = None



        # Main layout with proper proportions
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Create New Brand Kit")

            # Compact form layout
            with st.container():
                # Brand Information Section
                brand_name = st.text_input(
                    "Brand Name *",
                    placeholder="e.g., TechCorp, GreenLeaf Organics",
                    key="brand_name_input"
                )
                brand_tagline = st.text_input(
                    "Tagline (optional)",
                    placeholder="e.g., Innovation at its finest",
                    key="brand_tagline_input"
                )

                # Logo Source Selection
                st.markdown("**Logo Source**")
                logo_source = st.radio(
                    "Choose your logo source:",
                    ["Generate New Logo", "Use Existing Logo URL"],
                    key="logo_source_radio",
                    horizontal=True
                )

                # Logo Generation Path
                if logo_source == "Generate New Logo":
                    # Check if there's a generated logo in session
                    if st.session_state.get('edited_image'):
                        # Logo Available - Show Preview and Creation Option
                        st.success("✅ Logo ready for brand kit creation!")

                        # Compact logo preview
                        logo_col1, logo_col2 = st.columns([1, 2])
                        with logo_col1:
                            st.image(st.session_state.edited_image, caption="Generated Logo", width=120)
                        with logo_col2:
                            st.markdown("**Your logo is ready!**")
                            st.caption("Fill in the brand name above and create your brand kit.")

                        logo_url = st.session_state.edited_image

                        # Create brand kit button
                        if brand_name.strip():
                            if st.button("🎯 Create Brand Kit", type="primary", key="create_from_generated", use_container_width=True):
                                with st.spinner("Creating brand kit and extracting colors..."):
                                    try:
                                        brand_kit = create_brand_kit(logo_url, brand_name, brand_tagline)
                                        if brand_kit:
                                            if save_brand_kit(brand_kit):
                                                st.success(f"✨ Brand kit '{brand_name}' created successfully!")
                                                st.balloons()
                                                # Clear the form
                                                if 'edited_image' in st.session_state:
                                                    del st.session_state['edited_image']
                                                st.rerun()
                                            else:
                                                st.error("Failed to save brand kit")
                                        else:
                                            st.error("Failed to create brand kit")
                                    except Exception as e:
                                        st.error(f"Error creating brand kit: {str(e)}")
                        else:
                            st.button("🎯 Create Brand Kit", disabled=True, help="Please enter a brand name above")

                    else:
                        # No Logo - Show Navigation with Working Button
                        st.info("🎯 Generate a logo first to create your brand kit")

                        # Working navigation button
                        st.info("🎯 **Next Step:** Generate a logo to create your brand kit")

                        # Enhanced navigation with session management - prevent new tabs
                        nav_button_clicked = st.button("🏢 Go to Logo Generation", type="primary", key="nav_to_logo", use_container_width=True)

                        if nav_button_clicked:
                            # Immediate feedback to prevent multiple clicks
                            st.info("🔄 **Navigating...** Please wait")

                            # Set navigation flag with session verification
                            st.session_state.navigate_to_logo_tab = True
                            st.session_state.navigation_source = "brand_kit"
                            st.session_state.previous_interface = "brand_kit"

                            # Force page refresh in current window (not new tab)
                            st.rerun()

                        # Alternative: Show workflow instructions
                        if st.button("📋 Show Complete Workflow", key="show_workflow_btn", use_container_width=True):
                            st.session_state.show_workflow_guide = True
                            st.rerun()

                        # Show workflow instructions if requested
                        if st.session_state.get('show_workflow_guide'):
                            with st.expander("� Complete Workflow Guide", expanded=True):
                                st.markdown("**Step-by-Step Process:**")
                                st.markdown("1. **Navigate:** Look at the tab bar above and click '🏢 Logo Generation' (2nd tab)")
                                st.markdown("   ⚠️ **Important:** Don't click 'Generate Image' - make sure it says 'Logo Generation'")
                                st.markdown("2. **Create:** Fill in your company name and preferences")
                                st.markdown("3. **Generate:** Click 'Generate Logo' to create your logo")
                                st.markdown("4. **Return:** Come back to this '🎯 Brand Kit' tab (3rd tab)")
                                st.markdown("5. **Build:** Your logo will be automatically detected")
                                st.markdown("6. **Complete:** Create your brand kit with extracted colors")

                                if st.button("✅ Got it!", key="dismiss_workflow_btn"):
                                    st.session_state.show_workflow_guide = False
                                    st.rerun()



                # URL Input Path
                else:  # Use Existing Logo URL
                    logo_url = st.text_input(
                        "Logo URL *",
                        placeholder="https://example.com/logo.png",
                        key="logo_url_input"
                    )

                    # URL validation and preview
                    if logo_url:
                        if logo_url.startswith(('http://', 'https://')):
                            try:
                                # Compact preview
                                url_col1, url_col2 = st.columns([1, 2])
                                with url_col1:
                                    st.image(logo_url, caption="Preview", width=120)
                                with url_col2:
                                    st.success("✅ Logo URL valid")
                                    st.caption("Preview looks good? Create your brand kit below.")
                            except Exception as e:
                                st.warning("⚠️ Could not load preview. Please verify the URL.")
                        else:
                            st.error("❌ URL must start with 'http://' or 'https://'")

                    # Validation status
                    brand_name_valid = brand_name.strip() != ""
                    logo_url_valid = logo_url.strip() != "" and logo_url.startswith(('http://', 'https://'))

                    # Submit button
                    if brand_name_valid and logo_url_valid:
                        if st.button("🎯 Create Brand Kit", type="primary", key="create_from_url", use_container_width=True):
                            with st.spinner("Creating brand kit and extracting colors..."):
                                try:
                                    brand_kit = create_brand_kit(logo_url, brand_name, brand_tagline)
                                    if brand_kit:
                                        if save_brand_kit(brand_kit):
                                            st.success(f"✨ Brand kit '{brand_name}' created successfully!")
                                            st.balloons()
                                            # Clear form
                                            st.session_state.logo_url_input = ""
                                            st.rerun()
                                        else:
                                            st.error("Failed to save brand kit")
                                    else:
                                        st.error("Failed to create brand kit")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    else:
                        st.button("🎯 Create Brand Kit", disabled=True, help="Fill in brand name and valid logo URL", use_container_width=True)
                        if not brand_name_valid:
                            st.caption("⚠️ Brand name required")
                        if not logo_url_valid:
                            st.caption("⚠️ Valid logo URL required")

        with col2:
            st.subheader("Brand Kit Manager")

            # Available brand kits
            available_kits = get_available_brand_kits()

            if available_kits:
                selected_kit = st.selectbox("Select Brand Kit", available_kits, key="brand_kit_selector")

                if selected_kit:
                    brand_kit = load_brand_kit(selected_kit)
                    if brand_kit:
                        # Compact brand info display
                        with st.container():
                            st.markdown(f"**{brand_kit.get('brand_name', 'Unknown')}**")
                            if brand_kit.get('tagline'):
                                st.caption(f"_{brand_kit['tagline']}_")

                            # Compact color palette
                            colors = brand_kit.get('color_palette', [])
                            if colors and len(colors) >= 3:
                                color_col1, color_col2, color_col3 = st.columns(3)
                                with color_col1:
                                    st.color_picker("Primary", colors[0], disabled=True, key=f"mgr_color_1")
                                with color_col2:
                                    st.color_picker("Secondary", colors[1], disabled=True, key=f"mgr_color_2")
                                with color_col3:
                                    st.color_picker("Accent", colors[2], disabled=True, key=f"mgr_color_3")

                            # Action buttons
                            if st.button("✅ Set as Active", key="set_active_btn", use_container_width=True):
                                st.session_state.active_brand_kit = brand_kit
                                st.success(f"'{selected_kit}' is now active!")
                                st.rerun()

                            if st.button("🗑️ Delete", key="delete_btn", type="secondary", use_container_width=True):
                                del st.session_state.brand_kits[selected_kit]
                                if st.session_state.active_brand_kit == brand_kit:
                                    st.session_state.active_brand_kit = None
                                st.success(f"'{selected_kit}' deleted!")
                                st.rerun()
            else:
                st.info("💡 No brand kits yet. Create your first one!")

        # Active Brand Kit Display (Compact)
        if st.session_state.active_brand_kit:
            st.markdown("---")
            st.subheader("🎯 Active Brand Kit")

            active_kit = st.session_state.active_brand_kit

            # Compact active brand display
            active_col1, active_col2 = st.columns([2, 1])

            with active_col1:
                # Brand info and logo
                brand_info_col1, brand_info_col2 = st.columns([1, 2])
                with brand_info_col1:
                    if active_kit.get('logo_url'):
                        st.image(active_kit['logo_url'], width=100)
                with brand_info_col2:
                    st.markdown(f"**{active_kit.get('brand_name', 'Unknown')}**")
                    if active_kit.get('tagline'):
                        st.caption(f"_{active_kit['tagline']}_")

                    # Compact color display
                    if active_kit.get('color_palette'):
                        colors = active_kit['color_palette'][:3]
                        color_display = " ".join([f'<span style="background-color:{color}; padding:2px 8px; margin:2px; border-radius:3px; color:white; font-size:10px;">{color}</span>' for color in colors])
                        st.markdown(f"**Colors:** {color_display}", unsafe_allow_html=True)

            with active_col2:
                # Brand application settings
                st.markdown("**Auto-Apply**")
                if 'apply_brand_automatically' not in st.session_state:
                    st.session_state.apply_brand_automatically = True

                apply_brand = st.checkbox(
                    "Apply to new generations",
                    value=st.session_state.apply_brand_automatically,
                    key="brand_auto_apply"
                )
                st.session_state.apply_brand_automatically = apply_brand

                if apply_brand:
                    st.success("✅ Brand styling active")
                else:
                    st.info("⏸️ Brand styling paused")

    # Lifestyle Shot Tab
    with tabs[3]:
        st.header("🖼️ Lifestyle Shot")
        
        uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"], key="product_upload")
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_container_width=True)
                
                # Product editing options
                edit_option = st.selectbox("Select Edit Option", [
                    "Create Packshot",
                    "Add Shadow",
                    "Lifestyle Shot"
                ])
                
                if edit_option == "Create Packshot":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        bg_color = st.color_picker("Background Color", "#FFFFFF")
                        sku = st.text_input("SKU (optional)", "")
                    with col_b:
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                    
                    if st.button("Create Packshot"):
                        with st.spinner("Creating professional packshot..."):
                            try:
                                # First remove background if needed
                                if force_rmbg:
                                    from services.background_service import remove_background
                                    bg_result = remove_background(
                                        st.session_state.api_key,
                                        uploaded_file.getvalue(),
                                        content_moderation=content_moderation
                                    )
                                    if bg_result and "result_url" in bg_result:
                                        # Download the background-removed image
                                        response = requests.get(bg_result["result_url"])
                                        if response.status_code == 200:
                                            image_data = response.content
                                        else:
                                            st.error("Failed to download background-removed image")
                                            return
                                    else:
                                        st.error("Background removal failed")
                                        return
                                else:
                                    image_data = uploaded_file.getvalue()
                                
                                # Now create packshot
                                result = create_packshot(
                                    st.session_state.api_key,
                                    image_data,
                                    background_color=bg_color,
                                    sku=sku if sku else None,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Packshot created successfully!")
                                    st.session_state.edited_image = result["result_url"]
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error creating packshot: {str(e)}")
                                if "422" in str(e):
                                    st.warning("Content moderation failed. Please ensure the image is appropriate.")
                
                elif edit_option == "Add Shadow":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop"])
                        bg_color = st.color_picker("Background Color (optional)", "#FFFFFF")
                        use_transparent_bg = st.checkbox("Use Transparent Background", True)
                        shadow_color = st.color_picker("Shadow Color", "#000000")
                        sku = st.text_input("SKU (optional)", "")
                        
                        # Shadow offset
                        st.subheader("Shadow Offset")
                        offset_x = st.slider("X Offset", -50, 50, 0)
                        offset_y = st.slider("Y Offset", -50, 50, 15)
                    
                    with col_b:
                        shadow_intensity = st.slider("Shadow Intensity", 0, 100, 60)
                        shadow_blur = st.slider("Shadow Blur", 0, 50, 15 if shadow_type.lower() == "regular" else 20)
                        
                        # Float shadow specific controls
                        if shadow_type == "Float":
                            st.subheader("Float Shadow Settings")
                            shadow_width = st.slider("Shadow Width", -100, 100, 0)
                            shadow_height = st.slider("Shadow Height", -100, 100, 70)
                        
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                    
                    if st.button("Add Shadow"):
                        with st.spinner("Adding shadow effect..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    shadow_type=shadow_type.lower(),
                                    background_color=None if use_transparent_bg else bg_color,
                                    shadow_color=shadow_color,
                                    shadow_offset=[offset_x, offset_y],
                                    shadow_intensity=shadow_intensity,
                                    shadow_blur=shadow_blur,
                                    shadow_width=shadow_width if shadow_type == "Float" else None,
                                    shadow_height=shadow_height if shadow_type == "Float" else 70,
                                    sku=sku if sku else None,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Shadow added successfully!")
                                    st.session_state.edited_image = result["result_url"]
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error adding shadow: {str(e)}")
                                if "422" in str(e):
                                    st.warning("Content moderation failed. Please ensure the image is appropriate.")
                
                elif edit_option == "Lifestyle Shot":
                    shot_type = st.radio("Shot Type", ["Text Prompt", "Reference Image"])
                    
                    # Common settings for both types
                    col1, col2 = st.columns(2)
                    with col1:
                        placement_type = st.selectbox("Placement Type", [
                            "Original", "Automatic", "Manual Placement",
                            "Manual Padding", "Custom Coordinates"
                        ])
                        num_results = st.slider("Number of Results", 1, 8, 4)
                        sync_mode = st.checkbox("Synchronous Mode", False,
                            help="Wait for results instead of getting URLs immediately")
                        original_quality = st.checkbox("Original Quality", False,
                            help="Maintain original image quality")
                        
                        if placement_type == "Manual Placement":
                            positions = st.multiselect("Select Positions", [
                                "Upper Left", "Upper Right", "Bottom Left", "Bottom Right",
                                "Right Center", "Left Center", "Upper Center",
                                "Bottom Center", "Center Vertical", "Center Horizontal"
                            ], ["Upper Left"])
                        
                        elif placement_type == "Manual Padding":
                            st.subheader("Padding Values (pixels)")
                            pad_left = st.number_input("Left Padding", 0, 1000, 0)
                            pad_right = st.number_input("Right Padding", 0, 1000, 0)
                            pad_top = st.number_input("Top Padding", 0, 1000, 0)
                            pad_bottom = st.number_input("Bottom Padding", 0, 1000, 0)
                        
                        elif placement_type in ["Automatic", "Manual Placement", "Custom Coordinates"]:
                            st.subheader("Shot Size")
                            shot_width = st.number_input("Width", 100, 2000, 1000)
                            shot_height = st.number_input("Height", 100, 2000, 1000)
                    
                    with col2:
                        if placement_type == "Custom Coordinates":
                            st.subheader("Product Position")
                            fg_width = st.number_input("Product Width", 50, 1000, 500)
                            fg_height = st.number_input("Product Height", 50, 1000, 500)
                            fg_x = st.number_input("X Position", -500, 1500, 0)
                            fg_y = st.number_input("Y Position", -500, 1500, 0)
                        
                        sku = st.text_input("SKU (optional)")
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                        
                        if shot_type == "Text Prompt":
                            fast_mode = st.checkbox("Fast Mode", True,
                                help="Balance between speed and quality")
                            optimize_desc = st.checkbox("Optimize Description", True,
                                help="Enhance scene description using AI")
                            if not fast_mode:
                                exclude_elements = st.text_area("Exclude Elements (optional)",
                                    help="Elements to exclude from the generated scene")
                        else:  # Reference Image
                            enhance_ref = st.checkbox("Enhance Reference Image", True,
                                help="Improve lighting, shadows, and texture")
                            ref_influence = st.slider("Reference Influence", 0.0, 1.0, 1.0,
                                help="Control similarity to reference image")
                    
                    if shot_type == "Text Prompt":
                        prompt = st.text_area("Describe the environment")
                        if st.button("Generate Lifestyle Shot") and prompt:
                            with st.spinner("Generating lifestyle shot..."):
                                try:
                                    # Convert placement selections to API format
                                    if placement_type == "Manual Placement":
                                        manual_placements = [p.lower().replace(" ", "_") for p in positions]
                                    else:
                                        manual_placements = ["upper_left"]
                                    
                                    result = lifestyle_shot_by_text(
                                        api_key=st.session_state.api_key,
                                        image_data=uploaded_file.getvalue(),
                                        scene_description=prompt,
                                        placement_type=placement_type.lower().replace(" ", "_"),
                                        num_results=num_results,
                                        sync=sync_mode,
                                        fast=fast_mode,
                                        optimize_description=optimize_desc,
                                        shot_size=[shot_width, shot_height] if placement_type != "Original" else [1000, 1000],
                                        original_quality=original_quality,
                                        exclude_elements=exclude_elements if not fast_mode else None,
                                        manual_placement_selection=manual_placements,
                                        padding_values=[pad_left, pad_right, pad_top, pad_bottom] if placement_type == "Manual Padding" else [0, 0, 0, 0],
                                        foreground_image_size=[fg_width, fg_height] if placement_type == "Custom Coordinates" else None,
                                        foreground_image_location=[fg_x, fg_y] if placement_type == "Custom Coordinates" else None,
                                        force_rmbg=force_rmbg,
                                        content_moderation=content_moderation,
                                        sku=sku if sku else None
                                    )
                                    
                                    if result:
                                        if sync_mode:
                                            if isinstance(result, dict):
                                                if "result_url" in result:
                                                    st.session_state.edited_image = result["result_url"]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result_urls" in result:
                                                    st.session_state.edited_image = result["result_urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result" in result and isinstance(result["result"], list):
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            st.session_state.edited_image = item["urls"][0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                        elif isinstance(item, list) and len(item) > 0:
                                                            st.session_state.edited_image = item[0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                elif "urls" in result:
                                                    st.session_state.edited_image = result["urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                        else:
                                            urls = []
                                            if isinstance(result, dict):
                                                if "urls" in result:
                                                    urls.extend(result["urls"][:num_results])  # Limit to requested number
                                                elif "result" in result and isinstance(result["result"], list):
                                                    # Process each result item
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            urls.extend(item["urls"])
                                                        elif isinstance(item, list):
                                                            urls.extend(item)
                                                        # Break if we have enough URLs
                                                        if len(urls) >= num_results:
                                                            break
                                                    
                                                    # Trim to requested number
                                                    urls = urls[:num_results]
                                            
                                            if urls:
                                                st.session_state.pending_urls = urls
                                                
                                                # Create a container for status messages
                                                status_container = st.empty()
                                                refresh_container = st.empty()
                                                
                                                # Show initial status
                                                status_container.info(f"🎨 Generation started! Waiting for {len(urls)} image{'s' if len(urls) > 1 else ''}...")
                                                
                                                # Try automatic checking first
                                                if auto_check_images(status_container):
                                                    st.rerun()
                                                
                                                # Add refresh button for manual checking
                                                if refresh_container.button("🔄 Check for Generated Images"):
                                                    with st.spinner("Checking for completed images..."):
                                                        if check_generated_images():
                                                            status_container.success("✨ Image ready!")
                                                            st.rerun()
                                                        else:
                                                            status_container.warning(f"⏳ Still generating your image{'s' if len(urls) > 1 else ''}... Please check again in a moment.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    if "422" in str(e):
                                        st.warning("Content moderation failed. Please ensure the content is appropriate.")
                    else:
                        ref_image = st.file_uploader("Upload Reference Image", type=["png", "jpg", "jpeg"], key="ref_upload")
                        if st.button("Generate Lifestyle Shot") and ref_image:
                            with st.spinner("Generating lifestyle shot..."):
                                try:
                                    # Convert placement selections to API format
                                    if placement_type == "Manual Placement":
                                        manual_placements = [p.lower().replace(" ", "_") for p in positions]
                                    else:
                                        manual_placements = ["upper_left"]
                                    
                                    result = lifestyle_shot_by_image(
                                        api_key=st.session_state.api_key,
                                        image_data=uploaded_file.getvalue(),
                                        reference_image=ref_image.getvalue(),
                                        placement_type=placement_type.lower().replace(" ", "_"),
                                        num_results=num_results,
                                        sync=sync_mode,
                                        shot_size=[shot_width, shot_height] if placement_type != "Original" else [1000, 1000],
                                        original_quality=original_quality,
                                        manual_placement_selection=manual_placements,
                                        padding_values=[pad_left, pad_right, pad_top, pad_bottom] if placement_type == "Manual Padding" else [0, 0, 0, 0],
                                        foreground_image_size=[fg_width, fg_height] if placement_type == "Custom Coordinates" else None,
                                        foreground_image_location=[fg_x, fg_y] if placement_type == "Custom Coordinates" else None,
                                        force_rmbg=force_rmbg,
                                        content_moderation=content_moderation,
                                        sku=sku if sku else None,
                                        enhance_ref_image=enhance_ref,
                                        ref_image_influence=ref_influence
                                    )
                                    
                                    if result:
                                        if sync_mode:
                                            if isinstance(result, dict):
                                                if "result_url" in result:
                                                    st.session_state.edited_image = result["result_url"]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result_urls" in result:
                                                    st.session_state.edited_image = result["result_urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result" in result and isinstance(result["result"], list):
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            st.session_state.edited_image = item["urls"][0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                        elif isinstance(item, list) and len(item) > 0:
                                                            st.session_state.edited_image = item[0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                elif "urls" in result:
                                                    st.session_state.edited_image = result["urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                        else:
                                            urls = []
                                            if isinstance(result, dict):
                                                if "urls" in result:
                                                    urls.extend(result["urls"][:num_results])  # Limit to requested number
                                                elif "result" in result and isinstance(result["result"], list):
                                                    # Process each result item
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            urls.extend(item["urls"])
                                                        elif isinstance(item, list):
                                                            urls.extend(item)
                                                        # Break if we have enough URLs
                                                        if len(urls) >= num_results:
                                                            break
                                                    
                                                    # Trim to requested number
                                                    urls = urls[:num_results]
                                            
                                            if urls:
                                                st.session_state.pending_urls = urls
                                                
                                                # Create a container for status messages
                                                status_container = st.empty()
                                                refresh_container = st.empty()
                                                
                                                # Show initial status
                                                status_container.info(f"🎨 Generation started! Waiting for {len(urls)} image{'s' if len(urls) > 1 else ''}...")
                                                
                                                # Try automatic checking first
                                                if auto_check_images(status_container):
                                                    st.rerun()
                                                
                                                # Add refresh button for manual checking
                                                if refresh_container.button("🔄 Check for Generated Images"):
                                                    with st.spinner("Checking for completed images..."):
                                                        if check_generated_images():
                                                            status_container.success("✨ Image ready!")
                                                            st.rerun()
                                                        else:
                                                            status_container.warning(f"⏳ Still generating your image{'s' if len(urls) > 1 else ''}... Please check again in a moment.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    if "422" in str(e):
                                        st.warning("Content moderation failed. Please ensure the content is appropriate.")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Edited Image", use_container_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "edited_product.png",
                            "image/png"
                        )
                elif st.session_state.pending_urls:
                    st.info("Images are being generated. Click the refresh button above to check if they're ready.")

    # Generative Fill Tab
    with tabs[4]:
        st.header("🔧 Generative Fill")
        st.markdown("Draw a mask on the image and describe what you want to generate in that area.")
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="fill_upload")
        if uploaded_file:
            # Create columns for original image and canvas
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original image
                st.image(uploaded_file, caption="Original Image", use_container_width=True)
                
                # Get image dimensions for canvas
                img = Image.open(uploaded_file)
                img_width, img_height = img.size
                
                # Calculate aspect ratio and set canvas height
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 800)  # Max width of 800px
                canvas_height = int(canvas_width * aspect_ratio)
                
                # Resize image to match canvas dimensions
                img = img.resize((canvas_width, canvas_height))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to numpy array with proper shape and type
                img_array = np.array(img).astype(np.uint8)
                
                # Add drawing canvas using Streamlit's drawing canvas component
                stroke_width = st.slider("Brush width", 1, 50, 20)
                stroke_color = st.color_picker("Brush color", "#fff")
                drawing_mode = "freedraw"
                
                # Create canvas with background image
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    drawing_mode=drawing_mode,
                    background_color="",  # Transparent background
                    background_image=img if img_array.shape[-1] == 3 else None,  # Only pass RGB images
                    height=canvas_height,
                    width=canvas_width,
                    key="canvas",
                )
                
                # Options for generation
                st.subheader("Generation Options")
                prompt = st.text_area("Describe what to generate in the masked area")
                negative_prompt = st.text_area("Describe what to avoid (optional)")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    num_results = st.slider("Number of variations", 1, 4, 1)
                    sync_mode = st.checkbox("Synchronous Mode", False,
                        help="Wait for results instead of getting URLs immediately",
                        key="gen_fill_sync_mode")
                
                with col_b:
                    seed = st.number_input("Seed (optional)", min_value=0, value=0,
                        help="Use same seed to reproduce results")
                    content_moderation = st.checkbox("Enable Content Moderation", False,
                        key="gen_fill_content_mod")
                
                if st.button("🎨 Generate", type="primary"):
                    if not prompt:
                        st.error("Please enter a prompt describing what to generate.")
                        return
                    
                    if canvas_result.image_data is None:
                        st.error("Please draw a mask on the image first.")
                        return
                    
                    # Convert canvas result to mask
                    mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                    mask_img = mask_img.convert('L')
                    
                    # Convert mask to bytes
                    mask_bytes = io.BytesIO()
                    mask_img.save(mask_bytes, format='PNG')
                    mask_bytes = mask_bytes.getvalue()
                    
                    # Convert uploaded image to bytes
                    image_bytes = uploaded_file.getvalue()
                    
                    with st.spinner("🎨 Generating..."):
                        try:
                            result = generative_fill(
                                st.session_state.api_key,
                                image_bytes,
                                mask_bytes,
                                prompt,
                                negative_prompt=negative_prompt if negative_prompt else None,
                                num_results=num_results,
                                sync=sync_mode,
                                seed=seed if seed != 0 else None,
                                content_moderation=content_moderation
                            )
                            
                            if result:
                                if sync_mode:
                                    if "urls" in result and result["urls"]:
                                        st.session_state.edited_image = result["urls"][0]
                                        if len(result["urls"]) > 1:
                                            st.session_state.generated_images = result["urls"]
                                        st.success("✨ Generation complete!")
                                    elif "result_url" in result:
                                        st.session_state.edited_image = result["result_url"]
                                        st.success("✨ Generation complete!")
                                else:
                                    if "urls" in result:
                                        st.session_state.pending_urls = result["urls"][:num_results]
                                        
                                        # Create containers for status
                                        status_container = st.empty()
                                        refresh_container = st.empty()
                                        
                                        # Show initial status
                                        status_container.info(f"🎨 Generation started! Waiting for {len(st.session_state.pending_urls)} image{'s' if len(st.session_state.pending_urls) > 1 else ''}...")
                                        
                                        # Try automatic checking
                                        if auto_check_images(status_container):
                                            st.rerun()
                                        
                                        # Add refresh button
                                        if refresh_container.button("🔄 Check for Generated Images"):
                                            if check_generated_images():
                                                status_container.success("✨ Images ready!")
                                                st.rerun()
                                            else:
                                                status_container.warning("⏳ Still generating... Please check again in a moment.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            st.write("Full error details:", str(e))
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Generated Result", use_container_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "generated_fill.png",
                            "image/png"
                        )
                elif st.session_state.pending_urls:
                    st.info("Generation in progress. Click the refresh button above to check status.")

    # Erase Elements Tab
    with tabs[5]:
        st.header("🗑️ Erase Elements")
        st.markdown("Upload an image and select the area you want to erase.")
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="erase_upload")
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original image
                st.image(uploaded_file, caption="Original Image", use_container_width=True)
                
                # Get image dimensions for canvas
                img = Image.open(uploaded_file)
                img_width, img_height = img.size
                
                # Calculate aspect ratio and set canvas height
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 800)  # Max width of 800px
                canvas_height = int(canvas_width * aspect_ratio)
                
                # Resize image to match canvas dimensions
                img = img.resize((canvas_width, canvas_height))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Add drawing canvas using Streamlit's drawing canvas component
                stroke_width = st.slider("Brush width", 1, 50, 20, key="erase_brush_width")
                stroke_color = st.color_picker("Brush color", "#fff", key="erase_brush_color")
                
                # Create canvas with background image
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_color="",  # Transparent background
                    background_image=img,  # Pass PIL Image directly
                    drawing_mode="freedraw",
                    height=canvas_height,
                    width=canvas_width,
                    key="erase_canvas",
                )
                
                # Options for erasing
                st.subheader("Erase Options")
                content_moderation = st.checkbox("Enable Content Moderation", False, key="erase_content_mod")
                
                if st.button("🎨 Erase Selected Area", key="erase_btn"):
                    if not canvas_result.image_data is None:
                        with st.spinner("Erasing selected area..."):
                            try:
                                # Convert canvas result to mask
                                mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                                mask_img = mask_img.convert('L')
                                
                                # Convert uploaded image to bytes
                                image_bytes = uploaded_file.getvalue()
                                
                                result = erase_foreground(
                                    st.session_state.api_key,
                                    image_data=image_bytes,
                                    content_moderation=content_moderation
                                )
                                
                                if result:
                                    if "result_url" in result:
                                        st.session_state.edited_image = result["result_url"]
                                        st.success("✨ Area erased successfully!")
                                    else:
                                        st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                if "422" in str(e):
                                    st.warning("Content moderation failed. Please ensure the image is appropriate.")
                    else:
                        st.warning("Please draw on the image to select the area to erase.")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Result", use_container_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "erased_image.png",
                            "image/png",
                            key="erase_download"
                        )

    # Free AI Copywriter Tab
    with tabs[6]:
        st.header("📝 Free AI Content Copywriter")
        st.markdown("Generate professional marketing copy for your products using free AI models - no API keys required!")

        # Show service status
        col_status1, col_status2 = st.columns([3, 1])
        with col_status1:
            st.info("🆓 **Completely Free** - No API keys required! Powered by Hugging Face open-source models.")
        with col_status2:
            # Test connection button
            if st.button("🔍 Test Service", key="test_free_copywriter_tab"):
                with st.spinner("Testing free copywriter service..."):
                    is_working, message = test_free_copywriter_connection()
                    if is_working:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")

        # Free Copywriter controls
        col1, col2 = st.columns([2, 1])

        with col1:
            # Image description input
            image_description = st.text_area(
                "Describe your product/image:",
                placeholder="e.g., Premium wireless headphones with noise cancellation, sleek black design, professional quality",
                height=100,
                key="free_copy_image_desc_tab"
            )

        with col2:
            # Copy type selection using free options
            copy_types = get_copy_type_options_free()
            copy_type = st.selectbox(
                "Content Type",
                options=[opt["value"] for opt in copy_types],
                format_func=lambda x: next(opt["label"] for opt in copy_types if opt["value"] == x),
                key="free_copy_type_select_tab"
            )

            # Show copy type description
            copy_desc = next(opt["description"] for opt in copy_types if opt["value"] == copy_type)
            st.caption(f"📝 {copy_desc}")

            # Tone and length options
            st.subheader("Options")
            tone = st.selectbox("Tone", ["professional", "casual", "creative", "luxury", "urgent"], key="free_tone_tab")
            length = st.selectbox("Length", ["short", "medium", "long"], index=1, key="free_length_tab")

            # Show model info
            st.caption("🤖 **Powered by:** Hugging Face open-source AI models")

        # Generate copy buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🆓 Generate Copy", type="primary", key="generate_free_single_copy_tab"):
                if not image_description:
                    st.warning("Please describe your product/image first.")
                else:
                    with st.spinner("🤖 Generating free marketing copy..."):
                        try:
                            copy_text = generate_marketing_copy_free(
                                image_description=image_description,
                                brand_kit=st.session_state.get('active_brand_kit'),
                                copy_type=copy_type,
                                tone=tone,
                                length=length
                            )

                            if copy_text:
                                st.session_state.generated_copy_tab = copy_text
                                st.success("🆓 Copy generated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to generate copy. Please try again.")
                        except Exception as e:
                            st.error(f"Error generating copy: {str(e)}")

        with col2:
            if st.button("🎯 Generate Variations", key="generate_free_copy_variations_tab"):
                if not image_description:
                    st.warning("Please describe your product/image first.")
                else:
                    with st.spinner("🤖 Generating free copy variations..."):
                        try:
                            variations = generate_multiple_copy_variations_free(
                                image_description=image_description,
                                brand_kit=st.session_state.get('active_brand_kit'),
                                copy_type=copy_type
                            )

                            if variations:
                                st.session_state.copy_variations_tab = variations
                                st.success(f"🆓 Generated {len(variations)} copy variations!")
                                st.rerun()
                            else:
                                st.error("Failed to generate variations. Please try again.")
                        except Exception as e:
                            st.error(f"Error generating variations: {str(e)}")

        # Display generated copy
        if st.session_state.get('generated_copy_tab'):
            st.markdown("---")
            st.markdown("**🆓 Generated Copy:**")
            st.markdown(f"*{st.session_state.generated_copy_tab}*")

            # Copy to clipboard button
            if st.button("📋 Copy Text", key="copy_free_generated_text_tab"):
                st.code(st.session_state.generated_copy_tab)
                st.success("Copy text displayed above!")

        # Display copy variations
        if st.session_state.get('copy_variations_tab'):
            st.markdown("---")
            st.markdown("**🎯 Copy Variations:**")

            for i, variation in enumerate(st.session_state.copy_variations_tab):
                with st.expander(f"{variation['label']} ({variation['word_count']} words)", expanded=i==0):
                    st.markdown(variation['text'])

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"📋 Copy", key=f"copy_free_variation_tab_{i}"):
                            st.code(variation['text'])
                            st.success("Copy text displayed above!")
                    with col2:
                        st.caption(f"Tone: {variation['tone'].title()} | Length: {variation['length'].title()}")

        # Show helpful tips
        if not st.session_state.get('generated_copy_tab') and not st.session_state.get('copy_variations_tab'):
            with st.expander("💡 Tips for Better Copy Generation", expanded=False):
                st.markdown("**For Best Results:**")
                st.markdown("• Provide detailed product descriptions")
                st.markdown("• Include key features and benefits")
                st.markdown("• Mention target audience if relevant")
                st.markdown("• Use active Brand Kits for consistent messaging")
                st.markdown("• Try different content types for various use cases")
                st.markdown("• Generate variations to compare different approaches")
                st.markdown("• Experiment with different tones and lengths")

    # Display generated images section (shared across all tabs)
    if st.session_state.edited_image:
        st.markdown("---")
        st.subheader("🎨 Generated Image")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(st.session_state.edited_image, caption="🎨 Generated Image", use_container_width=True)

        with col2:
            # Download button
            image_data = download_image(st.session_state.edited_image)
            if image_data:
                st.download_button(
                    "⬇️ Download Image",
                    image_data,
                    "generated_image.png",
                    "image/png",
                    key="main_download"
                )

            # Additional actions
            if st.button("🔄 Generate Another", key="generate_another"):
                st.session_state.edited_image = None
                st.rerun()

            if st.button("📋 Copy URL", key="copy_url"):
                st.code(st.session_state.edited_image)
                st.success("URL copied to display!")



if __name__ == "__main__":
    main()