"""
Main Entry Point for StyleBot - Customer Interaction AI System
A Streamlit-based chat interface for the custom clothing e-commerce platform.
"""

import os
os.environ["STREAMLIT_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_WATCHER_IGNORE_MODULES"] = "torch"

import streamlit as st
import torch
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import our modules
from app.agent import stylebot
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="StyleBot - AI Design Assistant",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left: 4px solid #ff6b6b;
    }
    .bot-message {
        background-color: #e8f4f8;
        border-left: 4px solid #4ecdc4;
    }
    .suggestion-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .suggestion-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .design-colors {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .color-chip {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 1px solid #ccc;
    }
    .stats-metric {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "streamlit_user"
    
    if 'design_mode' not in st.session_state:
        st.session_state.design_mode = False


def display_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message"""
    css_class = "user-message" if is_user else "bot-message"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{"You" if is_user else "StyleBot"}:</strong><br>
            {message.get('content', message.get('message', ''))}
        </div>
        """, unsafe_allow_html=True)


def display_suggestions(suggestions: List[Dict[str, Any]]):
    """Display interactive suggestions"""
    if not suggestions:
        return
    
    st.markdown("### 💡 Suggestions")
    
    cols = st.columns(min(len(suggestions), 3))
    
    for i, suggestion in enumerate(suggestions):
        col_idx = i % 3
        
        with cols[col_idx]:
            with st.container():
                # Create suggestion card
                card_html = f"""
                <div class="suggestion-card">
                    <h4>{suggestion.get('title', 'Suggestion')}</h4>
                    <p>{suggestion.get('description', '')}</p>
                """
                
                # Add colors for design suggestions
                if suggestion.get('type') == 'design' and suggestion.get('colors'):
                    colors_html = '<div class="design-colors">'
                    for color in suggestion['colors']:
                        # Simple color mapping - in production, use a proper color library
                        color_code = get_color_code(color)
                        colors_html += f'<div class="color-chip" style="background-color: {color_code};" title="{color}"></div>'
                    colors_html += '</div>'
                    card_html += colors_html
                
                card_html += "</div>"
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Add interaction button
                import uuid
                button_key = f"suggestion_{i}_{suggestion.get('title', 'btn')}_{uuid.uuid4()}"
                if st.button(f"Select", key=button_key):
                    handle_suggestion_click(suggestion)


def get_color_code(color_name: str) -> str:
    """Simple color name to hex code mapping"""
    color_map = {
        'red': '#ff0000', 'blue': '#0000ff', 'green': '#008000',
        'yellow': '#ffff00', 'purple': '#800080', 'orange': '#ffa500',
        'pink': '#ffc0cb', 'black': '#000000', 'white': '#ffffff',
        'gray': '#808080', 'brown': '#a52a2a', 'navy': '#000080',
        'teal': '#008080', 'olive': '#808000', 'maroon': '#800000',
        'lime green': '#32cd32', 'hot pink': '#ff69b4', 'turquoise': '#40e0d0',
        'beige': '#f5f5dc', 'cream': '#fffdd0', 'tan': '#d2b48c',
        'rust': '#b7410e', 'forest green': '#228b22', 'aqua': '#00ffff',
        'sandy beige': '#f4a460', 'gold': '#ffd700', 'deep red': '#8b0000',
        'light pink': '#ffb6c1', 'lavender': '#e6e6fa', 'mint green': '#98fb98',
        'baby blue': '#87ceeb', 'peach': '#ffcba4', 'electric blue': '#7df9ff',
        'bright yellow': '#ffff00', 'burgundy': '#800020', 'burnt orange': '#cc5500',
        'golden yellow': '#ffdf00', 'dark green': '#006400', 'light green': '#90ee90',
        'light blue': '#add8e6'
    }
    return color_map.get(color_name.lower(), '#cccccc')


def handle_suggestion_click(suggestion: Dict[str, Any]):
    """Handle suggestion click"""
    suggestion_type = suggestion.get('type')
    action = suggestion.get('action')
    
    if action == 'select_design':
        design_data = suggestion.get('data', {})
        st.session_state.messages.append({
            'role': 'user',
            'content': f"I like the {design_data.get('title', 'design')} suggestion. Can you tell me more about it?"
        })
        
        response_text = f"""Great choice! You've selected the **{design_data.get('title', 'design')}**.

**Design Details:**
- **Style:** {design_data.get('style', 'N/A').title()}
- **Colors:** {', '.join(design_data.get('colors', []))}
- **Theme:** {design_data.get('theme', 'N/A').title()}
- **Placement:** {design_data.get('placement', 'N/A')}
- **Print Method:** {design_data.get('print_method', 'N/A').title()}

{design_data.get('description', '')}

Would you like me to refine this design further, or would you like to see pricing and ordering information?"""
        
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response_text,
            'type': 'design_selection'
        })
        
    elif action == 'start_design':
        st.session_state.design_mode = True
        st.session_state.messages.append({
            'role': 'user',
            'content': "I want to start designing a custom item"
        })
        
    elif action == 'browse_products':
        st.session_state.messages.append({
            'role': 'user',
            'content': "Can you show me what products you have available?"
        })
    
    st.rerun()


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">👕 StyleBot - AI Design Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Welcome to Custom Clothing Co.! I'm StyleBot, your AI design assistant. 🎨")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 StyleBot Dashboard")
        
        # Display conversation stats
        if hasattr(stylebot, 'context') and stylebot.context.interaction_count > 0:
            stats = stylebot.get_conversation_stats()
            st.markdown("### 📊 Session Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Interactions", stats['interaction_count'])
            with col2:
                st.metric("Topic", stats.get('current_topic', 'General').title())
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🎨 Get Design Inspiration"):
            st.session_state.messages.append({
                'role': 'user',
                'content': "Show me some trending design ideas"
            })
            st.rerun()
        
        if st.button("👕 Browse Products"):
            st.session_state.messages.append({
                'role': 'user',
                'content': "What products do you have available?"
            })
            st.rerun()
        
        if st.button("❓ Get Help"):
            st.session_state.messages.append({
                'role': 'user',
                'content': "I need help with your service"
            })
            st.rerun()
        
        if st.button("🔄 Clear Chat"):
            st.session_state.messages = []
            stylebot.context.conversation_history = []
            st.rerun()
        
        # Configuration
        st.markdown("### ⚙️ Configuration")
        
        # Model selection
        model_option = st.selectbox(
            "AI Model",
            ["OpenAI GPT-4", "Local Model", "Fallback Mode"],
            help="Choose the AI model for responses"
        )
        
        # API key input
        if model_option == "OpenAI GPT-4":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=config.openai_api_key or "",
                help="Enter your OpenAI API key for better responses"
            )
            if api_key:
                config.openai_api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
        
        # Design preferences
        st.markdown("### 🎨 Design Preferences")
        style_preference = st.selectbox(
            "Preferred Style",
            ["Any", "Minimalist", "Vintage", "Modern", "Geometric", "Organic", "Abstract"]
        )
        
        color_preference = st.selectbox(
            "Color Palette",
            ["Any", "Vibrant", "Pastel", "Monochrome", "Earth Tones", "Ocean", "Sunset"]
        )
    
    # Chat interface
    st.markdown("## 💬 Chat with StyleBot")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        # Welcome message
        if not st.session_state.messages:
            welcome_msg = {
                'role': 'assistant',
                'content': """Hi there! I'm StyleBot, your AI design assistant! 👋

I'm here to help you create amazing custom clothing designs. I can:

🎨 **Generate creative design ideas** based on your preferences
👕 **Answer questions** about our products and services  
📦 **Help with orders** and shipping information
💡 **Provide design consultation** for your custom items

What would you like to create today? Just tell me about your style preferences, or ask me anything!""",
                'suggestions': [
                    {
                        'type': 'suggestion',
                        'title': '🎨 Design a Custom T-Shirt',
                        'description': 'Create a unique t-shirt design',
                        'action': 'start_design'
                    },
                    {
                        'type': 'suggestion',
                        'title': '👕 Browse Products',
                        'description': 'See available products and pricing',
                        'action': 'browse_products'
                    },
                    {
                        'type': 'suggestion',
                        'title': '✨ Get Trending Ideas',
                        'description': 'See what\'s popular right now',
                        'action': 'trending_designs'
                    }
                ]
            }
            st.session_state.messages.append(welcome_msg)
        
        # Display messages
        for message in st.session_state.messages:
            is_user = message['role'] == 'user'
            display_message(message, is_user)
            
            # Display suggestions for assistant messages
            if not is_user and message.get('suggestions'):
                display_suggestions(message['suggestions'])
    
    # Chat input
    with st.container():
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get bot response
            with st.spinner("StyleBot is thinking..."):
                try:
                    response = stylebot.chat(user_input, st.session_state.user_id)
                    
                    # Add bot response
                    bot_message = {
                        'role': 'assistant',
                        'content': response['message'],
                        'type': response.get('type', 'general'),
                        'suggestions': response.get('suggestions', [])
                    }
                    
                    st.session_state.messages.append(bot_message)
                    
                except Exception as e:
                    error_message = {
                        'role': 'assistant',
                        'content': f"I'm sorry, I encountered an error: {str(e)}. Please try again or contact support.",
                        'type': 'error'
                    }
                    st.session_state.messages.append(error_message)
                    logger.error(f"Chat error: {str(e)}")
            
            st.rerun()


def run_cli_interface():
    """Simple CLI interface for testing"""
    print("👕 StyleBot - Customer Interaction AI")
    print("=" * 40)
    print("Type 'quit' to exit, 'help' for commands")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- 'quit' or 'exit': End the conversation")
                print("- 'stats': Show conversation statistics")
                print("- 'clear': Clear conversation history")
                print("- Or just chat normally!")
                continue
            
            if user_input.lower() == 'stats':
                stats = stylebot.get_conversation_stats()
                print(f"\n📊 Conversation Stats:")
                print(f"Interactions: {stats['interaction_count']}")
                print(f"Session Duration: {stats['session_duration']}")
                print(f"Current Topic: {stats.get('current_topic', 'General')}")
                continue
            
            if user_input.lower() == 'clear':
                stylebot.context.conversation_history = []
                print("🔄 Conversation history cleared!")
                continue
            
            if not user_input:
                continue
            
            # Get response from StyleBot
            response = stylebot.chat(user_input)
            
            print(f"\nStyleBot: {response['message']}")
            
            # Show suggestions if any
            if response.get('suggestions'):
                print(f"\n💡 Suggestions:")
                for i, suggestion in enumerate(response['suggestions'][:3], 1):
                    print(f"{i}. {suggestion['title']}: {suggestion['description']}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            logger.error(f"CLI error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli_interface()
    else:
        # Run Streamlit app
        main() 