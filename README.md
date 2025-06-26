# 🎨 J-Genix Studio

**Professional AI-Powered Creative Suite for Modern Businesses**

A comprehensive Streamlit application that combines advanced AI image generation, editing, and marketing copy creation into one powerful platform. Built with Bria AI's cutting-edge APIs and free open-source AI models.

## 🌟 Features

### 🖼️ **Image Generation & Editing**
- **HD Image Generation**: Create high-quality product images from text prompts
- **Logo Generation**: Professional logo creation with multiple styles and formats
- **Lifestyle Shots**: Generate contextual product images with backgrounds
- **Generative Fill**: AI-powered image completion and editing
- **Element Removal**: Remove unwanted objects from images
- **Background Effects**: Add shadows, remove backgrounds, create packshots

### 📝 **Free AI Copywriter**
- **No API Keys Required**: Powered by Hugging Face open-source models
- **Multiple Content Types**: Product descriptions, social media posts, ads, and more
- **Tone Variations**: Professional, casual, creative, luxury, urgent
- **Copy Variations**: Generate multiple versions for A/B testing
- **Brand Kit Integration**: Consistent messaging across all content

### 🎨 **Brand Management**
- **Brand Kit Creation**: Store brand colors, fonts, and messaging
- **Color Extraction**: Extract brand colors from uploaded images
- **Consistent Branding**: Apply brand elements across all generated content

## 🚀 Quick Deployment

### **Option 1: One-Click Streamlit Cloud Deployment (Recommended)**

1. **Fork this repository** to your GitHub account
2. **Run locally** to see the Deploy button:
   ```bash
   streamlit run app.py
   ```
3. **Click the "Deploy" button** in the top-right corner
4. **Configure secrets** in Streamlit Cloud:
   ```toml
   BRIA_API_KEY = "your_bria_api_key_here"
   ```
5. **Your app will be live** at `https://your-app-name.streamlit.app`

### **Option 2: Local Development**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JeffersenGodfrey/J-Genix-Studio.git
   cd J-Genix-Studio
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file
   echo "BRIA_API_KEY=your_api_key_here" > .env
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### **Required API Keys**
- **Bria AI API Key**: For image generation and editing features
  - Sign up at [Bria AI](https://bria.ai)
  - Get your API key from the dashboard
  - Add to `.env` file or Streamlit Cloud secrets

### **Free Features (No API Key Required)**
- ✅ **AI Copywriter**: Complete marketing copy generation
- ✅ **Brand Kit Management**: Store and manage brand assets
- ✅ **Copy Variations**: Generate multiple content versions

## 📱 User Interface

### **7 Main Tabs**
1. **🖼️ Generate Image**: HD image creation from prompts
2. **🎨 Logo Generation**: Professional logo design
3. **🎯 Brand Kit**: Brand asset management
4. **🏠 Lifestyle Shot**: Contextual product photography
5. **🔧 Generative Fill**: AI image editing and completion
6. **🗑️ Erase Elements**: Object removal from images
7. **📝 Free AI Copywriter**: Marketing content generation

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **AI Services**: Bria AI APIs, Hugging Face Transformers
- **Image Processing**: Pillow, NumPy
- **Deployment**: Streamlit Cloud, Docker-ready
- **Languages**: Python 3.8+

## 🎯 Use Cases

- **E-commerce**: Product photography and descriptions
- **Marketing Agencies**: Campaign assets and copy
- **Small Businesses**: Professional branding materials
- **Content Creators**: Social media assets
- **Startups**: MVP marketing materials

## 📊 Business Model Ready

- **Freemium Structure**: Free copywriter + paid image features
- **User Authentication**: Built-in user management
- **Usage Tracking**: Analytics and monitoring ready
- **Scalable Architecture**: Production deployment ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Bria AI](https://bria.ai) for powerful image generation APIs
- [Hugging Face](https://huggingface.co) for open-source AI models
- [Streamlit](https://streamlit.io) for the amazing web framework
- The open-source community for inspiration and tools
