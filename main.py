import os
from dotenv import load_dotenv
import requests
import pandas as pd
import openai

# load environment variables from .env (openai token)
load_dotenv()

# Access API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if key loaded
if openai_api_key:
    print("API key loaded successfully!")
else:
    print("API key not found. Check .env file")

# Load News API Key
newsapi_key = os.getenv("NEWS_API_KEY")

# Define the API endpoint and parameters
url = "https://newsapi.org/v2/everything"

params = {
    "q": "stock market OR stocks OR finance", # newsapi search keywords
    "language": "en",
    "sortBy": "publishedAt", # sorts for news posted most recently
    "pageSize": 20,
    "apiKey": newsapi_key
}

# Make the HTTP request to newsAPI
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200: # indicates successful request
    data = response.json()
    articles = data.get("articles", [])
    print(f"Fetched {len(articles)} articles")
else:
    print(f"Error fetching news: {response.status_code}")

# Prepare a list of articles to save
news_list = []

for article in articles:
    news_list.append({
        "title": article["title"],
        "description": article["description"],
        "url": article["url"],
        "publishedAt": article["publishedAt"],
        "source": article["source"]["name"]
    })

# Convert to a DataFrame
df = pd.DataFrame(news_list)

# Save to CSV
df.to_csv("data/stock_news.csv", index=False)
print("Saved news to data/stock_news.csv")

# load the CSV saved above
df = pd.read_csv("data/stock_news.csv")

# Check the first 5 rows of the df
print(df.head())

# Remove articles with missing title or description
df = df.dropna(subset=["title","description"])

# Remove duplicates
df = df.drop_duplicates(subset={"title"})

print(f"After cleaning, {len(df)} articles remain")

# Combine title and description
df["text_for_ai"] = df["title"] + ". " + df["description"]

# Check the first 5 combined texts
print(df["text_for_ai"].head())

# Prompt template
def create_prompt(article_text):
    return (
        f"Write a concise, engaging stock news article based on the following information:\n\n"
        f"{article_text}\n\n"
        f"Keep it professional, clear, and under 150 words."
    )

# Test the first article
first_prompt = create_prompt(df["text_for_ai"].iloc[0])
print(first_prompt)

# Set your API key for OpenAI
openai.api_key = openai_api_key

def generate_article(prompt):
    """
    Sends a prompt to openAI and returns the AI generated text
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # using GPT-3.5 model
            messages=[{"role": "user","content": prompt}],
            temperature=0.7 # creativity: 0 = conservative, 1 = creative
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        print("Error generating article: ", e)
        return ""
    
# List to store generated articles from openAI
generated_articles = []
for i, article_text in enumerate(df["text_for_ai"]):
    prompt = create_prompt(article_text)
    print(f"\n Generating article {i+1}....")
    ai_text = generate_article(prompt)
    generated_articles.append({
        "original_text": article_text,
        "ai_article": ai_text
    })

# Convert to DataFrame
ai_df = pd.DataFrame(generated_articles)

# Save to CSV
ai_df.to_csv("data/generated_stock_news.csv",index=False)
print("/nAll AI-generated articales saved to data/generated_stock_news.csv")
    