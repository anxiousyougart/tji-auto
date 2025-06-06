#!/usr/bin/env python3
"""
Fallback Selection System

This module provides fallback selection methods when AI (Groq API) is not available.
Uses rule-based algorithms to select the best content from scraped results.

Author: Augment Agent
Date: 2025-01-25
"""

import json
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import re

def score_tech_article(article: Dict) -> float:
    """
    Score a tech news article based on title keywords and relevance.
    
    Args:
        article: Dictionary containing article data
        
    Returns:
        Score between 0-100 (higher is better)
    """
    title = article.get('title', '').lower()
    score = 0.0
    
    # High-value keywords (10 points each)
    high_value_keywords = [
        'breakthrough', 'innovation', 'new', 'launch', 'release',
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        'quantum', 'blockchain', 'cryptocurrency', 'cybersecurity'
    ]
    
    # Medium-value keywords (5 points each)
    medium_value_keywords = [
        'software', 'developer', 'programming', 'coding', 'tech',
        'startup', 'technology', 'algorithm', 'data science',
        'cloud', 'mobile', 'web', 'api', 'framework'
    ]
    
    # Low-value keywords (2 points each)
    low_value_keywords = [
        'update', 'feature', 'tool', 'platform', 'service',
        'app', 'website', 'system', 'network', 'database'
    ]
    
    # Negative keywords (-10 points each)
    negative_keywords = [
        'opinion', 'editorial', 'blog', 'personal', 'drama',
        'controversy', 'gossip', 'rumor', 'politics', 'lawsuit'
    ]
    
    # Score based on keywords
    for keyword in high_value_keywords:
        if keyword in title:
            score += 10
    
    for keyword in medium_value_keywords:
        if keyword in title:
            score += 5
    
    for keyword in low_value_keywords:
        if keyword in title:
            score += 2
    
    for keyword in negative_keywords:
        if keyword in title:
            score -= 10
    
    # Bonus for recent articles (if date available)
    if 'date' in article:
        try:
            article_date = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
            hours_old = (datetime.now() - article_date).total_seconds() / 3600
            if hours_old < 24:
                score += 5  # Recent bonus
        except:
            pass
    
    # Bonus for title length (not too short, not too long)
    title_length = len(title)
    if 30 <= title_length <= 100:
        score += 3
    
    return max(0, score)

def score_internship(internship: Dict) -> float:
    """
    Score an internship based on relevance for CS/IT students.
    
    Args:
        internship: Dictionary containing internship data
        
    Returns:
        Score between 0-100 (higher is better)
    """
    title = internship.get('title', '').lower()
    company = internship.get('company', '').lower()
    description = internship.get('description', '').lower()
    
    score = 0.0
    
    # High-value keywords for CS/IT (15 points each)
    cs_keywords = [
        'software', 'developer', 'programming', 'coding', 'computer science',
        'it', 'technology', 'tech', 'web development', 'mobile development',
        'data science', 'machine learning', 'ai', 'artificial intelligence'
    ]
    
    # Medium-value keywords (10 points each)
    tech_keywords = [
        'engineer', 'analyst', 'technical', 'digital', 'automation',
        'cloud', 'database', 'api', 'frontend', 'backend', 'fullstack'
    ]
    
    # Company reputation bonus (if known tech companies)
    tech_companies = [
        'google', 'microsoft', 'amazon', 'apple', 'facebook', 'meta',
        'netflix', 'uber', 'airbnb', 'spotify', 'adobe', 'salesforce',
        'oracle', 'ibm', 'intel', 'nvidia', 'tesla', 'twitter'
    ]
    
    # Score based on title keywords
    for keyword in cs_keywords:
        if keyword in title:
            score += 15
    
    for keyword in tech_keywords:
        if keyword in title:
            score += 10
    
    # Score based on company
    for company_name in tech_companies:
        if company_name in company:
            score += 20
    
    # Bonus for description keywords
    for keyword in cs_keywords:
        if keyword in description:
            score += 5
    
    # Penalty for suspicious patterns
    suspicious_patterns = [
        'work from home', 'earn money', 'no experience required',
        'easy money', 'part time', 'flexible hours', 'commission based'
    ]
    
    for pattern in suspicious_patterns:
        if pattern in title or pattern in description:
            score -= 15
    
    return max(0, score)

def score_job(job: Dict) -> float:
    """
    Score a job based on relevance for fresh engineering graduates.
    
    Args:
        job: Dictionary containing job data
        
    Returns:
        Score between 0-100 (higher is better)
    """
    title = job.get('title', '').lower()
    company = job.get('company', '').lower()
    description = job.get('description', '').lower()
    
    score = 0.0
    
    # High-value job titles (20 points each)
    entry_level_titles = [
        'junior', 'associate', 'entry level', 'graduate', 'fresher',
        'software engineer', 'developer', 'analyst', 'specialist'
    ]
    
    # Medium-value keywords (10 points each)
    tech_keywords = [
        'software', 'programming', 'coding', 'development', 'technical',
        'it', 'computer science', 'technology', 'engineer'
    ]
    
    # Experience level bonus
    experience_patterns = [
        '0-1 year', '0-2 year', 'fresher', 'entry level', 'graduate',
        'no experience', 'fresh graduate'
    ]
    
    # Score based on title
    for title_keyword in entry_level_titles:
        if title_keyword in title:
            score += 20
    
    for keyword in tech_keywords:
        if keyword in title:
            score += 10
    
    # Experience level scoring
    for pattern in experience_patterns:
        if pattern in title or pattern in description:
            score += 15
    
    # Penalty for senior positions
    senior_keywords = [
        'senior', 'lead', 'principal', 'manager', 'director',
        'head of', 'chief', 'vp', 'vice president', '5+ years',
        '3+ years', 'experienced'
    ]
    
    for keyword in senior_keywords:
        if keyword in title:
            score -= 25
    
    return max(0, score)

def score_upskill_article(article: Dict) -> float:
    """
    Score an upskill article based on learning value for CS students.
    
    Args:
        article: Dictionary containing article data
        
    Returns:
        Score between 0-100 (higher is better)
    """
    title = article.get('title', '').lower()
    score = 0.0
    
    # High-value learning keywords (15 points each)
    learning_keywords = [
        'tutorial', 'guide', 'how to', 'learn', 'beginner',
        'step by step', 'complete guide', 'introduction to',
        'getting started', 'best practices'
    ]
    
    # Technology keywords (10 points each)
    tech_keywords = [
        'python', 'javascript', 'react', 'node.js', 'java', 'c++',
        'machine learning', 'data science', 'web development',
        'mobile development', 'cloud computing', 'docker', 'kubernetes'
    ]
    
    # Project keywords (12 points each)
    project_keywords = [
        'project', 'build', 'create', 'implement', 'develop',
        'portfolio', 'hands-on', 'practical', 'example'
    ]
    
    # Score based on keywords
    for keyword in learning_keywords:
        if keyword in title:
            score += 15
    
    for keyword in tech_keywords:
        if keyword in title:
            score += 10
    
    for keyword in project_keywords:
        if keyword in title:
            score += 12
    
    # Bonus for title structure
    if any(word in title for word in ['how', 'what', 'why', 'when', 'where']):
        score += 5
    
    return max(0, score)

def fallback_select_best(items: List[Dict], item_type: str) -> Optional[Dict]:
    """
    Select the best item using fallback scoring algorithms.
    
    Args:
        items: List of items to choose from
        item_type: Type of items ('tech_news', 'internship', 'job', 'upskill')
        
    Returns:
        Best item or None if no items provided
    """
    if not items:
        return None
    
    # Score all items
    scored_items = []
    
    for item in items:
        if item_type == 'tech_news':
            score = score_tech_article(item)
        elif item_type == 'internship':
            score = score_internship(item)
        elif item_type == 'job':
            score = score_job(item)
        elif item_type == 'upskill':
            score = score_upskill_article(item)
        else:
            score = 0
        
        scored_items.append((score, item))
    
    # Sort by score (highest first)
    scored_items.sort(key=lambda x: x[0], reverse=True)
    
    # Log the selection
    best_score, best_item = scored_items[0]
    logging.info(f"Fallback selection for {item_type}: score={best_score:.1f}, title='{best_item.get('title', 'N/A')}'")
    
    return best_item

def create_fallback_selection_result(item: Dict, item_type: str, total_items: int) -> Dict:
    """
    Create a standardized result format for fallback selections.
    
    Args:
        item: Selected item
        item_type: Type of item
        total_items: Total number of items analyzed
        
    Returns:
        Standardized result dictionary
    """
    return {
        "title": item.get('title', 'Unknown'),
        "url": item.get('url', ''),
        "company": item.get('company', '') if 'company' in item else None,
        "selection_method": "fallback_algorithm",
        "selection_reasoning": f"Selected using rule-based scoring algorithm from {total_items} {item_type} items",
        "ai_selection": False,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the scoring functions
    print("🧪 TESTING FALLBACK SELECTION ALGORITHMS")
    print("-" * 50)
    
    # Test tech news scoring
    test_articles = [
        {"title": "New AI Breakthrough in Machine Learning", "url": "test1.com"},
        {"title": "Opinion: Why I Think Tech is Bad", "url": "test2.com"},
        {"title": "Google Releases New Developer Framework", "url": "test3.com"}
    ]
    
    print("📰 Tech News Scoring:")
    for article in test_articles:
        score = score_tech_article(article)
        print(f"  {score:5.1f} - {article['title']}")
    
    best = fallback_select_best(test_articles, 'tech_news')
    print(f"  🏆 Best: {best['title']}")
    print()
