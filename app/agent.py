"""
Conversational Agent Module
Handles chat interactions, context management, and integrates RAG with design suggestions.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from config import config, PROMPT_TEMPLATES
from app.rag import rag_system
from app.design_suggestions import design_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of user queries"""
    PRODUCT_INQUIRY = "product_inquiry"
    FAQ = "faq"
    DESIGN_CONSULTATION = "design_consultation"
    GENERAL_CHAT = "general_chat"
    SHIPPING = "shipping"
    SUPPORT = "support"


@dataclass
class ConversationContext:
    """Holds conversation context and state"""
    user_id: str = "anonymous"
    session_id: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_topic: Optional[str] = None
    design_preferences: Dict[str, Any] = field(default_factory=dict)
    product_interests: List[str] = field(default_factory=list)
    last_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    interaction_count: int = 0
    started_at: datetime = field(default_factory=datetime.now)


class IntentClassifier:
    """Classifies user intents and query types"""
    
    def __init__(self):
        self.intent_keywords = {
            QueryType.PRODUCT_INQUIRY: [
                "product", "price", "cost", "buy", "purchase", "available", "stock",
                "size", "color", "material", "hoodie", "t-shirt", "shirt", "jacket",
                "do you have", "what colors", "what sizes", "how much"
            ],
            QueryType.FAQ: [
                "how do", "what is", "can i", "policy", "return", "refund", "exchange",
                "care instructions", "wash", "payment", "account", "discount"
            ],
            QueryType.DESIGN_CONSULTATION: [
                "design", "custom", "create", "want", "idea", "style", "pattern",
                "color scheme", "theme", "inspiration", "suggest", "recommend",
                "minimalist", "vintage", "modern", "geometric", "organic"
            ],
            QueryType.SHIPPING: [
                "shipping", "delivery", "ship", "order", "tracking", "when will",
                "how long", "express", "standard", "overnight", "international"
            ],
            QueryType.SUPPORT: [
                "help", "support", "problem", "issue", "contact", "phone", "email",
                "complaint", "error", "wrong", "cancel", "modify"
            ]
        }
    
    def classify_intent(self, user_input: str) -> Tuple[QueryType, float]:
        """Classify user intent and return confidence score"""
        user_input_lower = user_input.lower()
        
        scores = {}
        for query_type, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            scores[query_type] = score
        
        # Get the query type with highest score
        if not scores or max(scores.values()) == 0:
            return QueryType.GENERAL_CHAT, 0.5
        
        best_match = max(scores, key=scores.get)
        confidence = scores[best_match] / len(self.intent_keywords[best_match])
        
        return best_match, min(confidence, 1.0)


class LLMInterface:
    """Interface for LLM interactions"""
    
    def __init__(self):
        self.model_type = "openai" if config.openai_api_key else "local"
        logger.info(f"Using {self.model_type} model")
    
    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """Generate response using configured LLM"""
        max_tokens = max_tokens or config.openai_max_tokens
        
        if self.model_type == "openai" and config.openai_api_key:
            return self._generate_openai_response(prompt, max_tokens)
        else:
            return self._generate_local_response(prompt, max_tokens)
    
    def _generate_openai_response(self, prompt: str, max_tokens: int) -> str:
        """Generate response using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.openai_api_key)
            
            response = client.chat.completions.create(
                model=config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=config.openai_temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _generate_local_response(self, prompt: str, max_tokens: int) -> str:
        """Generate response using local model"""
        try:
            from transformers import pipeline
            
            # Use a simple text generation pipeline
            generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )
            
            response = generator(
                prompt,
                max_length=max_tokens,
                num_return_sequences=1,
                temperature=config.hf_temperature,
                pad_token_id=50256
            )
            
            return response[0]['generated_text']
            
        except Exception as e:
            logger.error(f"Local model error: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when LLM is unavailable"""
        return "I'm sorry, I'm having trouble processing your request right now. Please try again or contact our support team for assistance."


class StyleBot:
    """Main conversational agent"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.llm = LLMInterface()
        self.memory = ConversationBufferMemory(return_messages=True)
        self.context = ConversationContext()
        self.rag_system = rag_system
        self.design_engine = design_engine
        
        # Initialize RAG system
        try:
            self.rag_system.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}")
    
    def chat(self, user_input: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """Main chat interface"""
        try:
            # Update context
            self.context.user_id = user_id
            self.context.interaction_count += 1
            
            # Classify intent
            query_type, confidence = self.intent_classifier.classify_intent(user_input)
            
            # Process based on intent
            if query_type == QueryType.PRODUCT_INQUIRY:
                response = self._handle_product_inquiry(user_input)
            elif query_type == QueryType.FAQ:
                response = self._handle_faq(user_input)
            elif query_type == QueryType.DESIGN_CONSULTATION:
                response = self._handle_design_consultation(user_input)
            elif query_type == QueryType.SHIPPING:
                response = self._handle_shipping_inquiry(user_input)
            elif query_type == QueryType.SUPPORT:
                response = self._handle_support_request(user_input)
            else:
                response = self._handle_general_chat(user_input)
            
            # Update conversation history
            self._update_conversation_history(user_input, response, query_type.value)
            
            # Update memory
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response["message"])
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            return {
                "message": "I apologize, but I'm experiencing some technical difficulties. Please try again or contact our support team.",
                "type": "error",
                "suggestions": []
            }
    
    def _handle_product_inquiry(self, user_input: str) -> Dict[str, Any]:
        """Handle product-related questions"""
        # Get relevant product information
        context = self.rag_system.get_relevant_context(user_input)
        product_results = self.rag_system.search_products(user_input)
        
        # Build prompt
        prompt = PROMPT_TEMPLATES["product_inquiry"].format(
            context=context,
            question=user_input
        )
        
        # Generate response
        response = self.llm.generate_response(prompt)
        
        # Extract product information for suggestions
        product_suggestions = []
        for product in product_results[:3]:  # Top 3 products
            product_suggestions.append({
                "type": "product",
                "title": f"Product: {product['product_id']}",
                "description": product['content'][:200] + "...",
                "action": "view_product"
            })
        
        return {
            "message": response,
            "type": "product_inquiry",
            "suggestions": product_suggestions,
            "context": context
        }
    
    def _handle_faq(self, user_input: str) -> Dict[str, Any]:
        """Handle FAQ questions"""
        # Get FAQ context
        context = self.rag_system.get_relevant_context(user_input)
        faq_response = self.rag_system.get_faq_response(user_input)
        
        if faq_response:
            # Use direct FAQ response
            response = faq_response
        else:
            # Generate response with context
            prompt = PROMPT_TEMPLATES["faq_response"].format(
                context=context,
                question=user_input
            )
            response = self.llm.generate_response(prompt)
        
        return {
            "message": response,
            "type": "faq",
            "suggestions": [
                {
                    "type": "faq",
                    "title": "Need more help?",
                    "description": "Contact our support team for personalized assistance",
                    "action": "contact_support"
                }
            ]
        }
    
    def _handle_design_consultation(self, user_input: str) -> Dict[str, Any]:
        """Handle design consultation requests"""
        # Generate design suggestions
        suggestions = self.design_engine.generate_suggestions(user_input)
        
        # Store suggestions in context
        self.context.last_suggestions = suggestions
        self.context.current_topic = "design"
        
        # Update design preferences
        preferences = self.design_engine.analyze_preferences(user_input)
        self.context.design_preferences.update(preferences)
        
        # Create response message
        response_parts = [
            "I'd love to help you create the perfect design! Based on your preferences, here are some creative suggestions:"
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            response_parts.append(f"\n**Option {i}: {suggestion['title']}**")
            response_parts.append(suggestion['description'])
        
        response_parts.append("\nWhich design catches your eye? I can refine any of these based on your feedback!")
        
        # Format suggestions for UI
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                "type": "design",
                "title": suggestion['title'],
                "description": suggestion['description'],
                "colors": suggestion['colors'],
                "style": suggestion['style'],
                "print_method": suggestion['print_method'],
                "action": "select_design",
                "data": suggestion
            })
        
        return {
            "message": "\n".join(response_parts),
            "type": "design_consultation",
            "suggestions": formatted_suggestions,
            "design_preferences": self.context.design_preferences
        }
    
    def _handle_shipping_inquiry(self, user_input: str) -> Dict[str, Any]:
        """Handle shipping-related questions"""
        context = self.rag_system.get_relevant_context(user_input)
        
        prompt = PROMPT_TEMPLATES["faq_response"].format(
            context=context,
            question=user_input
        )
        
        response = self.llm.generate_response(prompt)
        
        return {
            "message": response,
            "type": "shipping",
            "suggestions": [
                {
                    "type": "shipping",
                    "title": "Track Your Order",
                    "description": "Enter your order number to track your package",
                    "action": "track_order"
                }
            ]
        }
    
    def _handle_support_request(self, user_input: str) -> Dict[str, Any]:
        """Handle support requests"""
        response = """I'm here to help! For immediate assistance, you can:

• **Chat with me** - I can answer questions about products, designs, orders, and policies
• **Email us** - support@customclothingco.com (response within 24 hours)
• **Call us** - 1-800-CUSTOM-1 (9 AM - 6 PM EST)
• **Live chat** - Available on our website during business hours

What specific issue can I help you with today?"""
        
        return {
            "message": response,
            "type": "support",
            "suggestions": [
                {
                    "type": "support",
                    "title": "Contact Support",
                    "description": "Speak with a human representative",
                    "action": "contact_support"
                },
                {
                    "type": "support", 
                    "title": "Order Issues",
                    "description": "Problems with existing orders",
                    "action": "order_support"
                }
            ]
        }
    
    def _handle_general_chat(self, user_input: str) -> Dict[str, Any]:
        """Handle general conversation"""
        # Get conversation history
        history = self._get_conversation_history_string()
        
        # Use general chat prompt
        prompt = PROMPT_TEMPLATES["general_chat"].format(
            history=history,
            input=user_input
        )
        
        response = self.llm.generate_response(prompt)
        
        # Add helpful suggestions
        suggestions = [
            {
                "type": "suggestion",
                "title": "🎨 Design a Custom Item",
                "description": "Let me help you create a unique design",
                "action": "start_design"
            },
            {
                "type": "suggestion",
                "title": "👕 Browse Products",
                "description": "See what we have available",
                "action": "browse_products"
            },
            {
                "type": "suggestion",
                "title": "❓ Get Help",
                "description": "Ask me anything about our service",
                "action": "ask_question"
            }
        ]
        
        return {
            "message": response,
            "type": "general_chat",
            "suggestions": suggestions
        }
    
    def refine_design(self, design_id: str, feedback: str) -> Dict[str, Any]:
        """Refine a design based on user feedback"""
        # Find the design in last suggestions
        original_design = None
        for suggestion in self.context.last_suggestions:
            if suggestion.get("id") == design_id:
                original_design = suggestion
                break
        
        if not original_design:
            return {
                "message": "I couldn't find that design. Let me create some new suggestions for you!",
                "type": "error",
                "suggestions": []
            }
        
        # Refine the design
        refined_design = self.design_engine.refine_suggestion(original_design, feedback)
        
        # Update context
        self.context.last_suggestions = [refined_design]
        
        response = f"Great feedback! I've refined the design based on your input:\n\n**{refined_design['title']}**\n{refined_design['description']}\n\nHow does this look? I can make further adjustments if needed!"
        
        return {
            "message": response,
            "type": "design_refinement",
            "suggestions": [{
                "type": "design",
                "title": refined_design['title'],
                "description": refined_design['description'],
                "colors": refined_design['colors'],
                "style": refined_design['style'],
                "action": "select_design",
                "data": refined_design
            }]
        }
    
    def get_trending_designs(self, garment_type: str = "t-shirt") -> Dict[str, Any]:
        """Get trending design suggestions"""
        trending = self.design_engine.get_trending_suggestions(garment_type)
        
        response = f"Here are some trending {garment_type} designs that are popular right now:"
        
        formatted_suggestions = []
        for design in trending:
            formatted_suggestions.append({
                "type": "design",
                "title": design['title'],
                "description": design['description'],
                "colors": design['colors'],
                "style": design['style'],
                "trending": True,
                "action": "select_design",
                "data": design
            })
        
        return {
            "message": response,
            "type": "trending_designs",
            "suggestions": formatted_suggestions
        }
    
    def _update_conversation_history(self, user_input: str, response: Dict[str, Any], query_type: str):
        """Update conversation history"""
        self.context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response["message"],
            "query_type": query_type,
            "suggestions_count": len(response.get("suggestions", []))
        })
        
        # Keep only last 20 interactions
        if len(self.context.conversation_history) > 20:
            self.context.conversation_history = self.context.conversation_history[-20:]
    
    def _get_conversation_history_string(self) -> str:
        """Get formatted conversation history"""
        if not self.context.conversation_history:
            return "This is the beginning of our conversation."
        
        history_parts = []
        for interaction in self.context.conversation_history[-5:]:  # Last 5 interactions
            history_parts.append(f"User: {interaction['user_input']}")
            history_parts.append(f"StyleBot: {interaction['response']}")
        
        return "\n".join(history_parts)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "interaction_count": self.context.interaction_count,
            "session_duration": str(datetime.now() - self.context.started_at),
            "current_topic": self.context.current_topic,
            "design_preferences": self.context.design_preferences,
            "product_interests": self.context.product_interests
        }


# Singleton instance
stylebot = StyleBot() 