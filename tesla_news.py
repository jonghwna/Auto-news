import os
import json
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Perplexity API configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
openai.api_key = PERPLEXITY_API_KEY
openai.api_base = "https://api.perplexity.ai"

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'tesla!A:E'  # Updated to include date column (A) and all other columns (B-E)

def get_google_sheets_credentials():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token))
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_tesla_news():
    # Get yesterday's date in YYYY-MM-DD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Prepare the messages
    messages = [
        {
            "role": "system",
            "content": """You are an expert news research assistant specializing in in Tesla and Tesla related political news. Your task is to:
1. Find the most relevant and recent news articles about Tesla
2. Provide accurate and detailed information
3. Format the response as a valid JSON array
4. Include only factual information with proper sources
5. Focus on significant developments, announcements, and market impacts"""
        },
        {
            "role": "user",
            "content": f"""Find news articles about Tesla published on {yesterday}. For each article:
1. Title: The exact headline of the article
2. Source: The name of the news organization or website
3. URL: The direct link to the article
4. Summary: A detailed 3-4 bullet point summary focusing on key financial facts, events, and context

Format the response as a JSON array. Example:
[
    {{
        "title": "Tesla Announces New Factory in Texas",
        "source": "Reuters",
        "url": "https://reuters.com/tesla-factory",
        "summary": "Tesla has announced plans to build a new Gigafactory in Texas. The facility will produce the Cybertruck and create 5,000 jobs. Production is expected to begin in 2024."
    }}
]"""
        }
    ]
    
    try:
        # Get chat completion
        response = openai.ChatCompletion.create(
            model="sonar-pro",  # Using the correct model name from Perplexity docs
            messages=messages,
            temperature=0.7,
            max_tokens=6000  # Increased token limit for more detailed responses
        )
        
        # Print the raw response for debugging
        print("Raw API Response:", response)
        
        # Get the content from the response
        content = response.choices[0].message.content
        print("Response Content:", content)
        
        # Try to parse the JSON response
        try:
            news_articles = json.loads(content)
            if not isinstance(news_articles, list):
                print("Error: Response is not a JSON array")
                return []
            return news_articles
        except json.JSONDecodeError as je:
            print(f"JSON Parse Error: {str(je)}")
            print("Invalid JSON content:", content)
            return []
            
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        if hasattr(e, 'response'):
            print("Response content:", e.response.text)
        return []

def update_google_sheet(news_articles):
    creds = get_google_sheets_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Get yesterday's date in YYYY-MM-DD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Prepare the data for Google Sheets
    values = []
    for article in news_articles:
        values.append([
            yesterday,  # Date column
            article['title'],
            article['source'],
            article['url'],
            article['summary']
        ])
    
    body = {
        'values': values
    }
    
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"Updated {len(values)} rows in Google Sheet")
    except Exception as e:
        print(f"Error updating Google Sheet: {str(e)}")

def main():
    print("Starting Tesla news collection...")
    news_articles = get_tesla_news()
    if news_articles:
        update_google_sheet(news_articles)
    else:
        print("No news articles found or error occurred")

if __name__ == "__main__":
    main() 