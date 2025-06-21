"""
Retrieval-Augmented Generation (RAG) Module
Handles document loading, embedding, and retrieval for the knowledge base.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader
import markdown

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles loading and processing of knowledge base documents"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_markdown_files(self, directory: str) -> List[Document]:
        """Load and process markdown files"""
        documents = []
        kb_path = Path(directory)
        
        for md_file in kb_path.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert markdown to plain text for better processing
                html = markdown.markdown(content)
                # Simple HTML tag removal
                import re
                text = re.sub('<[^<]+?>', '', html)
                
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": str(md_file),
                        "type": "markdown",
                        "filename": md_file.name
                    }
                )
                documents.append(doc)
                logger.info(f"Loaded markdown file: {md_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading {md_file}: {str(e)}")
        
        return documents
    
    def load_json_files(self, directory: str) -> List[Document]:
        """Load and process JSON files"""
        documents = []
        kb_path = Path(directory)
        
        for json_file in kb_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process different JSON structures
                if json_file.name == "products.json":
                    documents.extend(self._process_products_json(data, str(json_file)))
                else:
                    # Generic JSON processing
                    content = json.dumps(data, indent=2)
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(json_file),
                            "type": "json",
                            "filename": json_file.name
                        }
                    )
                    documents.append(doc)
                
                logger.info(f"Loaded JSON file: {json_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
        
        return documents
    
    def _process_products_json(self, data: Dict, source: str) -> List[Document]:
        """Process products.json into individual product documents"""
        documents = []
        
        if "products" in data:
            for product in data["products"]:
                # Create a readable product description
                content = f"""
Product: {product.get('name', 'Unknown')}
ID: {product.get('id', 'N/A')}
Category: {product.get('category', 'N/A')}
Price: ${product.get('base_price', 'N/A')}
Description: {product.get('description', 'N/A')}
Sizes Available: {', '.join(product.get('sizes', []))}
Colors Available: {', '.join(product.get('colors', []))}
Materials: {', '.join(product.get('materials', []))}
Features: {', '.join(product.get('features', []))}
Customization Options: {', '.join(product.get('customization_options', []))}
Stock Status: {product.get('stock_status', 'N/A')}
Lead Time: {product.get('lead_time', 'N/A')}
                """.strip()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": source,
                        "type": "product",
                        "product_id": product.get('id'),
                        "category": product.get('category'),
                        "price": product.get('base_price')
                    }
                )
                documents.append(doc)
        
        # Process customization info
        if "customization_info" in data:
            custom_info = data["customization_info"]
            content = f"""
Customization Information:
Accepted Design Formats: {', '.join(custom_info.get('design_formats', []))}
Minimum Resolution: {custom_info.get('minimum_resolution', 'N/A')}
Maximum Colors: {custom_info.get('maximum_colors', 'N/A')}
Design Areas: {json.dumps(custom_info.get('design_areas', {}), indent=2)}
Rush Order Available: {custom_info.get('rush_order', {}).get('available', 'N/A')}
Rush Order Cost: ${custom_info.get('rush_order', {}).get('additional_cost', 'N/A')}
Rush Order Lead Time: {custom_info.get('rush_order', {}).get('lead_time', 'N/A')}
            """.strip()
            
            doc = Document(
                page_content=content,
                metadata={
                    "source": source,
                    "type": "customization_info"
                }
            )
            documents.append(doc)
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        return self.text_splitter.split_documents(documents)


class VectorStore:
    """Handles vector embeddings and similarity search"""
    
    def __init__(self):
        self.embeddings_model = SentenceTransformer(config.embedding_model)
        self.index = None
        self.documents = []
        self.embeddings = None
    
    def build_index(self, documents: List[Document]) -> None:
        """Build FAISS index from documents"""
        logger.info("Building vector index...")
        
        self.documents = documents
        texts = [doc.page_content for doc in documents]
        
        # Generate embeddings
        self.embeddings = self.embeddings_model.encode(texts)
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        logger.info(f"Built index with {len(documents)} documents")
    
    def similarity_search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index is None:
            logger.error("Index not built. Call build_index first.")
            return []
        
        k = k or config.top_k_results
        
        # Encode query
        query_embedding = self.embeddings_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score >= config.similarity_threshold:
                results.append({
                    "document": self.documents[idx],
                    "score": float(score),
                    "rank": i + 1
                })
        
        return results
    
    def save_index(self, path: str) -> None:
        """Save the FAISS index and documents"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, f"{path}.index")
        
        # Save documents and embeddings
        import pickle
        with open(f"{path}.docs", 'wb') as f:
            pickle.dump(self.documents, f)
        
        np.save(f"{path}.embeddings", self.embeddings)
        logger.info(f"Saved index to {path}")
    
    def load_index(self, path: str) -> bool:
        """Load a pre-built FAISS index"""
        try:
            self.index = faiss.read_index(f"{path}.index")
            
            import pickle
            with open(f"{path}.docs", 'rb') as f:
                self.documents = pickle.load(f)
            
            self.embeddings = np.load(f"{path}.embeddings.npy")
            logger.info(f"Loaded index from {path}")
            return True
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False


class RAGSystem:
    """Main RAG system that combines document processing and retrieval"""
    
    def __init__(self, knowledge_base_path: str = "app/knowledge_base"):
        self.kb_path = knowledge_base_path
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.is_initialized = False
    
    def initialize(self, force_rebuild: bool = False) -> None:
        """Initialize the RAG system"""
        index_path = "data/vector_index"
        
        # Try to load existing index
        if not force_rebuild and self.vector_store.load_index(index_path):
            self.is_initialized = True
            logger.info("RAG system initialized with existing index")
            return
        
        # Build new index
        logger.info("Building new RAG index...")
        
        # Load all documents
        all_docs = []
        
        # Load markdown files
        md_docs = self.doc_processor.load_markdown_files(self.kb_path)
        all_docs.extend(md_docs)
        
        # Load JSON files
        json_docs = self.doc_processor.load_json_files(self.kb_path)
        all_docs.extend(json_docs)
        
        # Split into chunks
        chunked_docs = self.doc_processor.split_documents(all_docs)
        
        # Build vector index
        self.vector_store.build_index(chunked_docs)
        
        # Save index
        self.vector_store.save_index(index_path)
        
        self.is_initialized = True
        logger.info("RAG system initialization complete")
    
    def get_relevant_context(self, query: str, max_context_length: int = 2000) -> str:
        """Retrieve relevant context for a query"""
        if not self.is_initialized:
            self.initialize()
        
        results = self.vector_store.similarity_search(query)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Combine relevant documents
        context_parts = []
        total_length = 0
        
        for result in results:
            doc = result["document"]
            content = doc.page_content
            score = result["score"]
            
            # Add metadata for context
            source_info = f"[Source: {doc.metadata.get('filename', 'unknown')}]"
            content_with_source = f"{source_info}\n{content}\n"
            
            if total_length + len(content_with_source) > max_context_length:
                break
            
            context_parts.append(content_with_source)
            total_length += len(content_with_source)
        
        return "\n---\n".join(context_parts)
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search specifically for products"""
        if not self.is_initialized:
            self.initialize()
        
        results = self.vector_store.similarity_search(query)
        
        # Filter for product documents
        product_results = []
        for result in results:
            if result["document"].metadata.get("type") == "product":
                product_results.append({
                    "product_id": result["document"].metadata.get("product_id"),
                    "content": result["document"].page_content,
                    "score": result["score"]
                })
        
        return product_results
    
    def get_faq_response(self, query: str) -> Optional[str]:
        """Get response from FAQ documents"""
        if not self.is_initialized:
            self.initialize()
        
        results = self.vector_store.similarity_search(query)
        
        # Look for FAQ content
        for result in results:
            doc = result["document"]
            if "faq" in doc.metadata.get("filename", "").lower():
                return doc.page_content
        
        return None


# Singleton instance
rag_system = RAGSystem() 