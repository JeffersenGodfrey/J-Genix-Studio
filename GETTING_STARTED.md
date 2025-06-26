# 🚀 Getting Started with AdSnap Studio

## 📋 Prerequisites

1. **Get Your Bria AI API Key**:
   - Visit [Bria AI](https://bria.ai)
   - Sign up for an account
   - Navigate to your dashboard
   - Generate an API key

2. **Python Environment**:
   - Python 3.8+ installed
   - All dependencies installed (already done!)

## 🔧 Setup Instructions

### 1. Configure Your API Key

Edit the `.env` file in this directory:
```bash
# Replace with your actual API key from Bria AI
BRIA_API_KEY= 2038ba8e5ce8486b9cf75f7c162942d0
```

### 2. Run the Application

```powershell
# Navigate to the project directory
cd j-genix-studio

# Run the Streamlit app
python -m streamlit run app.py
```

### 3. Access the Application

Open your browser and go to: `http://localhost:8501`

## 🎨 Features Overview

### **Tab 1: Generate Image**
- Create images from text prompts
- Choose different styles (Realistic, Artistic, Cartoon, etc.)
- Adjust aspect ratios and quality settings
- AI-powered prompt enhancement

### **Tab 2: Lifestyle Shot**
- Upload product images
- Create professional packshots
- Add realistic shadows
- Generate lifestyle photography

### **Tab 3: Generative Fill**
- Edit parts of images using AI
- Draw masks to specify areas to modify
- Fill or replace image regions

### **Tab 4: Erase Elements**
- Remove unwanted objects from images
- Clean up backgrounds
- Professional image editing

## 📁 Project Structure

```
j-genix-studio/
├── app.py                 # Main Streamlit application
├── .env                   # Your API key configuration
├── requirements.txt       # Python dependencies
├── components/            # UI components
│   ├── image_preview.py
│   ├── sidebar.py
│   └── uploader.py
├── services/              # API service functions
│   ├── hd_image_generation.py
│   ├── lifestyle_shot.py
│   ├── packshot.py
│   ├── shadow.py
│   ├── generative_fill.py
│   ├── erase_foreground.py
│   └── prompt_enhancement.py
└── workflows/             # Complex workflows
    └── generate_ad_set.py
```

## 🛠️ Customization Tips

### Adding New Features
1. Create new service functions in `services/`
2. Import them in `services/__init__.py`
3. Add UI components in `app.py`

### Modifying the UI
- Edit `app.py` for main interface changes
- Modify components in `components/` folder
- Streamlit documentation: https://docs.streamlit.io

### API Integration
- All API calls are in the `services/` folder
- Each service handles a specific Bria AI endpoint
- Error handling and response parsing included

## 🔍 Understanding the Code

### Main Application (`app.py`)
- **Lines 1-42**: Imports and configuration
- **Lines 43-58**: Session state management
- **Lines 139-925**: Main UI with tabs and functionality

### Service Functions (`services/`)
- Each file handles one API endpoint
- Consistent error handling
- Type hints for better code understanding

### Key Functions to Study:
1. `generate_hd_image()` - Text to image generation
2. `create_packshot()` - Product photography
3. `add_shadow()` - Shadow effects
4. `lifestyle_shot_by_text()` - Lifestyle photography

## 🎯 Next Steps

1. **Get your API key** and update the `.env` file
2. **Run the application** and explore the features
3. **Try generating your first image** with a simple prompt
4. **Experiment with different settings** to understand the options
5. **Look at the code** to understand how it works
6. **Customize and extend** the application for your needs

## 💡 Learning Resources

- **Bria AI Documentation**: https://docs.bria.ai
- **Streamlit Documentation**: https://docs.streamlit.io
- **Python Requests Library**: https://docs.python-requests.org

## 🆘 Troubleshooting

### Common Issues:
1. **API Key Error**: Make sure your API key is valid and has credits
2. **Import Errors**: Ensure all dependencies are installed
3. **Port Issues**: Try a different port with `streamlit run app.py --server.port 8502`

### Getting Help:
- Check the console output for error messages
- Review the API response in the debug sections
- Ensure your API key has sufficient credits
