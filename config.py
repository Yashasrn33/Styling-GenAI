import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    """Configuration for AI models and APIs"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000
    
    # Hugging Face Configuration
    hf_model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"
    hf_temperature: float = 0.7
    hf_max_length: int = 1000
    
    # Vector Store Configuration
    vector_store_type: str = "faiss"  # faiss, chroma
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # RAG Configuration
    top_k_results: int = 3
    similarity_threshold: float = 0.7
    
    # Design Generation Configuration
    design_creativity: float = 0.8
    design_max_suggestions: int = 3
    
    def __post_init__(self):
        # Try to get API keys from environment
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")

# Global config instance
config = ModelConfig()

# Prompt Templates
PROMPT_TEMPLATES = {
    "system_prompt": """You are StyleBot, an AI assistant for a custom clothing e-commerce platform. 
You help customers with product inquiries, design suggestions, and general questions about custom clothing.
Be friendly, creative, and helpful. Always maintain context in conversations.
When suggesting designs, be specific about colors, patterns, and styles.""",
    
    "product_inquiry": """Based on the following product information, answer the user's question about product availability, specifications, or details:

Product Information:
{context}

User Question: {question}

Answer:""",
    
    "faq_response": """Based on the following FAQ information, provide a helpful response to the user's question:

FAQ Information:
{context}

User Question: {question}

Answer:""",
    
    "design_consultation": """You are helping a customer design custom clothing. Based on their preferences and the conversation context, suggest creative design ideas.

Customer Preferences: {preferences}
Conversation Context: {context}

Provide 2-3 specific design suggestions with colors, patterns, and style details.""",
    
    "general_chat": """Continue the conversation naturally while staying in character as StyleBot, a helpful AI assistant for custom clothing design.

Conversation History:
{history}

User: {input}

StyleBot:"""
} 