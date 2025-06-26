import streamlit as st
import requests
from PIL import Image
import io

def download_image(url):
    """Download image from URL and return as bytes."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

def render_image_preview(result):
    """Render the image preview with download options."""
    
    if not result or "images" not in result:
        st.error("No images to display")
        return
    
    st.subheader("🖼️ Generated Images")
    
    # Create columns for multiple images
    cols = st.columns(len(result["images"]))
    
    for idx, (col, image_data) in enumerate(zip(cols, result["images"])):
        with col:
            if "url" in image_data:
                image_bytes = download_image(image_data["url"])
                if image_bytes:
                    st.image(image_bytes, caption=f"Generated Image {idx + 1}")
                    
                    # Convert to PIL Image for saving
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Save button
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format or 'PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    st.download_button(
                        label=f"💾 Download Image {idx + 1}",
                        data=img_byte_arr,
                        file_name=f"adsnap_generated_{idx + 1}.png",
                        mime="image/png"
                    )
            else:
                st.error(f"Invalid image data for image {idx + 1}")
    
    # Display API response details in expander
    with st.expander("🔍 Image Generation Details"):
        st.json({
            k: v for k, v in result.items() 
            if k != "images"  # Exclude image data to keep response clean
        }) 