import os
import json
import feedparser
import datetime
import urllib.parse # Added for URL Encoding
from google import genai # Updated Google SDK

# 1. Configure the LLM using the new SDK syntax
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def fetch_latest_papers(query='all:"Wan 2.2" OR all:"video generation"', max_results=3):
    """Fetches the latest research papers from ArXiv based on specific AI architectures."""
    
    # URL Encode the query to safely handle spaces and quotes
    safe_query = urllib.parse.quote(query)
    url = f'http://export.arxiv.org/api/query?search_query={safe_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    feed = feedparser.parse(url)
    return feed.entries

def analyze_paper(title, summary):
    """Passes the paper details to the LLM for analysis."""
    prompt = f"""
    Act as a Senior AI Researcher. Analyze the following paper abstract and provide:
    1. A one-sentence ELI5 summary.
    2. The core technical innovation (e.g., specific architectural changes to the U-Net or DiT).
    3. Potential real-world application.
    
    Title: {title}
    Abstract: {summary}
    """
    
    # Updated text generation syntax for the new google-genai library
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def main():
    print("Agent waking up. Fetching papers...")
    papers = fetch_latest_papers()
    
    daily_report = f"# AI Research Digest - {datetime.date.today()}\n\n"
    
    for paper in papers:
        print(f"Analyzing: {paper.title}")
        analysis = analyze_paper(paper.title, paper.summary)
        
        daily_report += f"## {paper.title}\n"
        daily_report += f"**Link:** {paper.link}\n\n"
        daily_report += f"{analysis}\n\n"
        daily_report += "---\n"
        
    # Save the report to a file
    file_path = f"reports/digest_{datetime.date.today()}.md"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(daily_report)
        
    print(f"Report saved to {file_path}")

if __name__ == "__main__":
    main()