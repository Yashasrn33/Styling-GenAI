# 🎨 StyleBot - Generative AI Customer Interaction System

A comprehensive AI-powered customer interaction system for a fictional custom clothing e-commerce platform. StyleBot combines Retrieval-Augmented Generation (RAG), creative design suggestions, and natural language processing to provide intelligent customer support and design consultation.

![StyleBot Demo](https://img.shields.io/badge/StyleBot-AI%20Assistant-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 🤖 Intelligent Conversational Agent
- **Multi-Intent Classification**: Automatically categorizes user queries (product inquiry, design consultation, FAQ, shipping, support)
- **Context-Aware Responses**: Maintains conversation history and context across interactions
- **Memory Management**: Uses LangChain's conversation memory for coherent multi-turn conversations

### 🎨 Generative Design Suggestions
- **AI-Powered Design Generation**: Creates unique clothing design concepts based on user preferences
- **Style Analysis**: Interprets natural language design requests (e.g., "minimalist geometric pattern")
- **Color Palette Matching**: Suggests appropriate color combinations for different themes
- **Design Refinement**: Iteratively improves designs based on user feedback

### 📚 Retrieval-Augmented Generation (RAG)
- **Knowledge Base Integration**: Searches through product catalogs, FAQs, and shipping information
- **Semantic Search**: Uses FAISS and sentence transformers for intelligent document retrieval
- **Context Enhancement**: Provides relevant information to improve response accuracy

### 🖥️ Multiple Interfaces
- **Streamlit Web App**: Beautiful, interactive chat interface with visual design suggestions
- **CLI Mode**: Command-line interface for testing and development
- **API Ready**: Designed for easy integration with FastAPI for production deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- (Optional) OpenAI API key for enhanced responses

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd customer_interaction_ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional)
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Run the application**

**Web Interface (Streamlit):**
```bash
streamlit run main.py
```

**CLI Interface:**
```bash
python main.py --cli
```

## 📁 Project Structure

```
customer_interaction_ai/
│
├── app/
│   ├── agent.py                # Conversational agent logic
│   ├── rag.py                  # Retrieval Augmented Generation
│   ├── design_suggestions.py   # AI design generation
│   └── knowledge_base/         # Knowledge base files
│       ├── faqs.md            # Frequently asked questions
│       ├── shipping.md        # Shipping information
│       └── products.json      # Product catalog
│
├── main.py                     # Streamlit/CLI entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 💬 Usage Examples

### Design Consultation
```
User: "I want a custom hoodie with a minimal design inspired by nature"

StyleBot: I'd love to help you create the perfect design! Based on your preferences, here are some creative suggestions:

Option 1: Organic Nature Design
A casual organic design featuring trees in white, black, and gray, positioned centered on the front chest with flowing, natural curves and clean, mathematical precision. This design would work beautifully with screen printing.

Option 2: Geometric Forest Design  
Picture a geometric-inspired leaf patterns design using forest green, tan, and olive, positioned large design across the entire front with designs inspired by the natural world. Perfect for digital printing to capture all the color nuances.

Which design catches your eye? I can refine any of these based on your feedback!
```

### Product Inquiry
```
User: "Do you have red hoodies in XL?"

StyleBot: Yes! We have the Custom Design Hoodie available in red and XL size. Here are the details:

- **Product**: Custom Design Hoodie
- **Price**: $45.99 (base price)
- **Available Colors**: black, white, gray, navy, red, green, blue
- **Available Sizes**: XS, S, M, L, XL, XXL
- **Material**: 80% cotton, 20% polyester
- **Features**: drawstring hood, kangaroo pocket, ribbed cuffs
- **Lead Time**: 7-10 business days

Would you like to customize this hoodie with a design, or do you need more information about our customization options?
```

### FAQ Support
```
User: "What's your return policy?"

StyleBot: We accept returns within 30 days for unworn, unaltered items in original condition. Custom items with personalized text or images are non-returnable unless there's a production error.

Here are the key points of our return policy:
- 30-day return window from delivery
- Items must be unworn and in original condition
- Custom/personalized items are generally non-returnable
- Production errors are covered with full refund/replacement
- Contact us within 7 days for any quality issues

Need help with a specific return? I can guide you through the process!
```

## 🔧 Configuration

### Model Configuration
Edit `config.py` to customize:

```python
# OpenAI Configuration
openai_model: str = "gpt-4"
openai_temperature: float = 0.7

# Vector Store Configuration
embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
top_k_results: int = 3

# Design Generation
design_max_suggestions: int = 3
design_creativity: float = 0.8
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (optional, falls back to local models)

## 🎨 Design System Architecture

### 1. **Intent Classification**
The system automatically classifies user intents into categories:
- Product Inquiry
- Design Consultation  
- FAQ
- Shipping
- Support
- General Chat

### 2. **RAG Pipeline**
```
User Query → Embedding → Vector Search → Context Retrieval → LLM Generation → Response
```

### 3. **Design Generation**
```
User Preferences → Style Analysis → Theme Selection → Color Palette → Description Generation → Suggestions
```

## 🚀 Deployment Options

### Option 1: Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

### Option 2: Docker (coming soon)
```bash
docker build -t stylebot .
docker run -p 8501:8501 stylebot
```

### Option 3: FastAPI Production
Create `api.py`:
```python
from fastapi import FastAPI
from app.agent import stylebot

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(message: str, user_id: str = "api_user"):
    return stylebot.chat(message, user_id)
```

## 📊 Performance Metrics

- **Response Time**: < 2 seconds for most queries
- **Design Generation**: 3 unique suggestions per request
- **Knowledge Base**: 50+ FAQ entries, 5 product categories
- **Context Memory**: Maintains last 20 interactions

## 🧪 Testing

### Manual Testing
```bash
# Test CLI interface
python main.py --cli

# Test individual components
python -c "from app.design_suggestions import design_engine; print(design_engine.generate_suggestions('minimalist t-shirt'))"
```

### Example Test Cases
1. **Product Search**: "Do you have blue t-shirts?"
2. **Design Request**: "Create a vintage band t-shirt design"
3. **FAQ Query**: "How long does shipping take?"
4. **Complex Request**: "I need a custom hoodie for my startup, something modern and tech-inspired"

## 🔮 Future Enhancements

### Planned Features
- [ ] **Visual Design Generation**: Integration with DALL-E or Stable Diffusion
- [ ] **Advanced Personalization**: User preference learning and recommendation system
- [ ] **Multi-language Support**: Internationalization for global customers
- [ ] **Voice Interface**: Speech-to-text and text-to-speech capabilities
- [ ] **Real-time Collaboration**: Multi-user design sessions
- [ ] **Integration APIs**: Shopify, WooCommerce, and other e-commerce platforms

### Technical Improvements
- [ ] **Caching Layer**: Redis for faster response times
- [ ] **A/B Testing**: Experiment framework for design suggestions
- [ ] **Analytics Dashboard**: Customer interaction insights
- [ ] **Mobile App**: React Native or Flutter mobile interface

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## ⚖️ Ethical Considerations

### Bias Prevention
- **Cultural Sensitivity**: Design suggestions avoid culturally inappropriate content
- **Inclusive Design**: Promotes diversity in color palettes and style suggestions
- **Fair Representation**: Ensures balanced representation across different demographics

### Privacy Protection
- **Data Minimization**: Only collects necessary conversation data
- **User Consent**: Clear privacy policy and data usage explanation
- **Secure Storage**: Encrypts sensitive customer information

### Transparency
- **AI Disclosure**: Clearly identifies AI-generated content
- **Limitation Awareness**: Informs users of system capabilities and limitations
- **Human Escalation**: Provides easy access to human support when needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For conversation memory and document processing
- **Sentence Transformers**: For semantic search capabilities
- **Streamlit**: For the beautiful web interface
- **FAISS**: For efficient vector similarity search
- **OpenAI**: For advanced language model capabilities

## 📞 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Email**: stylebot-support@example.com

---

**Made with ❤️ for the future of AI-powered customer experience**

## 🎯 Demo Conversation Flow

Here's a complete example of how StyleBot handles a complex customer interaction:

```
👤 User: Hi! I'm looking for a custom t-shirt for my gaming clan

🤖 StyleBot: Hi there! I'd love to help you create a custom t-shirt for your gaming clan! 🎮

That sounds like an exciting project. To create the perfect design, I'd like to know more about your preferences:

• What's the name or theme of your gaming clan?
• Do you prefer a bold, aggressive look or something more subtle?
• Any specific colors that represent your team?
• What games do you primarily play?

Based on what you tell me, I can generate some creative design concepts that capture your clan's spirit!

👤 User: We're called "Neon Shadows" and we play mostly cyberpunk games. We like dark themes with neon accents.

🤖 StyleBot: Perfect! "Neon Shadows" is a fantastic name for a cyberpunk gaming clan. Based on your preferences, here are some creative design suggestions:

**Option 1: Street Art Neon Design**
A bold street_art design featuring digital glitch in electric blue, hot pink, and black, positioned large design across the entire front with urban-inspired street art aesthetics. Perfect for digital printing to capture all the color nuances.

**Option 2: Geometric Technology Design**  
Picture a geometric-inspired circuit patterns design using electric blue, black, and lime green, positioned centered on the front chest with clean, mathematical precision. This design would work beautifully with screen printing.

**Option 3: Abstract Cyberpunk Design**
A bold abstract design featuring code snippets in hot pink, electric blue, and black, positioned statement design on the back with non-representational artistic expressions. The design would look stunning with a subtle texture overlay.

Which design resonates with your clan's vibe? I can refine any of these or create variations based on your feedback!

👤 User: I love option 1 but can we make it a bit more subtle? Maybe smaller and on the chest?

🤖 StyleBot: Great feedback! I've refined the design based on your input:

**Street Art Neon Design (Refined)**
A casual street_art design featuring digital glitch in electric blue, hot pink, and black, positioned small design on the left chest with urban-inspired street art aesthetics. This design would work beautifully with screen printing.

This smaller chest placement gives it a more professional, wearable look while still maintaining that cyberpunk edge your clan is known for. The neon colors will really pop against a black t-shirt base!

The refined design would work perfectly with:
- **Base Garment**: Premium Custom T-Shirt ($22.99)
- **Colors Available**: Black (recommended), navy, or gray
- **Print Method**: Digital printing for the neon color gradients
- **Estimated Lead Time**: 5-7 business days

How does this look? I can make further adjustments if needed, or we can move forward with sizing and ordering details!
```

This example showcases StyleBot's ability to:
- Understand context and themes
- Generate multiple creative options
- Respond to feedback and refine designs
- Provide practical implementation details
- Maintain an engaging, helpful tone throughout the conversation 