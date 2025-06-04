import os
import json
import asyncio
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import re

# For document processing
try:
    import PyPDF2
    import fitz  # PyMuPDF - better for text extraction
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF processing libraries not available. Install PyPDF2 and PyMuPDF.")

# For embeddings and vector search
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logging.warning("Embedding libraries not available. Install sentence-transformers and faiss-cpu.")

# For cloud processing with Modal
try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    logging.warning("Modal not available for cloud processing.")

class EUAIActProcessor:
    def __init__(self, document_path: Optional[str] = None):
        self.document_path = document_path or "eu_ai_act.pdf"
        self.chunks = []
        self.embeddings = None
        self.index = None
        self.embedding_model = None
        self.articles_metadata = {}
        self.is_initialized = False
        
        # Configuration
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.embedding_model_name = "all-MiniLM-L6-v2"  # Lightweight but effective
        
    async def initialize(self):
        """Initialize the document processor"""
        if self.is_initialized:
            return
            
        try:
            # Load embedding model
            if EMBEDDING_AVAILABLE:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logging.info(f"Loaded embedding model: {self.embedding_model_name}")
            else:
                raise ValueError("Embedding libraries not available. Please install sentence-transformers and faiss-cpu.")
            
            # Check if processed data exists
            if self._load_processed_data():
                logging.info("Loaded existing processed data")
                self.is_initialized = True
                return
            
            # Require the actual document
            if not os.path.exists(self.document_path):
                raise ValueError(f"EU AI Act PDF not found at {self.document_path}. Please provide the original 170-page document.")
            
            # Process the document
            await self._process_document()
                
            self.is_initialized = True
            logging.info("Document processor initialized successfully with original EU AI Act document")
            
        except Exception as e:
            logging.error(f"Failed to initialize document processor: {str(e)}")
            raise ValueError(f"Cannot initialize without original EU AI Act document: {str(e)}")
    
    def _load_processed_data(self) -> bool:
        """Load previously processed data if available"""
        try:
            if (os.path.exists("processed_chunks.json") and 
                os.path.exists("embeddings.npy") and 
                os.path.exists("articles_metadata.json")):
                
                with open("processed_chunks.json", "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                
                with open("articles_metadata.json", "r", encoding="utf-8") as f:
                    self.articles_metadata = json.load(f)
                
                if EMBEDDING_AVAILABLE:
                    self.embeddings = np.load("embeddings.npy")
                    self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
                    self.index.add(self.embeddings.astype('float32'))
                
                return True
        except Exception as e:
            logging.error(f"Failed to load processed data: {str(e)}")
        
        return False
    
    async def _process_document(self):
        """Process the EU AI Act PDF document"""
        logging.info(f"Processing document: {self.document_path}")
        
        # Extract text from PDF
        text_content = self._extract_text_from_pdf()
        
        # Parse articles and structure
        articles = self._parse_articles(text_content)
        
        # Create chunks
        self.chunks = self._create_chunks(text_content, articles)
        
        # Generate embeddings
        if EMBEDDING_AVAILABLE and self.embedding_model:
            await self._generate_embeddings()
        
        # Save processed data
        self._save_processed_data()
        
        logging.info(f"Processed {len(self.chunks)} chunks from EU AI Act")
    
    def _extract_text_from_pdf(self) -> str:
        """Extract text from PDF using PyMuPDF (better quality)"""
        if not PDF_AVAILABLE:
            raise ValueError("PDF processing libraries not available")
        
        text_content = ""
        
        try:
            # Try PyMuPDF first (better quality)
            doc = fitz.open(self.document_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            doc.close()
            
        except Exception as e:
            logging.error(f"PyMuPDF failed: {str(e)}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                with open(self.document_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
            except Exception as e2:
                logging.error(f"PyPDF2 also failed: {str(e2)}")
                raise ValueError("Failed to extract text from PDF")
        
        return text_content
    
    def _parse_articles(self, text_content: str) -> Dict[str, Dict]:
        """Parse articles from the EU AI Act text"""
        articles = {}
        
        # Common patterns for EU AI Act articles
        article_patterns = [
            r"Article\s+(\d+)\s*[\n\r]+([^\n\r]+)",  # Article number and title
            r"ARTICLE\s+(\d+)\s*[\n\r]+([^\n\r]+)",
        ]
        
        for pattern in article_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                article_num = match.group(1)
                article_title = match.group(2).strip()
                
                # Find the article content (text until next article or section)
                start_pos = match.end()
                next_article_pattern = r"Article\s+\d+"
                next_match = re.search(next_article_pattern, text_content[start_pos:], re.IGNORECASE)
                
                if next_match:
                    end_pos = start_pos + next_match.start()
                    content = text_content[start_pos:end_pos].strip()
                else:
                    # Take next 2000 characters as reasonable article length
                    content = text_content[start_pos:start_pos + 2000].strip()
                
                articles[article_num] = {
                    "title": article_title,
                    "content": content,
                    "number": article_num
                }
        
        self.articles_metadata = articles
        return articles
    
    def _create_chunks(self, text_content: str, articles: Dict) -> List[Dict]:
        """Create chunks from the document text"""
        chunks = []
        
        # Method 1: Article-based chunks
        for article_num, article_data in articles.items():
            chunk = {
                "content": f"Article {article_num}: {article_data['title']}\n\n{article_data['content']}",
                "type": "article",
                "article_number": article_num,
                "title": article_data['title'],
                "metadata": {
                    "source": "EU AI Act",
                    "article_number": article_num,
                    "type": "article"
                }
            }
            chunks.append(chunk)
        
        # Method 2: Sliding window chunks for comprehensive coverage
        words = text_content.split()
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunk = {
                "content": chunk_text,
                "type": "sliding_window",
                "start_word": i,
                "end_word": min(i + self.chunk_size, len(words)),
                "metadata": {
                    "source": "EU AI Act",
                    "type": "sliding_window",
                    "chunk_index": len(chunks)
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    async def _generate_embeddings(self):
        """Generate embeddings for all chunks"""
        if not self.embedding_model:
            return
        
        logging.info("Generating embeddings...")
        
        # Extract text content for embedding
        texts = [chunk["content"] for chunk in self.chunks]
        
        # Generate embeddings in batches
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)
            all_embeddings.append(batch_embeddings)
            
            if i % (batch_size * 10) == 0:
                logging.info(f"Generated embeddings for {i + len(batch_texts)}/{len(texts)} chunks")
        
        # Combine all embeddings
        self.embeddings = np.vstack(all_embeddings)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings.astype('float32'))
        
        logging.info(f"Generated {len(self.embeddings)} embeddings")
    
    def _save_processed_data(self):
        """Save processed data for future use"""
        try:
            with open("processed_chunks.json", "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
            
            with open("articles_metadata.json", "w", encoding="utf-8") as f:
                json.dump(self.articles_metadata, f, ensure_ascii=False, indent=2)
            
            if self.embeddings is not None:
                np.save("embeddings.npy", self.embeddings)
            
            logging.info("Saved processed data")
            
        except Exception as e:
            logging.error(f"Failed to save processed data: {str(e)}")
    
    async def search_relevant_articles(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for articles relevant to the query"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.chunks:
            return []
        
        # If embeddings are available, use semantic search
        if self.embeddings is not None and self.embedding_model and self.index:
            try:
                query_embedding = self.embedding_model.encode([query])
                scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.chunks):
                        chunk = self.chunks[idx].copy()
                        chunk['relevance_score'] = float(score)
                        results.append(chunk)
                
                return results
                
            except Exception as e:
                logging.error(f"Semantic search failed: {str(e)}")
        
        # Fallback to keyword search
        return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_chunks = []
        for chunk in self.chunks:
            content_lower = chunk["content"].lower()
            
            # Simple scoring based on keyword matches
            score = 0
            for word in query_words:
                score += content_lower.count(word)
            
            if score > 0:
                chunk_copy = chunk.copy()
                chunk_copy['relevance_score'] = score / len(query_words)
                scored_chunks.append(chunk_copy)
        
        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_chunks[:top_k]
    
    def get_article_by_number(self, article_number: str) -> Optional[Dict]:
        """Get specific article by number"""
        return self.articles_metadata.get(article_number)
    
    def get_all_articles(self) -> Dict[str, Dict]:
        """Get all parsed articles"""
        return self.articles_metadata 