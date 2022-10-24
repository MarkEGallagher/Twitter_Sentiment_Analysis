from statistics import mean
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup as bs
import html5lib
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from datetime import date
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Setting up the Edge webdriver - enter the file path of your driver in the open parentheses below
driver = webdriver.Edge()

#Logging into Twitter by passing Username and Password - enter your username and password in the .send_keys open parentheses below.
driver.get('https://twitter.com/i/flow/login')
time.sleep(5)
username = driver.find_element(By.TAG_NAME, "input")
username.send_keys()
driver.find_element(By.XPATH, "//div[@class='css-18t94o4 css-1dbjc4n r-sdzlij r-1phboty r-rs99b7 r-ywje51 r-usiww2 r-2yi16 r-1qi8awa r-1ny4l3l r-ymttw5 r-o7ynqc r-6416eg r-lrvibr r-13qz1uu']").click()
time.sleep(5)
pword = driver.find_element(By.XPATH, "//input[@name='password']")
pword.send_keys()
driver.find_element(By.XPATH, "//div[@data-testid='LoginForm_Login_Button']").click()
time.sleep(5)

#Searching for the topic that I want to collect data for - enter your topic using the .send_keys function
searchbar = driver.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")
searchbar.send_keys("Philadelphia 76ers")
searchbar.send_keys(Keys.ENTER)
time.sleep(5)

#Defining empty lists
name_data = []
text_data = []
date_data = []
handle_data = []

#Scroll function to obtain more data
def scroll(x):
    start = time.time()
    initialScroll = 0
    finalScroll = 1000 
    while True:
        driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
        initialScroll = finalScroll
        finalScroll += 1000
        time.sleep(3)
        end = time.time()
        if round(end - start) > x:
            break

#Defining collection function
def collection():
    source = driver.page_source
    soup = bs(source, 'lxml')
    for row in soup.find_all('article'):
        name = row.find_all('div', attrs = {'data-testid':'User-Names'})
        text = row.find_all('div', attrs = {'data-testid':'tweetText'})
        tweet = ""
        for item in name:
            col1 = item.get_text()
            col1 = col1.strip()
            if col1.find("&", 0, len(col1)) == -1:
                col1 = col1.split("@")
                col1v2 = col1[1].split("·")
                col1v3 = col1v2[1]
                handle_data.append("@" + col1v2[0])
            else:
                col1v2 = col1.split("·")
                print(col1v2)
                col1 = col1v2[0].split("@", 1)
                col1v2 = col1v2[0].replace("@", "")
                print(col1)
                col1v3 = col1v2[1]
                handle_data.append("@" + col1[1])
            if ' ' not in col1v3:
                col1v3 = date.today()
                col1v3 = col1v3.strftime('%B %d')
            if col1[0] != "":
                name_data.append(col1[0])
            else:
                name_data.append("Emojis")
            date_data.append(col1v3)
        for item in text:
            col2 = item.get_text()
            col2 = col2.strip()
            col2 = col2.replace('\n','')
            col2 = col2.replace('\n\n','')
            tweet = tweet + col2
        text_data.append(tweet)    

#Collecting the data
collection()
scroll(10)
collection()
scroll(20)
collection()
scroll(30)
collection()
scroll(40)
collection()
scroll(50)
collection()
time.sleep(3)

#Removing any duplicate list items
text_data = list(set(text_data))

#Creating a pandas dataframe
sixers_data = pd.DataFrame({'Name':name_data, 'Handle':handle_data, 'Date_Tweeted': date_data, 'Tweet':text_data})

#Defining new lists for future data wrangling
compound_sentiment = []
sentiment_classification = []
player_categorization = []

#Defining the list of Philadelphia 76ers Players
sixers_players = ["Embiid", "Harden", "Maxey", "Harris", "Harrell", "Melton", "Springer", "Tucker", "Milton", "Niang", "Thybulle", "House", "Korkmaz", "Foster", "Reed", "Champagnie", "Rivers"]

#Setting up sentiment analyzer
def sentiment_score(tweet):
    sentiment_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sentiment_obj.polarity_scores(tweet)
    compound_sentiment.append(sentiment_dict['compound'])
    if sentiment_dict['compound'] >= 0.05 :
        sentiment_classification.append(("Positive"))
    elif sentiment_dict['compound'] <= - 0.05 :
        sentiment_classification.append(("Negative"))
    else :
        sentiment_classification.append(("Neutral"))

def categorization(tweet):
    y = 0
    for x in sixers_players:
        if tweet.find(x, 0, len(tweet))!= -1:
            player_categorization.append(x)
            break
        else:
            y+=1
            continue
    if y == len(sixers_players):
        player_categorization.append("No Categorization")

#Analyzing the sentiment of each tweet and adding a player categorization
for tweet in sixers_data['Tweet']:
    sentiment_score(tweet)
    categorization(tweet)


#Adding sentiment data to the main dataframe
sixers_data['Sentiment_Score'] = compound_sentiment
sixers_data['Sentiment_Classification'] = sentiment_classification
sixers_data['Player_Categorization'] = player_categorization

#Printing the overall sentiment result
if sum(sixers_data['Sentiment_Score'])/len(sixers_data['Sentiment_Score']) >= 0.05:
    print("The overall sentiment regarding the Philadelphia 76ers is positive :)")
elif sum(sixers_data['Sentiment_Score'])/len(sixers_data['Sentiment_Score']) <= -0.05:
    print("The overall sentiment regarding the Philadelphia 76ers is negative :(")
else:
    print("The overall sentiment regarding the Philadelphia 76ers is neutral :|")

#Converting the data to excel
sixers_data.to_excel()