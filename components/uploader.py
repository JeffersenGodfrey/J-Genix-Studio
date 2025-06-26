import streamlit as st
import magic
import io

def is_valid_image(file_content):
    """Validate if the uploaded file is an image."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)
    return file_type.startswith('image/')

def render_uploader():
    """Render the image upload component with validation."""
    
    uploaded_file = st.file_uploader(
        "Upload Product Image (Optional)",
        type=["png", "jpg", "jpeg"],
        help="Upload a product image to enhance or modify"
    )
    
    if uploaded_file is not None:
        # Read file content
        file_content = uploaded_file.getvalue()
        
        # Validate image
        if not is_valid_image(file_content):
            st.error("Please upload a valid image file")
            return None
        
        # Preview image
        st.image(file_content, caption="Uploaded Image", use_container_width=True)
        
        return uploaded_file
        
    return None 