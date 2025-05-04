import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json

with open("config.json") as f:
    config = json.load(f)

PERPLEXITY_API_KEY = config["PERPLEXITY_API_KEY"]
SPREADSHEET_NAME = config["SPREADSHEET_NAME"]

def search_news_with_perplexity(query, num_results=10):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    prompt = f"""You are a financial news analyst. Search for and analyze news articles about {query} from {yesterday}.
    For each article, provide:
    1. Title
    2. URL
    3. A detailed 3-4 bullet point summary focusing on key financial facts, events, and context
    Format the response as a JSON array of objects with 'title', 'url', and 'summary' fields.
    Limit to {num_results} articles.
    Only include articles from reputable financial news sources.
    Ensure summaries are detailed and information-rich, not overly brief."""
    
    data = {
        "model": "sonar-medium-online",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("🧪 API 응답:", result)  # Debug print like in original code
        articles = json.loads(result['choices'][0]['message']['content'])
        return articles
    except Exception as e:
        print(f"Error searching with Perplexity: {str(e)}")
        return []

def write_to_google_sheets(rows):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1D67mpImQLqnHI4MKnvRcsWD6G5n-lZJsSwn06tMF4Po/edit?usp=sharing").sheet1
    for row in rows:
        sheet.append_row(row)

def run():
    date = datetime.now().strftime("%Y-%m-%d")
    query = "Tesla"
    news_items = search_news_with_perplexity(query)

    if not news_items:
        print("❗ 검색된 뉴스가 없습니다.")
        return

    results = []
    for item in news_items:
        title = item["title"]
        link = item["url"]
        summary = item["summary"]
        print("📰 기사:", title)
        
        if not summary:
            print("⚠️ 요약 실패:", title)
            continue
            
        row = [date, title, summary, link]
        print("📌 저장할 데이터:", row)
        results.append(row)

    if results:
        write_to_google_sheets(results)
        print("✅ Google Sheets에 저장 완료")
    else:
        print("⚠️ 저장할 데이터가 없습니다.")

if __name__ == "__main__":
    run() 