
# Fact-Check Verifier Flask App

## 📝 Project Overview

This Flask application is a versatile fact-checking tool designed to help users quickly verify the credibility of news or internet rumors. It integrates data from multiple reputable fact-checking websites (such as PolitiFact, Snopes, FactCheck.org, and Reuters) and aggregates the results into a comprehensive credibility score.

This project utilizes several advanced techniques to overcome the challenges of traditional web scraping:

  * **Selenium Browser Automation**: Used to handle dynamically loaded content on websites like PolitiFact and Snopes.
  * **requests library with a retry mechanism**: Used for scraping static websites (e.g., FactCheck.org and Reuters) and includes built-in error handling for network instability.
  * **SQLite Caching**: Stores query results in a local database to improve performance and reduce the frequency of requests to the target websites.
  * **spaCy Natural Language Processing**: An optional feature for keyword refinement that extracts core entities from long phrases to improve search accuracy.

-----

## ✨ Key Features

  * **Multi-Source Fact-Checking**: Simultaneously retrieves fact-check results from multiple authoritative websites.
  * **Comprehensive Credibility Score**: Aggregates ratings from different sources into a single credibility score ranging from 0 to 1.
  * **Smart Keyword Optimization**: Utilizes the **spaCy** library to automatically extract key entities from complex queries for more precise search results.
  * **High-Performance Caching System**: Uses **SQLite** to cache recent query results, preventing redundant scraping, speeding up the application, and reducing server load.
  * **Robust Scraping Architecture**: Combines the **requests** library's retry mechanism with **Selenium** browser automation to effectively handle dynamic website changes and anti-scraping measures.
  * **Clean and User-Friendly Interface**: Built with the **Bootstrap + Font Awesome** frameworks to provide an intuitive and responsive web interface.

-----

## 🛠️ Tech Stack

  * **Backend Framework**: [Flask](https://flask.palletsprojects.com/)
  * **Web Scraping**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/)
  * **Dynamic Content Handling**: [Selenium](https://selenium-python.readthedocs.io/)
  * **Natural Language Processing**: [spaCy](https://spacy.io/)
  * **Database**: [SQLite3](https://docs.python.org/3/library/sqlite3.html)
  * **Frontend Frameworks**: [Bootstrap 5](https://getbootstrap.com/), [Font Awesome 6](https://fontawesome.com/)
  * **HTTP Requests**: [requests](https://requests.readthedocs.io/en/latest/)

-----

## 🚀 Installation & Usage

### Prerequisites

  * **Python 3.x**
  * **Google Chrome browser** (required for Selenium)

### Step 1: Install Dependencies

First, clone the project to your local machine and install all the necessary Python libraries.

```bash
git clone <your-project-url>
cd <your-project-folder>
pip install -r requirements.txt
```

**`requirements.txt` File Content**

Make sure you have a `requirements.txt` file in your project's root directory with the following content:

```
Flask
requests
beautifulsoup4
selenium
urllib3
spacy
```

### Step 2: Download the spaCy Language Model

After installing the `spacy` library, you need to download an English language model. Run the following command in your terminal:

```bash
python -m spacy download en_core_web_sm
```

### Step 3: Install Chrome Driver

Selenium requires a driver that matches your Chrome browser's version.

  * Go to the official [ChromeDriver download page](https://googlechromelabs.github.io/chrome-for-testing/).
  * Download the ChromeDriver that matches your Chrome browser version.
  * Place the downloaded `chromedriver` executable in your system's PATH, or directly in your project's root directory.

### Step 4: Run the Application

In your terminal, navigate to the project's root directory and execute the following command:

```bash
python app.py
```

After the application starts, you will see a message in the terminal similar to this:

```bash
* Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

### Step 5: Open the Web Page

Open your browser and visit `http://127.0.0.1:5000` to start using the app.

-----

## ❓ Frequently Asked Questions

### Q: Why do I see a `No module named 'xxx'` error?

A: This means you haven't installed the required Python library. Please ensure you have run `pip install -r requirements.txt` and all libraries were installed successfully.

### Q: Why do I see a `Web scraping failed` or `Could not connect` error?

A: Web scraping can be fragile and is susceptible to website design changes. This error might occur because:

  * **The website's HTML structure has changed**: The class names or tags in your scraper code are no longer valid.
  * **Network connection issues**: Your network is unstable or your IP has been blocked by the website.
  * **Anti-bot measures**: The website has detected and blocked your scraping activity.

If this error occurs frequently, you may need to inspect the target website's HTML and update the scraping logic in your `get_credibility_from_...` functions.

### Q: What does `No relevant fact-checks were found...` mean?

A: This result usually indicates one of the following:

  * The keyword you entered is too broad, and no fact-checking article exists on the topic.
  * Your scraper successfully connected to the website but couldn't find any results that match the keyword.
  * If **spaCy** is enabled, it may have failed to extract meaningful entities from your query.
  
  ## Author
* **[Your Name/Alias]** - [Link to your GitHub Profile](https://github.com/your-username)
  * e.g., "Connect with me on [LinkedIn](https://linkedin.com/in/your-linkedin) or [Twitter](https://twitter.com/your-twitter)."
---
## Author
* **[Chen cian-rong/Joanna]** - [GitHub](https://github.com/CSSXML)
  * e.g., "Connect with me on [LinkedIn](www.linkedin.com/in/joanna-chen-4228152b8) 
  
  
# 訊息事實檢測平台

## 📝 專案簡介

這個 Flask 應用程式是一個多功能的事實查核工具，旨在幫助使用者快速驗證新聞或網路謠言的可信度。它整合了多個知名事實查核網站（如 PolitiFact、Snopes、FactCheck.org 和 Reuters）的資料，並將結果匯總成一個綜合性的可信度分數。

本專案利用了多種先進技術來克服傳統網頁爬蟲的挑戰，例如：

  * **Selenium 瀏覽器自動化**：用來處理動態載入內容的網站（如 PolitiFact 和 Snopes）。
  * **requests 函式庫與重試機制**：用來爬取靜態網站（如 FactCheck.org 和 Reuters），並內建錯誤處理以應對網路不穩定。
  * **SQLite 緩存機制**：將查詢結果儲存在本地資料庫中，以提高效率並減少對目標網站的請求頻率。
  * **spaCy 自然語言處理**：可選的關鍵詞優化功能，用於從長句中提取核心實體，以提高搜尋準確性。

-----

## ✨ 功能特色

  * **多源頭事實查核**：同時從多個權威網站獲取查核結果。
  * **綜合可信度分數**：將不同來源的評分匯總為一個單一的 0 到 1 的可信度分數。
  * **智慧關鍵詞優化**：利用 spaCy 函式庫，自動從複雜的查詢中提取關鍵實體，以得到更精準的搜尋結果。
  * **高效能緩存系統**：使用 SQLite 緩存最近的查詢結果，避免重複爬取，提升速度並降低伺服器負擔。
  * **強健的爬蟲架構**：結合 requests 函式庫的重試機制和 Selenium 瀏覽器自動化，有效應對網站的動態變化和反爬蟲措施。
  * **簡潔友好的使用者介面**：使用 Bootstrap + Font Awesome 框架，提供一個直觀且響應式的網頁介面。

-----

## 🛠️ 技術棧

  * **後端框架**：[Flask](https://flask.palletsprojects.com/)
  * **網頁爬蟲**：[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/)
  * **動態內容處理**：[Selenium](https://selenium-python.readthedocs.io/)
  * **自然語言處理**：[spaCy](https://spacy.io/)
  * **資料庫**：[SQLite3](https://docs.python.org/3/library/sqlite3.html)
  * **前端框架**：[Bootstrap 5](https://getbootstrap.com/)
  * **網路請求**：[requests](https://requests.readthedocs.io/en/latest/)

-----

## 🚀 安裝與執行

### 前提條件

  * **Python 3.x**
  * **Chrome 瀏覽器** (因專案使用 Selenium)

### 步驟 1: 安裝依賴項

首先，將專案複製到你的本地，然後安裝所有必要的 Python 函式庫。

```bash
git clone <你的專案網址>
cd <你的專案資料夾>
pip install -r requirements.txt
```

**`requirements.txt` 檔案內容**

請確保你的專案根目錄有一個 `requirements.txt` 檔案，內容如下：

```
Flask
requests
beautifulsoup4
selenium
urllib3
spacy
```

### 步驟 2: 下載 spaCy 語言模型

在安裝 `spacy` 函式庫後，你需要下載一個英文語言模型。在終端機中執行以下指令：

```bash
python -m spacy download en_core_web_sm
```

### 步驟 3: 安裝 Chrome Driver

Selenium 需要一個對應你 Chrome 瀏覽器版本的驅動程式。

  * 前往 [ChromeDriver 官方下載頁面](https://googlechromelabs.github.io/chrome-for-testing/)。
  * 下載與你 Chrome 瀏覽器版本相符的 ChromeDriver。
  * 將下載好的 `chromedriver` 執行檔放在你的系統 PATH 環境變數中，或者直接放在專案根目錄下。

### 步驟 4: 執行應用程式

在終端機中，從專案根目錄執行以下指令：

```bash
python app.py
```

應用程式啟動後，你將會在終端機中看到類似以下的訊息：

```bash
* Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

### 步驟 5: 開啟網頁

在你的瀏覽器中，訪問 `http://127.0.0.1:5000` 即可開始使用。

-----

## ❓ 常見問題

### Q: 為什麼我會看到 `No module named 'xxx'` 的錯誤？

A: 這表示你沒有安裝所需的 Python 函式庫。請確保你已經執行了 `pip install -r requirements.txt`，並且所有函式庫都成功安裝。

### Q: 為什麼我會看到 `Web scraping failed` 或 `Could not connect` 的錯誤？

A: 網頁爬蟲容易受到網站設計變動的影響。這可能是因為：

  * **網站的 HTML 結構改變了**：爬蟲程式碼中的類別名稱或標籤已失效。
  * **網路連線問題**：你的網路不穩定或被網站封鎖。
  * **反爬蟲措施**：網站偵測到爬蟲行為並阻擋了你的請求。

如果頻繁發生此類錯誤，請考慮檢查並更新 `get_credibility_from_...` 函式中的爬蟲邏輯。

### Q: `No relevant fact-checks were found...` 是什麼意思？

A: 這通常表示：

  * 你輸入的關鍵字太過廣泛，沒有任何一個網站有查核過相關主題。
  * 你的爬蟲程式碼雖然成功連接到網站，但未能找到與關鍵字匹配的結果。
  * 如果啟用了 spaCy，它可能無法從你的關鍵字中提取出任何有意義的實體。

-----


## Author
* **[Your Name/Alias]** - [Link to your GitHub Profile](https://github.com/your-username)
  * e.g., "Connect with me on [LinkedIn](https://linkedin.com/in/your-linkedin) or [Twitter](https://twitter.com/your-twitter)."
---
## Author
* **[Chen cian-rong/Joanna]** - [GitHub](https://github.com/CSSXML)
  * e.g., "Connect with me on [LinkedIn](www.linkedin.com/in/joanna-chen-4228152b8) 