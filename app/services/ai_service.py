"""
AI service for patent processing using Hugging Face
"""
from typing import List, Dict, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import transformers, but make it optional
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not installed. AI features will be disabled. Install with: pip install transformers")


class AIService:
    """AI service for patent summarization and relevance scoring"""
    
    def __init__(self):
        self.model_name = settings.hf_model_name
        self.summarizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Hugging Face model"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers library not available. AI features disabled.")
            self.summarizer = None
            return
        
        try:
            # Try to import torch, but continue without it if not available
            try:
                import torch
                device = -1  # Use CPU (change to 0 for GPU if available)
            except ImportError:
                logger.info("PyTorch not installed. Using CPU mode with transformers.")
                device = -1
            
            # Use a lightweight model for summarization
            # If torch is not available, transformers will use a fallback
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=device
            )
            logger.info(f"Initialized AI model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize AI model: {e}. Continuing without AI features.")
            logger.warning("Note: Install transformers and torch for AI processing: pip install transformers torch")
            self.summarizer = None
    
    def summarize_abstract(self, abstract: str, max_length: int = 150, min_length: int = 50) -> Optional[str]:
        """
        Summarize patent abstract using Hugging Face model
        
        Args:
            abstract: Patent abstract text
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Summarized text or None if model unavailable
        """
        if not self.summarizer or not abstract:
            return None
        
        try:
            # Truncate if too long (models have token limits)
            max_input_length = 1024
            if len(abstract) > max_input_length:
                abstract = abstract[:max_input_length]
            
            result = self.summarizer(
                abstract,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return result[0].get("summary_text", "") if result else None
            
        except Exception as e:
            logger.error(f"Error summarizing abstract: {e}")
            return None
    
    def calculate_relevance_score(
        self,
        patent: Dict,
        industry_keywords: Optional[List[str]] = None
    ) -> float:
        """
        Calculate relevance score for patent based on industry keywords
        
        Args:
            patent: Patent dictionary
            industry_keywords: List of keywords to match against
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not industry_keywords:
            return 0.5  # Neutral score if no keywords
        
        # Simple keyword matching algorithm
        # In production, use more sophisticated NLP
        text_to_search = " ".join([
            patent.get("title", ""),
            patent.get("abstract", ""),
            patent.get("technology_area", "")
        ]).lower()
        
        keyword_matches = 0
        for keyword in industry_keywords:
            if keyword.lower() in text_to_search:
                keyword_matches += 1
        
        # Calculate score: matches / total keywords, normalized to 0-1
        score = min(keyword_matches / len(industry_keywords), 1.0)
        
        # Boost score if multiple matches
        if keyword_matches > 1:
            score = min(score * 1.2, 1.0)
        
        return round(score, 2)
    
    def classify_technology_area(self, patent: Dict) -> Optional[str]:
        """
        Classify patent into technology area
        
        Args:
            patent: Patent dictionary
            
        Returns:
            Technology area string or None
        """
        # Simple keyword-based classification
        # In production, use trained ML model
        text = " ".join([
            patent.get("title", ""),
            patent.get("abstract", "")
        ]).lower()
        
        technology_areas = {
            "biotechnology": ["biotech", "pharmaceutical", "drug", "medicine", "therapeutic", "protein", "dna", "rna"],
            "electronics": ["electronic", "circuit", "semiconductor", "chip", "processor", "transistor"],
            "software": ["software", "algorithm", "computer", "system", "method", "application", "program"],
            "medical devices": ["medical", "device", "surgical", "diagnostic", "treatment", "implant"],
            "automotive": ["vehicle", "automotive", "engine", "transmission", "brake", "car"],
            "energy": ["energy", "solar", "battery", "fuel", "power", "renewable"],
            "materials": ["material", "polymer", "composite", "alloy", "coating"],
        }
        
        scores = {}
        for area, keywords in technology_areas.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[area] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def process_patents(
        self,
        patents: List[Dict],
        industry_keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Process list of patents with AI features
        
        Args:
            patents: List of patent dictionaries
            industry_keywords: Optional industry keywords for relevance scoring
            
        Returns:
            List of enriched patent dictionaries
        """
        processed = []
        
        for patent in patents:
            # Add AI summary
            abstract = patent.get("abstract", "")
            if abstract:
                summary = self.summarize_abstract(abstract)
                patent["ai_summary"] = summary
            
            # Classify technology area
            technology_area = self.classify_technology_area(patent)
            patent["technology_area"] = technology_area
            
            # Calculate relevance score
            relevance_score = self.calculate_relevance_score(patent, industry_keywords)
            patent["relevance_score"] = relevance_score
            
            processed.append(patent)
        
        # Sort by relevance score (highest first)
        processed.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        
        return processed

