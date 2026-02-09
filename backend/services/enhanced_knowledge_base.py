# """
# Enhanced knowledge base module - Advanced RAG
# Supports metadata filtering, hybrid search, reranking, and other advanced strategies
# """
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_core.documents import Document

# # LangChain retrievers - use langchain_classic for EnsembleRetriever
# from langchain_classic.retrievers import EnsembleRetriever

# from langchain_community.retrievers import BM25Retriever
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from config import get_settings
# import logging
# from typing import List, Optional, Dict
# import json

# logger = logging.getLogger(__name__)
# settings = get_settings()

# class EnhancedKnowledgeBase:
#     """Enhanced RAG Knowledge Base
    
#     Features:
#     - Metadata filtering: Precision retrieval by product (M400/M30/Dock3)
#     - Hybrid retrieval: BM25 (keyword) + Vector (semantic)
#     - Reranking: Cross-Encoder to improve accuracy
#     - Parent-child documents: Full context to avoid fragmentation
#     """
    
#     def __init__(self):
#         # Embedding model (supporting multiple languages)
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
#             model_kwargs={'device': 'cpu'}
#         )
        
#         # Chroma vector store
#         self.vectorstore = Chroma(
#             persist_directory=settings.chroma_persist_dir,
#             embedding_function=self.embeddings,
#             collection_name="dji_products_enhanced"
#         )
        
#         # BM25 retriever (exact keyword matching)
#         self.bm25_retriever = None
#         self._init_bm25()
        
#         # Reranking model (optional, requires sentence-transformers)
#         self.reranker = None
#         self._init_reranker()
        
#         # Product tag mapping
#         self.product_tags = {
#             "M400": {
#                 "keywords": ["m400", "matrice 400", "matrice400"],
#                 "tag_image": "1.png"  # corresponds to RoSP/1.png
#             },
#             "M30": {
#                 "keywords": ["m30", "matrice 30", "matrice30"],
#                 "tag_image": "11.png"  # corresponds to RoSP/11.png
#             },
#             "Dock3": {
#                 "keywords": ["dock 3", "dock3", "m4d", "airport"],
#                 "tag_image": "111.png"  # corresponds to RoSP/111.png
#             },
#             "RTK": {
#                 "keywords": ["rtk", "d-rtk", "d-rtk 2", "d-rtk 3"],
#                 "tag_image": None
#             }
#         }
        
#         logger.info(f"Enhanced knowledge base initialization complete: {settings.chroma_persist_dir}")
    
#     def _init_bm25(self):
#         """Initialize BM25 retriever"""
#         try:
#             # Get all documents from vector store for BM25 indexing
#             # Note: This may need optimization for large document counts
#             all_docs = self._get_all_documents()
#             if all_docs:
#                 self.bm25_retriever = BM25Retriever.from_documents(all_docs)
#                 self.bm25_retriever.k = 10  # BM25返回top 10
#                 logger.info(f"BM25 retriever initialization complete, document count: {len(all_docs)}")
#             else:
#                 logger.warning("BM25 retriever initialization failed: No documents")
#         except Exception as e:
#             logger.error(f"BM25 initialization failed: {e}")
    
#     def _init_reranker(self):
#         """Initialize reranking model"""
#         try:
#             from sentence_transformers import CrossEncoder
#             # Use BGE reranking model (supports multiple languages)
#             self.reranker = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=512)
#             logger.info("Reranking model loaded successfully")
#         except ImportError:
#             logger.warning("sentence-transformers not installed, reranking disabled")
#         except Exception as e:
#             logger.warning(f"Reranking model load failed: {e}. Falling back to standard search.")
    
#     def _get_all_documents(self) -> List[Document]:
#         """Get all documents (for BM25 indexing)"""
#         try:
#             # Use Chroma collection.get() to retrieve all documents
#             results = self.vectorstore._collection.get(include=['documents', 'metadatas'])
#             docs = []
#             for i, doc_text in enumerate(results['documents']):
#                 metadata = results['metadatas'][i] if 'metadatas' in results else {}
#                 docs.append(Document(page_content=doc_text, metadata=metadata))
#             return docs
#         except Exception as e:
#             logger.error(f"Failed to retrieve documents: {e}")
#             return []
    
#     def detect_product(self, query: str) -> Optional[str]:
#         """Smart product type detection in query
        
#         Args:
#             query: User query
            
#         Returns:
#             Product tag (M400/M30/Dock3/RTK) or None
#         """
#         query_lower = query.lower()
        
#         for product, info in self.product_tags.items():
#             if any(kw in query_lower for kw in info['keywords']):
#                 logger.info(f"Detected product: {product}")
#                 return product
        
#         return None
    
#     def search(
#         self, 
#         query: str, 
#         product_filter: Optional[str] = None,
#         top_k: int = 5,
#         use_hybrid: bool = True,
#         use_rerank: bool = True,
#         similarity_threshold: float = 0.3
#     ) -> List[Document]:
#         """Enhanced search functionality
        
#         Args:
#             query: Query text
#             product_filter: Product filter (M400/M30/Dock3/RTK)
#             top_k: Document count to return
#             use_hybrid: Whether to use hybrid search (BM25+Vector)
#             use_rerank: Whether to use reranking
#             similarity_threshold: Similarity score threshold
            
#         Returns:
#             List of relevant documents
#         """
#         try:
#             # Auto-detect product if not specified
#             if not product_filter:
#                 product_filter = self.detect_product(query)
            
#             # Build filtering criteria
#             filter_dict = None
#             if product_filter:
#                 filter_dict = {"product_tag": product_filter}
#                 logger.info(f"Applying product filter: {product_filter}")
            
#             # Strategy 1: Hybrid Search (BM25 + Vector)
#             if use_hybrid and self.bm25_retriever:
#                 docs = self._hybrid_search(query, filter_dict, top_k * 2)
#             else:
#                 # Fallback: Vector search only
#                 docs = self._vector_search(query, filter_dict, top_k * 2)
            
#             # Strategy 2: Reranking
#             if use_rerank and self.reranker and docs:
#                 docs = self._rerank_documents(query, docs, top_k)
#             else:
#                 docs = docs[:top_k]
            
#             # Filter out documents with low relevance
#             docs = self._filter_by_similarity(docs, similarity_threshold)
            
#             logger.info(f"Finally returned {len(docs)} documents")
#             return docs
            
#         except Exception as e:
#             logger.error(f"Search failed: {e}")
#             # Final Fallback
#             return self._vector_search(query, filter_dict, min(3, top_k))
    
#     def _vector_search(
#         self, 
#         query: str, 
#         filter_dict: Optional[Dict], 
#         k: int
#     ) -> List[Document]:
#         """Vector search only"""
#         try:
#             docs_and_scores = self.vectorstore.similarity_search_with_score(
#                 query,
#                 k=k,
#                 filter=filter_dict
#             )
#             return [doc for doc, score in docs_and_scores]
#         except Exception as e:
#             logger.error(f"Vector search failed: {e}")
#             return []
    
#     def _hybrid_search(
#         self, 
#         query: str, 
#         filter_dict: Optional[Dict], 
#         k: int
#     ) -> List[Document]:
#         """Hybrid Search (BM25 + Vector)
        
#         Weight: BM25 (0.4) + Vector (0.6)
#         """
#         try:
#             # Vector Search
#             vector_docs = self._vector_search(query, filter_dict, k)
            
#             # BM25 Search
#             bm25_docs = self.bm25_retriever.get_relevant_documents(query)
            
#             # Filter BM25 results if filter exists
#             if filter_dict:
#                 bm25_docs = [
#                     doc for doc in bm25_docs
#                     if doc.metadata.get('product_tag') == filter_dict.get('product_tag')
#                 ]
            
#             # Create ensemble retriever
#             ensemble = EnsembleRetriever(
#                 retrievers=[self.bm25_retriever, self.vectorstore.as_retriever()],
#                 weights=[0.4, 0.6]  # BM25(40%) + Vector(60%)
#             )
            
#             # Merge and deduplicate
#             seen_content = set()
#             merged_docs = []
            
#             # Add vector search results first (higher weight)
#             for doc in vector_docs:
#                 content_hash = hash(doc.page_content[:100])
#                 if content_hash not in seen_content:
#                     seen_content.add(content_hash)
#                     merged_docs.append(doc)
            
#             # Add BM25 results
#             for doc in bm25_docs[:k//2]:  # BM25 contributes half
#                 content_hash = hash(doc.page_content[:100])
#                 if content_hash not in seen_content:
#                     seen_content.add(content_hash)
#                     merged_docs.append(doc)
            
#             logger.info(f"Hybrid Search: Vector({len(vector_docs)}) + BM25({len(bm25_docs)}) -> Merged({len(merged_docs)})")
#             return merged_docs[:k]
            
#         except Exception as e:
#             logger.error(f"Hybrid search failed: {e}. Falling back to vector search.")
#             return self._vector_search(query, filter_dict, k)
    
#     def _rerank_documents(
#         self, 
#         query: str, 
#         docs: List[Document], 
#         top_k: int
#     ) -> List[Document]:
#         """Rerank documents using Cross-Encoder"""
#         if not docs or not self.reranker:
#             return docs
        
#         try:
#             # Build query-document pairs
#             pairs = [[query, doc.page_content] for doc in docs]
            
#             # Calculate relevance scores
#             scores = self.reranker.predict(pairs)
            
#             # Sort by scores
#             doc_scores = list(zip(docs, scores))
#             doc_scores.sort(key=lambda x: x[1], reverse=True)
            
#             # 返回Top K
#             reranked_docs = [doc for doc, score in doc_scores[:top_k]]
            
#             logger.info(f"Reranking: {len(docs)} -> {len(reranked_docs)} (Score range: {min(scores):.3f} - {max(scores):.3f})")
#             return reranked_docs
            
#         except Exception as e:
#             logger.error(f"Reranking failed: {e}")
#             return docs[:top_k]
    
#     def _filter_by_similarity(
#         self, 
#         docs: List[Document], 
#         threshold: float
#     ) -> List[Document]:
#         """Filter out low-relevance documents"""
#         # Only filter if document has score attribute, otherwise return all
#         if not docs:
#             return []
        
#         # Simple strategy: Return at least top 2
#         if len(docs) <= 2:
#             return docs
        
#         return docs  # Reranked results are already sorted by relevance
    
#     def add_documents(
#         self, 
#         documents: List[Document], 
#         auto_tag: bool = True
#     ):
#         """Add documents to knowledge base
        
#         Args:
#             documents: List of documents
#             auto_tag: Whether to automatically add product tags
#         """
#         try:
#             if auto_tag:
#                 documents = self._auto_tag_documents(documents)
            
#             self.vectorstore.add_documents(documents)
#             logger.info(f"Successfully added {len(documents)} documents")
            
#             # Rebuild BM25 index
#             if self.bm25_retriever:
#                 self._init_bm25()
                
#         except Exception as e:
#             logger.error(f"Failed to add documents: {e}")
    
#     def _auto_tag_documents(self, documents: List[Document]) -> List[Document]:
#         """Automatically add product tags to documents"""
#         for doc in documents:
#             # Skip if tag already exists
#             if 'product_tag' in doc.metadata:
#                 continue
            
#             # Detect product from filename or content
#             source = doc.metadata.get('source', '')
#             content = doc.page_content[:500]  # Check first 500 characters
            
#             combined = (source + ' ' + content).lower()
            
#             for product, info in self.product_tags.items():
#                 if any(kw in combined for kw in info['keywords']):
#                     doc.metadata['product_tag'] = product
#                     doc.metadata['tag_image'] = info['tag_image']
#                     logger.debug(f"Automatically tagged document as {product}")
#                     break
        
#         return documents

# # Global Singleton
# _enhanced_kb = None

# def get_enhanced_knowledge_base() -> EnhancedKnowledgeBase:
#     """Get enhanced knowledge base instance (singleton)"""
#     global _enhanced_kb
#     if _enhanced_kb is None:
#         _enhanced_kb = EnhancedKnowledgeBase()
#     return _enhanced_kb
