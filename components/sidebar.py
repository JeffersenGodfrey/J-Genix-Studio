import streamlit as st

def get_config():
    """Get configuration from sidebar."""
    config = {
        "create_packshot": False,
        "add_shadow": False,
        "lifestyle_shot": False,
        "background_color": "#FFFFFF",
        "shadow_type": "natural",
        "scene_description": "",
        "num_results": 1,
        "aspect_ratio": "1:1",
        "sync": True
    }
    
    st.sidebar.header("Configuration")
    
    # Image Generation Settings
    st.sidebar.subheader("Image Generation")
    config["num_results"] = st.sidebar.slider("Number of Results", 1, 4, 1)
    config["aspect_ratio"] = st.sidebar.selectbox(
        "Aspect Ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"]
    )
    config["sync"] = st.sidebar.checkbox("Wait for Results", True)
    
    # Packshot Settings
    st.sidebar.subheader("Packshot")
    config["create_packshot"] = st.sidebar.checkbox(
        "Create Packshot",
        help="Create a professional product packshot"
    )
    if config["create_packshot"]:
        config["background_color"] = st.sidebar.color_picker(
            "Background Color",
            "#FFFFFF"
        )
    
    # Shadow Settings
    st.sidebar.subheader("Shadow")
    config["add_shadow"] = st.sidebar.checkbox(
        "Add Shadow",
        help="Add shadow to the product image"
    )
    if config["add_shadow"]:
        config["shadow_type"] = st.sidebar.selectbox(
            "Shadow Type",
            ["Natural", "Drop"]
        ).lower()
    
    # Lifestyle Shot Settings
    st.sidebar.subheader("Lifestyle Shot")
    config["lifestyle_shot"] = st.sidebar.checkbox(
        "Create Lifestyle Shot",
        help="Generate lifestyle context for the product"
    )
    if config["lifestyle_shot"]:
        config["scene_description"] = st.sidebar.text_area(
            "Scene Description",
            help="Describe the environment for the lifestyle shot"
        )
    
    return config 