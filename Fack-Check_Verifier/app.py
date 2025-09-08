from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import time
from random import choice
import sqlite3
import spacy
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# User agents to rotate and avoid blocking
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Load spaCy for keyword refinement
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

def get_headers():
    """Return headers with a random user agent."""
    return {'User-Agent': choice(USER_AGENTS)}

def init_db():
    """Initialize SQLite database for caching results."""
    conn = sqlite3.connect("factcheck_cache.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS results (keyword TEXT, score REAL, message TEXT, status TEXT, timestamp TEXT)")
    c.execute("DELETE FROM results WHERE timestamp < datetime('now', '-7 days')")  # Clear entries older than 7 days
    conn.commit()
    conn.close()

def cache_result(keyword, score, message, status):
    """Cache query results in SQLite, only if score is not default (0.5) from connection failure."""
    if score == 0.5 and "Could not connect" in message:
        return
    conn = sqlite3.connect("factcheck_cache.db")
    c = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)", (keyword, score, message, status, timestamp))
    conn.commit()
    conn.close()

def get_cached_result(keyword):
    """Retrieve cached result if available."""
    conn = sqlite3.connect("factcheck_cache.db")
    c = conn.cursor()
    c.execute("SELECT score, message, status FROM results WHERE keyword = ? ORDER BY timestamp DESC LIMIT 1", (keyword,))
    result = c.fetchone()
    conn.close()
    return result if result else None

def refine_keyword(keyword):
    """Refine keyword using spaCy to extract key entities, or return original if spaCy fails."""
    if not nlp:
        return keyword
    doc = nlp(keyword)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]]
    return " ".join(entities) if entities else keyword

def get_selenium_driver():
    """Initialize headless Selenium Chrome driver with anti-detection."""
    options = Options()
    options.headless = True
    options.add_argument(f"user-agent={choice(USER_AGENTS)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

def get_credibility_from_politifact(keyword):
    """Scrape PolitiFact using Selenium for dynamic content."""
    search_url = f"https://www.politifact.com/search?q={urllib.parse.quote(keyword)}"
    score_map = {
        'true': 1.0, 'mostly true': 0.8, 'half true': 0.5, 'barely true': 0.4,
        'mostly false': 0.3, 'false': 0.1, 'pants on fire': 0.0
    }
    
    driver = get_selenium_driver()
    try:
        driver.get(search_url)
        logging.info(f"Scraping PolitiFact: {search_url}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m-statement__meter"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rating_containers = soup.find_all('div', class_='m-statement__meter')
        
        if not rating_containers:
            return 0.5, "No relevant fact-checks found on PolitiFact.", "info"
        
        first_rating_text = rating_containers[0].find('div', class_='c-label').text.strip().lower()
        matched_score = score_map.get(first_rating_text, 0.5)
        message, status = format_result(first_rating_text, matched_score, "PolitiFact")
        return matched_score, message, status
    
    except Exception as e:
        logging.error(f"PolitiFact scraping failed: {e}")
        return 0.5, "Could not connect to PolitiFact or no results found.", "danger"
    finally:
        driver.quit()

def get_credibility_from_snopes(keyword):
    """Scrape Snopes using Selenium for dynamic content."""
    search_url = f"https://www.snopes.com/?s={urllib.parse.quote(keyword)}"
    score_map = {
        'true': 1.0, 'mostly true': 0.8, 'mixture': 0.5, 'mostly false': 0.3,
        'false': 0.1, 'unproven': 0.4, 'scam': 0.0
    }
    
    driver = get_selenium_driver()
    try:
        driver.get(search_url)
        logging.info(f"Scraping Snopes: {search_url}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        result = soup.find('div', class_='search-result')
        
        if not result:
            return 0.5, "No relevant fact-checks found on Snopes.", "info"
        
        rating_span = result.find('span', class_='rating-label')
        if not rating_span:
            return 0.5, "No clear rating found on Snopes.", "info"
        
        first_rating_text = rating_span.text.strip().lower()
        matched_score = score_map.get(first_rating_text, 0.5)
        message, status = format_result(first_rating_text, matched_score, "Snopes")
        return matched_score, message, status
    
    except Exception as e:
        logging.error(f"Snopes scraping failed: {e}")
        return 0.5, "Could not connect to Snopes or no results found.", "danger"
    finally:
        driver.quit()

def get_credibility_from_factcheck_org(keyword):
    """Scrape FactCheck.org using requests with retries."""
    search_url = f"https://www.factcheck.org/?s={urllib.parse.quote(keyword)}"
    score_map = {
        'no evidence': 0.1, 'false': 0.1, 'misleading': 0.3, 'partially true': 0.5,
        'accurate': 1.0, 'correct': 1.0
    }
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(search_url, headers=get_headers(), timeout=20)
        logging.info(f"Scraping FactCheck.org: {search_url}, Status: {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('article', class_='post')
        
        if not result:
            return 0.5, "No relevant fact-checks found on FactCheck.org.", "info"
        
        content = result.get_text().lower()
        for key in score_map:
            if key in content:
                matched_score = score_map[key]
                message, status = format_result(key, matched_score, "FactCheck.org")
                return matched_score, message, status
        
        return 0.5, "No clear rating found on FactCheck.org.", "info"
    
    except requests.exceptions.RequestException as e:
        logging.error(f"FactCheck.org scraping failed: {e}")
        return 0.5, "Could not connect to FactCheck.org.", "danger"

def get_credibility_from_reuters(keyword):
    """Scrape Reuters Fact Check using requests with retries."""
    search_url = f"https://www.reuters.com/search/news?sortBy=relevance&blob={urllib.parse.quote(keyword)}"
    score_map = {'true': 1.0, 'partially true': 0.5, 'misleading': 0.3, 'false': 0.1}
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(search_url, headers=get_headers(), timeout=20)
        logging.info(f"Scraping Reuters: {search_url}, Status: {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('article')
        
        if not result:
            return 0.5, "No relevant fact-checks found on Reuters.", "info"
        
        content = result.get_text().lower()
        for key in score_map:
            if key in content:
                matched_score = score_map[key]
                message, status = format_result(key, matched_score, "Reuters")
                return matched_score, message, status
        
        return 0.5, "No clear rating found on Reuters.", "info"
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Reuters scraping failed: {e}")
        return 0.5, "Could not connect to Reuters.", "danger"

def format_result(rating_text, score, source):
    """Format the result message and status based on score."""
    rating_text = rating_text.title()
    if score > 0.7:
        message = f"{source} found the claim to be **{rating_text}**, suggesting high credibility."
        status = "success"
    elif score < 0.3:
        message = f"{source} found the claim to be **{rating_text}**, suggesting very low credibility."
        status = "danger"
    else:
        message = f"{source} found the claim to be **{rating_text}**. The credibility is moderate or mixed."
        status = "warning"
    return message, status

def aggregate_credibility(keyword):
    """Aggregate credibility scores from multiple sources."""
    sources = [
        get_credibility_from_politifact,
        get_credibility_from_snopes,
        get_credibility_from_factcheck_org,
        get_credibility_from_reuters
    ]
    scores = []
    messages = []
    statuses = []
    
    for source_func in sources:
        time.sleep(5)  # Increased delay to avoid rate-limiting
        try:
            score, message, status = source_func(keyword)
            scores.append(score)
            messages.append(message)
            statuses.append(status)
        except Exception as e:
            logging.error(f"Error in {source_func.__name__}: {e}")
            messages.append(f"Failed to retrieve data from {source_func.__name__.replace('get_credibility_from_', '')}.")
            statuses.append("danger")
            scores.append(0.5)
    
    # Aggregate scores (average of non-default scores)
    valid_scores = [s for s in scores if s != 0.5]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.5
    
    # Aggregate messages
    final_message = "<br>".join(messages)
    if not valid_scores:
        final_message += "<br>No fact-checks found across sources. Try a more specific claim (e.g., 'Biden created 14 million jobs' or 'Biden inflation 2023') or check primary sources like government reports."
    final_status = "success" if avg_score > 0.7 else "danger" if avg_score < 0.3 else "warning"
    
    return avg_score, final_message, final_status

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    keyword = request.form.get('keyword')
    
    if not keyword:
        return "Please provide a keyword.", 400

    # Check cache first
    cached_result = get_cached_result(keyword)
    if cached_result:
        credibility_score, result_message, status = cached_result
        return render_template(
            'result.html',
            keyword=keyword,
            credibility_score=round(float(credibility_score), 2),
            result_message=result_message,
            status=status,
            cached=True
        )

    # Try original keyword first, then refined if no results
    credibility_score, result_message, status = aggregate_credibility(keyword)
    if credibility_score == 0.5 and nlp:
        refined_keyword = refine_keyword(keyword)
        if refined_keyword != keyword:
            credibility_score, result_message, status = aggregate_credibility(refined_keyword)
            result_message += f"<br>Refined keyword used: '{refined_keyword}'"
    
    # Cache result
    cache_result(keyword, credibility_score, result_message, status)
    
    return render_template(
        'result.html',
        keyword=keyword,
        credibility_score=round(credibility_score, 2),
        result_message=result_message,
        status=status,
        cached=False
    )

if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(debug=True)