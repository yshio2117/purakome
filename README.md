# Anime Sentiment Analyzer 🇯🇵📊
*(Japanese Anime Review Sentiment Analysis Web App)*  

[![Demo App](https://img.shields.io/badge/Demo_App-Click_Here-brightgreen?style=for-the-badge)](https://purakome.net/sentiment/anime/jojo-stone-ocean/)



## 📖 Project Overview
This web application analyzes viewer sentiment towards Japanese anime titles by processing real-time review data.
It collects tweets using the **Twitter API**, classifies them into 5 sentiment levels using a **custom Machine Learning model**, and visualizes the results on a web dashboard.

I developed this project to demonstrate my skills in **Full-stack Development (Django)**, **Data Engineering**, and **Natural Language Processing (NLP)**.


> 🚧 **Current Status:** I am currently implementing an End-to-End test automation framework using **Playwright & Python** to ensure quality and robustness.  

<br>

## 🛠 Tech Stack
*   **Language:** Python 3
*   **Framework:** Django (MVT Architecture)
*   **Database:** PostgreSQL
*   **Machine Learning / NLP:**
    *   MeCab (Morphological Analysis for Japanese text)
    *   Scikit-learn for Sentiment Classification
*   **API Integration:** Twitter API
*   **Frontend:** HTML5, CSS, Bootstrap, JavaScript
*   **DevOps / Tools:** Git  
<br>


## 🌟 Key Features
1.  **Batch Data Ingestion:** 
    *   Collects and processes large volumes of tweet data in batches (managed manually or via scheduler).
2.  **Sentiment Analysis Engine:**
    *   Pre-processes Japanese text using **MeCab**.
    *   Classifies reviews into 5 scales: *Very Positive, Positive, Neutral, Negative, Very Negative*.
3.  **User-Friendly Visualization & Insights:**
    *   **Sentiment Ratio Chart:** Graphically visualizes the distribution of "Positive" vs. "Negative" reviews (e.g., Pie Chart/Bar Chart), allowing users to assess the overall reception instantly.
    *   **Word Cloud:** Visually maps the most frequent keywords to grasp main topics at a glance.
    *   **Review Summarization:** Extracts and displays key highlights from reviews, helping general users understand the reasons behind the ratings.
    *   **Top-Rated Anime Ranking (Leaderboard):** gregates sentiment scores across multiple anime titles. Displays a leaderboard of titles sorted by positivity (descending order), allowing users to identify the most highly-acclaimed anime instantly.  
5.  **Performance Optimization:** 
    *   Since data is pre-processed and stored in DB, the web dashboard provides fast response times without waiting for API calls.  
<br>



## 🏗 Architecture
This application consists of two main components: a **Data Pipeline (Batch Processing)** and a **Web Dashboard**.

1.  **Data Collection (Batch Process):** 
    *   A Python script periodically fetches tweets via Twitter API.
    *   Text data is tokenized by MeCab and classified by the ML model.
    *   Processed data is stored in **PostgreSQL**.
2.  **Web Application (Django):** 
    *   The Django frontend queries the database to display pre-analyzed sentiment trends to users.  
<br><br>


## 🚀 Setup & Installation (Local)
```bash
# Clone the repository
git clone https://github.com/yshio2117/purakome.git

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver

   
   
