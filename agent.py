# agent.py
"""
Agent wrapper that uses support_agent.py for FAQ handling.
Provides Agent class interface expected by app.py
"""

import os
import json
from typing import List, Dict, Tuple
from ui_components import ASSISTANT_AVATAR, USER_AVATAR

# Import functions from support_agent
from support_agent import (
    load_faqs as _load_faqs,
    find_similar_faqs,
    generate_response as _generate_response,
    build_index,
    should_escalate
)

# Simple config class for avatars
class Config:
    ASSISTANT_AVATAR = ASSISTANT_AVATAR
    USER_AVATAR = USER_AVATAR

class Agent:
    def __init__(self, faqs_path="data/faqs_large.json", dataset_csv_path="data/dataset.csv"):
        self.config = Config()
        self.faqs_path = faqs_path
        self.dataset_csv_path = dataset_csv_path
        
        # Load FAQs
        self.faqs = _load_faqs(faqs_path)
        
        # Load dataset CSV if exists
        self.rows = []
        if os.path.exists(dataset_csv_path):
            try:
                import csv
                with open(dataset_csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    self.rows = [r for r in reader]
            except Exception as e:
                print(f"Warning: Could not load dataset CSV: {e}")
                self.rows = []
        
        # Build search index
        if self.faqs:
            try:
                build_index(self.faqs)
            except Exception as e:
                print(f"Warning: Could not build search index: {e}")
    
    def load_faqs(self) -> List[Dict]:
        """Return FAQ list"""
        return self.faqs
    
    def build_suggestions(self, limit: int = 10) -> List[str]:
        """
        Build suggestion chips from FAQs.
        Returns list of question strings.
        """
        suggestions = []
        # Get short FAQ questions
        for f in self.faqs:
            q = str(f.get("question", "")).strip()
            if q and len(q.split()) <= 8:  # Keep questions short
                suggestions.append(q)
            if len(suggestions) >= limit:
                break
        
        # If we need more, add some common patterns
        if len(suggestions) < limit:
            common = [
                "How do I reset my password?",
                "What are the working hours?",
                "How do I request leave?",
                "Who do I contact for payroll issues?",
                "How to change bank details?",
                "What is my leave balance?",
                "How do I get reimbursement?",
            ]
            for c in common:
                if c not in suggestions:
                    suggestions.append(c)
                if len(suggestions) >= limit:
                    break
        
        return suggestions[:limit]
    
    def handle_query(self, user_query: str) -> Tuple[str, Dict]:
        """
        Handle user query and return (response, metadata).
        """
        if not user_query or not user_query.strip():
            return "Please ask a question.", {}
        
        # Check if should escalate
        try:
            escalate = should_escalate(user_query)
        except Exception:
            escalate = False
        
        # Generate response using support_agent
        try:
            response = _generate_response(user_query, self.faqs, self.rows)
            if not response or not response.strip():
                response = "I'm sorry, I couldn't find an answer to that question. Please try rephrasing or contact support."
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
            response = "Sorry — I encountered an error. Please try rephrasing your question or contact support."
        
        metadata = {
            "escalate": escalate,
            "faq_count": len(self.faqs) if self.faqs else 0,
            "dataset_count": len(self.rows) if self.rows else 0
        }
        
        return response, metadata

# Convenience functions for backward compatibility
def load_faqs(path: str = "data/faqs_large.json") -> List[Dict]:
    """Return FAQ list"""
    return _load_faqs(path)

def build_suggestions(faqs=None, rows=None, top_n: int = 40, limit: int = None):
    """
    Build suggestions. Accepts both top_n (legacy) and limit (new) parameters.
    """
    if limit is None:
        limit = top_n
    
    if faqs is None:
        faqs = load_faqs()
    
    suggestions = []
    # Include short FAQ questions first
    for f in faqs:
        q = str(f.get("question", "")).strip()
        if q and len(q.split()) <= 6:
            suggestions.append(q)
        if len(suggestions) >= limit:
            break
    
    return suggestions[:limit]
