# Tesla News Collector

This project automatically collects Tesla news articles published the previous day using the Perplexity API and organizes them in a Google Sheet. The collection runs daily at 7 AM UTC.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Set up Google Sheets API**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the credentials and save as `credentials.json`
   - Create a new Google Sheet and copy its ID from the URL

3. **Set up GitHub Secrets**
   Add the following secrets to your GitHub repository:
   - `PERPLEXITY_API_KEY`: Your Perplexity API key
   - `SPREADSHEET_ID`: Your Google Sheet ID
   - `GOOGLE_CREDENTIALS`: The contents of your `credentials.json` file

4. **Local Development**
   - Create a `.env` file with the following variables:
     ```
     PERPLEXITY_API_KEY=your_perplexity_api_key
     SPREADSHEET_ID=your_spreadsheet_id
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the script:
     ```bash
     python tesla_news.py
     ```

## Google Sheet Structure
The script will create a sheet with the following columns:
- Title
- Source
- URL
- Summary

## Automation
The script runs automatically every day at 7 AM UTC through GitHub Actions. You can also trigger it manually through the GitHub Actions interface.

## Error Handling
The script includes error handling for:
- API request failures
- Google Sheets authentication issues
- Data parsing errors

## Contributing
Feel free to submit issues and enhancement requests! 