import requests
import math
import smtplib
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"


# -------------------------- GET STOCKS DATA FROM API ----------------------------

# making a request
stocks_endpoint = 'https://www.alphavantage.co/query'
parameters = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': 'IBM',
    'apikey': os.environ.get("STOCK_API_KEY")
}

response = requests.get(url=stocks_endpoint, params=parameters)
response.raise_for_status()
stock_data = response.json()
# turn stock_data dict into a list, so we can pass each date as an index to the dictionary
# ,and we can access the closing stock prices in the last two days
dates = list(stock_data["Time Series (Daily)"])
recent_close_prices = [stock_data["Time Series (Daily)"][date]["4. close"] for date in dates[:2]]

# put the extracted values into variables,
yday_stocks = float(recent_close_prices[0])
day_before_yday_stocks = float(recent_close_prices[1])

# -------------------------- determines the change percentage in the stock prices ----------------------------

difference = yday_stocks - day_before_yday_stocks
dif_percentage = math.floor((difference/yday_stocks) * 100)

if dif_percentage < 0:
    sign = "🔻"
else:
    sign = "🔺"

# formats the header
header = f"{STOCK} {sign}{dif_percentage}%".encode('ascii', 'ignore').decode('ascii')

# if the difference is equal or more than 5%,
# get the first three articles about the stock
if abs(dif_percentage) >= 5:

    news_endpoint = "https://newsapi.org/v2/everything"
    parameters = {
        "q": "tesla",
        "apiKey": os.environ.get("NEWS_API_KEY")
    }

    response = requests.get(news_endpoint, params=parameters)
    # extract the first three articles
    articles = response.json()["articles"][:3]
    # format each article as how you want each of them to appear and put them into a list
    news = [f"Headline: {article['title']} \n\nBrief: {article['description']}\n\n" for article in articles]
    for article in news:
        # encode method was needed as it gave me an error and the text was not appearing properly
        msg = article.encode('ascii', 'ignore').decode('ascii')

        with smtplib.SMTP("smtp.gmail.com") as connection:
            my_email = "sintercvnt@gmail.com"
            password = os.environ.get("APP_KEY")
            # secures the connection
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs="sintercvnt606@yahoo.com",
                                msg=f"Subject: {header}\n\n{msg}")
