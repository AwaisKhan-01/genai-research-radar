import os
import time
import datetime
import urllib.parse
import feedparser
from google import genai

# Configure the LLM
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def fetch_latest_papers(max_results=3):
    """Fetches the latest research papers from ArXiv."""
    
    # ArXiv's legacy API requires strict formatting: '+' for spaces, '%22' for quotes.
    # We manually construct the exact string to prevent boolean logic from breaking.
    search_query = 'all:%22video+generation%22+AND+all:diffusion'
    url = f'http://export.arxiv.org/api/query?search_query={search_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    print(f"Querying ArXiv API: {url}")
    feed = feedparser.parse(url)
    return feed.entries

def analyze_paper(title, summary, max_retries=3):
    """Passes the paper details to the LLM with retry logic for 503 errors."""
    prompt = f"""
    Act as a Principal AI Engineer. We are building a daily research digest for a team building production Generative AI pipelines.
    Analyze the following academic paper abstract and extract the tangible engineering value.
    
    Format your response strictly as follows (use markdown bolding):
    **The TL;DR:** (One clear sentence explaining the core concept).
    **Architectural Innovation:** (What exactly did they change? e.g., modifications to DiT, U-Net, latent spaces, or attention mechanisms).
    **Engineering Takeaway:** (How could this be applied to real-world GenAI products or improve inference speed/quality?)
    
    Title: {title}
    Abstract: {summary}
    """
    
    # ---------------------------------------------------------
    # NEW: Exponential Backoff Retry Logic
    # ---------------------------------------------------------
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"  [!] API Call Failed (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = 15 * (attempt + 1) # Waits 15s, then 30s
                print(f"  [*] Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                return "> *Analysis failed due to sustained API high demand. Try reading the abstract directly on ArXiv.*"

def main():
    print("Agent waking up. Fetching papers...")
    papers = fetch_latest_papers()
    
    print(f"Found {len(papers)} papers matching the query.")
    if len(papers) == 0:
        print("No papers found today. Exiting without creating a blank report.")
        return
    
    daily_report = f"# AI Research Digest - {datetime.date.today()}\n\n"
    daily_report += "> *Automated daily analysis of the latest text-to-video and diffusion model research.*\n\n"
    
    for paper in papers:
        print(f"Analyzing: {paper.title}")
        analysis = analyze_paper(paper.title, paper.summary)
        
        daily_report += f"### {paper.title}\n"
        daily_report += f"[Read Full Paper on ArXiv]({paper.link})\n\n"
        daily_report += f"{analysis}\n\n"
        daily_report += "---\n"
        
    # Save the report to a file
    file_path = f"reports/digest_{datetime.date.today()}.md"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(daily_report)
        
    print(f"Successfully generated and saved research digest to {file_path}")

if __name__ == "__main__":
    main()