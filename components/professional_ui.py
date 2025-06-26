import streamlit as st
from typing import Dict, Any, Optional
import time

class ProfessionalUI:
    """Professional UI components and styling for the application"""
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS for professional appearance"""
        st.markdown("""
        <style>
        /* Main app styling */
        .main {
            padding-top: 2rem;
        }
        
        /* Custom header */
        .custom-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        
        .custom-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .custom-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Feature cards */
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .feature-card h3 {
            color: #333;
            margin-top: 0;
            font-size: 1.3rem;
        }
        
        .feature-card p {
            color: #666;
            margin-bottom: 0;
        }
        
        /* Progress indicators */
        .progress-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .progress-step {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .progress-step.active {
            color: #667eea;
            font-weight: 600;
        }
        
        .progress-step.completed {
            color: #28a745;
        }
        
        /* Custom buttons */
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Success/Error messages */
        .success-message {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .error-message {
            background: linear-gradient(90deg, #dc3545, #fd7e14);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        /* Loading animation */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Image gallery */
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .image-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        
        .image-card:hover {
            transform: scale(1.02);
        }
        
        /* Metrics dashboard */
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header(title: str, subtitle: str = ""):
        """Render professional header"""
        st.markdown(f"""
        <div class="custom-header">
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_feature_card(title: str, description: str, icon: str = "🎨"):
        """Render a feature card"""
        st.markdown(f"""
        <div class="feature-card">
            <h3>{icon} {title}</h3>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_indicator(steps: list, current_step: int):
        """Render progress indicator"""
        progress_html = '<div class="progress-container">'
        
        for i, step in enumerate(steps):
            if i < current_step:
                status_class = "completed"
                icon = "✅"
            elif i == current_step:
                status_class = "active"
                icon = "🔄"
            else:
                status_class = ""
                icon = "⏳"
            
            progress_html += f'''
            <div class="progress-step {status_class}">
                {icon} {step}
            </div>
            '''
        
        progress_html += '</div>'
        st.markdown(progress_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_animation(message: str = "Processing..."):
        """Render loading animation"""
        st.markdown(f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <span style="margin-left: 1rem; font-weight: 600;">{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_success_message(message: str):
        """Render success message"""
        st.markdown(f"""
        <div class="success-message">
            ✅ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_error_message(message: str):
        """Render error message"""
        st.markdown(f"""
        <div class="error-message">
            ❌ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metrics_dashboard(metrics: Dict[str, Any]):
        """Render metrics dashboard"""
        metrics_html = '<div class="metrics-container">'
        
        for label, value in metrics.items():
            metrics_html += f'''
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            '''
        
        metrics_html += '</div>'
        st.markdown(metrics_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_image_gallery(images: list, columns: int = 3):
        """Render image gallery"""
        cols = st.columns(columns)
        
        for i, image_data in enumerate(images):
            with cols[i % columns]:
                if isinstance(image_data, dict):
                    st.image(image_data['url'], caption=image_data.get('caption', ''))
                    if 'download_url' in image_data:
                        st.download_button(
                            "Download", 
                            image_data['download_url'],
                            file_name=f"image_{i+1}.jpg"
                        )
                else:
                    st.image(image_data)
    
    @staticmethod
    def create_professional_sidebar():
        """Create professional sidebar with branding"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2 style="color: #667eea; margin-bottom: 0.5rem;">🎨 ProductAI Pro</h2>
                <p style="color: #666; font-size: 0.9rem;">Professional AI Image Generation</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📋 Navigation")
            page = st.selectbox(
                "Choose a feature:",
                ["🎨 Generate Images", "📸 Product Photography", "🎭 A/B Testing", 
                 "🎨 Brand Kit", "📊 Analytics", "⚙️ Settings"]
            )
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("### 📊 Quick Stats")
            st.metric("Images Generated", "1,234", "12%")
            st.metric("Success Rate", "98.5%", "2.1%")
            st.metric("Avg. Processing", "3.2s", "-0.8s")
            
            return page
