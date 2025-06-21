"""
Demo Script for StyleBot - Customer Interaction AI System
This script demonstrates the key capabilities of the system.
"""

import os
import sys
import time
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from app.agent import stylebot
from app.rag import rag_system
from app.design_suggestions import design_engine


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎨 {title}")
    print("="*60)


def print_response(response: Dict[str, Any]):
    """Print a formatted response"""
    print(f"\n🤖 StyleBot: {response['message']}")
    
    if response.get('suggestions'):
        print(f"\n💡 Suggestions ({len(response['suggestions'])}):")
        for i, suggestion in enumerate(response['suggestions'], 1):
            print(f"   {i}. {suggestion['title']}")
            if suggestion.get('colors'):
                print(f"      Colors: {', '.join(suggestion['colors'])}")
            print(f"      {suggestion['description']}")


def demo_basic_chat():
    """Demonstrate basic chat functionality"""
    print_header("Basic Chat Demonstration")
    
    test_queries = [
        "Hello! I'm new here, what can you help me with?",
        "What products do you have available?",
        "Do you have red hoodies in XL?",
        "What's your return policy?",
        "How long does shipping take?"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = stylebot.chat(query, "demo_user")
        print_response(response)
        time.sleep(1)  # Brief pause for readability


def demo_design_consultation():
    """Demonstrate design consultation capabilities"""
    print_header("Design Consultation Demonstration")
    
    design_queries = [
        "I want a custom hoodie with a minimal design inspired by nature",
        "Create a vintage band t-shirt design with dark colors",
        "I need something geometric and modern for my tech startup",
        "Design a playful t-shirt for kids with animals and bright colors"
    ]
    
    for query in design_queries:
        print(f"\n👤 User: {query}")
        response = stylebot.chat(query, "design_demo_user")
        print_response(response)
        time.sleep(1)


def demo_design_refinement():
    """Demonstrate design refinement capabilities"""
    print_header("Design Refinement Demonstration")
    
    # First, get initial design suggestions
    print(f"\n👤 User: I want a space-themed t-shirt design")
    response = stylebot.chat("I want a space-themed t-shirt design", "refinement_user")
    print_response(response)
    
    if response.get('suggestions') and stylebot.context.last_suggestions:
        # Refine the first suggestion
        design_id = stylebot.context.last_suggestions[0]['id']
        print(f"\n👤 User: Can you make the first design brighter and more colorful?")
        
        refined_response = stylebot.refine_design(design_id, "brighter and more colorful")
        print_response(refined_response)


def demo_rag_system():
    """Demonstrate RAG system capabilities"""
    print_header("Knowledge Base Retrieval Demonstration")
    
    print("🔧 Initializing RAG system...")
    try:
        rag_system.initialize(force_rebuild=True)
        print("✅ RAG system initialized successfully!")
        
        # Test different types of queries
        test_queries = [
            "hoodies pricing",
            "return policy details", 
            "shipping costs",
            "customization options",
            "t-shirt materials"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            context = rag_system.get_relevant_context(query)
            print(f"📚 Retrieved Context: {context[:200]}...")
            
    except Exception as e:
        print(f"❌ RAG system error: {str(e)}")


def demo_design_engine():
    """Demonstrate standalone design engine"""
    print_header("Design Engine Demonstration")
    
    test_preferences = [
        "minimalist geometric patterns",
        "vintage music-inspired designs",
        "bold cyberpunk aesthetics",
        "nature-inspired organic shapes",
        "playful cartoon animals"
    ]
    
    for preference in test_preferences:
        print(f"\n🎨 Preference: {preference}")
        suggestions = design_engine.generate_suggestions(preference, "t-shirt", 2)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n   Design {i}: {suggestion['title']}")
            print(f"   Style: {suggestion['style']}")
            print(f"   Colors: {', '.join(suggestion['colors'])}")
            print(f"   Description: {suggestion['description']}")


def demo_conversation_flow():
    """Demonstrate a realistic conversation flow"""
    print_header("Realistic Conversation Flow")
    
    conversation = [
        "Hi! I run a small coffee shop and want custom t-shirts for my staff",
        "We're called 'Bean There Coffee' and have a cozy, rustic vibe",
        "I like the second design! Can you make it a bit more professional?",
        "Perfect! What would be the pricing for 12 t-shirts?",
        "Great! How do I place the order?"
    ]
    
    user_id = "coffee_shop_demo"
    
    for message in conversation:
        print(f"\n👤 User: {message}")
        response = stylebot.chat(message, user_id)
        print_response(response)
        time.sleep(1.5)
    
    # Show conversation stats
    stats = stylebot.get_conversation_stats()
    print(f"\n📊 Conversation Statistics:")
    print(f"   Interactions: {stats['interaction_count']}")
    print(f"   Current Topic: {stats.get('current_topic', 'General')}")
    print(f"   Session Duration: {stats['session_duration']}")


def run_interactive_demo():
    """Run an interactive demo"""
    print_header("Interactive Demo Mode")
    print("Type your messages to chat with StyleBot. Type 'quit' to exit.")
    
    user_id = "interactive_demo"
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for trying StyleBot!")
                break
            
            if user_input.lower() == 'stats':
                stats = stylebot.get_conversation_stats()
                print(f"\n📊 Stats: {stats['interaction_count']} interactions, "
                      f"Topic: {stats.get('current_topic', 'General')}")
                continue
            
            if not user_input:
                continue
            
            response = stylebot.chat(user_input, user_id)
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for trying StyleBot!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main demo function"""
    print("🎨 StyleBot - Customer Interaction AI System Demo")
    print("=" * 60)
    print("This demo showcases the key capabilities of StyleBot.")
    print("Choose a demo mode:")
    print()
    print("1. 🚀 Full Demo (all features)")
    print("2. 💬 Basic Chat Demo")
    print("3. 🎨 Design Consultation Demo")
    print("4. 🔧 Design Refinement Demo")
    print("5. 📚 RAG System Demo")
    print("6. 🎯 Design Engine Demo")
    print("7. 🗣️  Conversation Flow Demo")
    print("8. 🎮 Interactive Demo")
    print("9. ❌ Exit")
    
    try:
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            demo_basic_chat()
            demo_design_consultation()
            demo_design_refinement()
            demo_rag_system()
            demo_design_engine()
            demo_conversation_flow()
            
        elif choice == '2':
            demo_basic_chat()
            
        elif choice == '3':
            demo_design_consultation()
            
        elif choice == '4':
            demo_design_refinement()
            
        elif choice == '5':
            demo_rag_system()
            
        elif choice == '6':
            demo_design_engine()
            
        elif choice == '7':
            demo_conversation_flow()
            
        elif choice == '8':
            run_interactive_demo()
            
        elif choice == '9':
            print("👋 Goodbye!")
            return
            
        else:
            print("❌ Invalid choice. Please try again.")
            main()
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")


if __name__ == "__main__":
    main() 