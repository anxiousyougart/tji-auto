#!/usr/bin/env python3
"""
Debug script to analyze LinkedIn page structure and identify all job cards
"""

import requests
from bs4 import BeautifulSoup
import json

# Request configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def analyze_linkedin_structure():
    """Analyze the LinkedIn page structure to identify all job cards"""
    
    search_url = "https://www.linkedin.com/jobs/search/?currentJobId=4234905066&distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=computer%20science&origin=JOB_SEARCH_PAGE_JOB_FILTER"
    
    print("Fetching LinkedIn page...")
    response = requests.get(search_url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"Page fetched successfully. Content length: {len(response.content)}")
    
    # Save the raw HTML for inspection
    with open('linkedin_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Raw HTML saved to linkedin_page.html")
    
    # Look for all elements that might contain job information
    print("\n=== ANALYZING PAGE STRUCTURE ===")
    
    # Check for data-job-id attributes specifically
    job_id_elements = soup.find_all(attrs={"data-job-id": True})
    print(f"\nElements with data-job-id: {len(job_id_elements)}")
    for i, elem in enumerate(job_id_elements[:5]):
        print(f"  {i+1}. Tag: {elem.name}, data-job-id: {elem.get('data-job-id')}, classes: {elem.get('class', [])}")
    
    # Check for job-card-container attributes
    job_card_containers = soup.find_all(attrs={"job-card-container": True})
    print(f"\nElements with job-card-container: {len(job_card_containers)}")
    for i, elem in enumerate(job_card_containers[:5]):
        print(f"  {i+1}. Tag: {elem.name}, classes: {elem.get('class', [])}")
    
    # Check for various job-related selectors
    selectors_to_test = [
        'div[data-entity-urn*="job"]',
        'div[data-job-id]',
        'div.base-card',
        'li.result-card',
        'div.job-search-card',
        'div.base-search-card',
        'article[data-entity-urn]',
        'div.jobs-search-results__list-item',
        'li[data-occludable-job-id]',
        'div[data-test-id*="job"]',
        'div.job-result-card',
        'article',
        'li[data-entity-urn]',
        'div[class*="job"]',
        'li[class*="job"]',
        '[data-job-id]',
        '[job-card-container]',
        '.job-card',
        '.job-listing',
        '.job-item'
    ]
    
    print(f"\n=== TESTING SELECTORS ===")
    all_found_elements = []
    
    for selector in selectors_to_test:
        try:
            elements = soup.select(selector)
            print(f"{selector}: {len(elements)} elements")
            
            if elements:
                # Store first few elements for analysis
                for i, elem in enumerate(elements[:3]):
                    element_info = {
                        'selector': selector,
                        'index': i,
                        'tag': elem.name,
                        'classes': elem.get('class', []),
                        'data_attrs': {k: v for k, v in elem.attrs.items() if k.startswith('data-')},
                        'text_snippet': elem.get_text()[:100].strip()
                    }
                    all_found_elements.append(element_info)
                    
        except Exception as e:
            print(f"{selector}: ERROR - {e}")
    
    # Save analysis results
    with open('../data/linkedin_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(all_found_elements, f, ensure_ascii=False, indent=2)
    print(f"../data/\nAnalysis saved to linkedin_analysis.json")
    
    # Look for pagination or load more buttons
    print(f"\n=== PAGINATION/LOAD MORE ANALYSIS ===")
    pagination_selectors = [
        'button[aria-label*="next"]',
        'button[aria-label*="more"]',
        '.pagination',
        '[data-test-id*="pagination"]',
        '[data-test-id*="load"]',
        'button[data-test-id*="load"]',
        '.load-more',
        '.see-more',
        '.show-more'
    ]
    
    for selector in pagination_selectors:
        try:
            elements = soup.select(selector)
            if elements:
                print(f"{selector}: {len(elements)} elements found")
                for elem in elements[:2]:
                    print(f"  Text: '{elem.get_text().strip()}'")
        except Exception as e:
            print(f"{selector}: ERROR - {e}")
    
    # Check for JavaScript-loaded content indicators
    print(f"\n=== DYNAMIC CONTENT INDICATORS ===")
    script_tags = soup.find_all('script')
    print(f"Total script tags: {len(script_tags)}")
    
    # Look for common dynamic loading patterns
    dynamic_indicators = ['react', 'vue', 'angular', 'ajax', 'fetch', 'xhr', 'infinite', 'lazy']
    for script in script_tags:
        if script.string:
            script_text = script.string.lower()
            for indicator in dynamic_indicators:
                if indicator in script_text:
                    print(f"Found '{indicator}' in script tag")
                    break

if __name__ == "__main__":
    analyze_linkedin_structure()
