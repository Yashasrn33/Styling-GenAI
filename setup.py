"""
Setup script for StyleBot - Customer Interaction AI System
This script helps users set up and configure the system.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎨 {title}")
    print("="*60)


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\n🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "data",
        "data/vector_index",
        "logs",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_env_file():
    """Create environment file if it doesn't exist"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_content = """# StyleBot Environment Configuration
# Copy this file to .env and fill in your actual values

# OpenAI Configuration (Optional - system will work without this)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Hugging Face Configuration (Optional)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=your_huggingface_token_here

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Design Generation Settings
DESIGN_CREATIVITY=0.8
MAX_DESIGN_SUGGESTIONS=3

# RAG System Settings
TOP_K_RESULTS=3
SIMILARITY_THRESHOLD=0.7
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Model Settings
DEFAULT_MODEL=openai  # Options: openai, local, fallback
TEMPERATURE=0.7
MAX_TOKENS=1000

# Feature Flags
ENABLE_DESIGN_SUGGESTIONS=true
ENABLE_RAG_SYSTEM=true
ENABLE_CONVERSATION_MEMORY=true
ENABLE_ANALYTICS=false
"""
    
    if not os.path.exists(".env"):
        with open(".env.example", "w") as f:
            f.write(env_content)
        print("✅ Created .env.example file")
        print("   Copy this to .env and add your API keys")
    else:
        print("✅ .env file already exists")


def test_system():
    """Test basic system functionality"""
    print("\n🧪 Testing system components...")
    
    try:
        # Test imports
        from app.design_suggestions import design_engine
        from app.rag import rag_system
        from app.agent import stylebot
        print("✅ All modules imported successfully")
        
        # Test design engine
        suggestions = design_engine.generate_suggestions("minimalist design", "t-shirt", 1)
        if suggestions:
            print("✅ Design engine working")
        else:
            print("⚠️  Design engine returned no suggestions")
        
        # Test basic chat (without RAG to avoid long initialization)
        response = stylebot.chat("Hello", "test_user")
        if response and response.get('message'):
            print("✅ Chat system working")
        else:
            print("⚠️  Chat system issue")
            
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return False


def download_models():
    """Download required models"""
    print("\n📥 Downloading required models...")
    
    try:
        # Download sentence transformer model
        from sentence_transformers import SentenceTransformer
        print("   Downloading embedding model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Embedding model downloaded")
        
        return True
    except Exception as e:
        print(f"⚠️  Model download issue: {str(e)}")
        print("   Models will be downloaded on first use")
        return False


def main():
    """Main setup function"""
    print_header("StyleBot Setup")
    print("This script will set up StyleBot - Customer Interaction AI System")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Download models
    download_models()
    
    # Test system
    if test_system():
        print_header("Setup Complete! 🎉")
        print("""
✅ StyleBot has been set up successfully!

🚀 Next Steps:
1. (Optional) Add your OpenAI API key to .env file for better responses
2. Run the demo: python demo.py
3. Start the web interface: streamlit run main.py
4. Or use CLI mode: python main.py --cli

📚 Documentation:
- README.md - Complete documentation
- demo.py - Interactive demonstrations
- main.py - Web and CLI interfaces

💡 Quick Test:
python demo.py

🌐 Web Interface:
streamlit run main.py

❓ Need Help?
Check the README.md file or run: python demo.py
        """)
    else:
        print_header("Setup Issues Detected")
        print("""
⚠️  Setup completed with some issues.

🔧 Troubleshooting:
1. Make sure all dependencies are installed: pip install -r requirements.txt
2. Check Python version (3.8+ required): python --version
3. Try running the demo: python demo.py
4. Check the logs for detailed error messages

📞 Support:
If issues persist, please check the README.md file or create an issue.
        """)


if __name__ == "__main__":
    main() 