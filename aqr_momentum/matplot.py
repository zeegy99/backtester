import requests
from bs4 import BeautifulSoup
import re
import webbrowser
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def sanitize_ticker(ticker):
    return ticker.replace('.', '-')



def find_nearest_date(date):
    count = 0
    '''We will use s&p 500 and find the closest date to when something is'''
    stock = yf.Ticker("KO")
    df = stock.history('10y')
    df.index = df.index.tz_localize(None)

    if date in df.index:

        return date
    
    date_2 = date
 
    while date not in df.index:
        count += 1
        date = date + pd.DateOffset(days=count)
        date_2 = date_2 + pd.DateOffset(days=-count)
        
        if date in df.index:
            return date
        if date_2 in df.index:
            return date_2


def get_returns(ticker, start_date_obj, end_date_obj):
    stock = yf.Ticker(sanitize_ticker(ticker))
    df = stock.history(period = '10y')
    if len(df.index) == 0:
        print("HI")
        return -1
    
    start_open_price = 1
    end_open_price = 1
    
    
    df.index = df.index.tz_localize(None)

    
    if (start_date_obj in df.index):
        row = df.loc[start_date_obj]
        start_open_price = row['Open']
    else:
        return -1
    
    if (end_date_obj in df.index):
        row2 = df.loc[end_date_obj]

        end_open_price = row2['Open']
    else:
        return -1

    #print(f"Open price: {start_open_price}, Close price: {end_open_price}")
    return (end_open_price - start_open_price)/(start_open_price)

# def get_tickers():







url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
resp = requests.get(url)

#print(resp.text) #Resp.text is giant html doctype

soup = BeautifulSoup(resp.text)

table = soup.find("table" ,{'id':"constituents"})

tr_tags = table.find_all("tr")

all_companies = []

for i in range(1,len(tr_tags)):
    temp_info = []
    for j in tr_tags[i].find_all('td'):
        temp_info.append(j.text.strip())
    all_companies.append(temp_info)


all_stock_tickers = [] #All stock tickers wow

for i in all_companies:
    all_stock_tickers.append(i[0])



'''Levers'''

k = 2 #holding period of stock in months
j = 3 #time horizon for when we check stock performance in months
total_portfolio_return = 0
start_date_obj = datetime.strptime("2015-04-15", "%Y-%m-%d")






for months in range(100):
    offset = pd.DateOffset(months=months)
    current_start = start_date_obj + offset
    current_end = current_start + pd.DateOffset(months=j)


    start_date_obj = find_nearest_date(current_start)
    end_date_obj = find_nearest_date(current_end)

    ticker_with_return_list = []
    for i in all_stock_tickers:
        temp = []
        temp.append(i)
        temp.append(get_returns(i, start_date_obj, end_date_obj))
        ticker_with_return_list.append(temp)



    sorted_ticker_with_return_list = sorted(ticker_with_return_list, key=lambda x: x[1], reverse = True)

    adjusted_return_list = []

    for i in sorted_ticker_with_return_list:
        if i[1] > 10 or i[1] == -1:
            continue
        else:
            adjusted_return_list.append(i)




    num = int(len(adjusted_return_list) / 10) 
    winners = [adjusted_return_list[i][0] for i in range(num)]
    losers = [adjusted_return_list[i][0] for i in range(len(adjusted_return_list) -num, len(adjusted_return_list))]




    '''Check performance by the end of the {jth} month'''

    tester_start_time, tester_end_time = end_date_obj, end_date_obj + pd.DateOffset(years=0, months=k, days=0)
    tester_end_time = find_nearest_date(tester_end_time)
    
    portfolio_return = 0
    for i in winners:
        portfolio_return += get_returns(i, tester_start_time, tester_end_time)

    for m in losers:
        portfolio_return -= get_returns(m, tester_start_time, tester_end_time)
    total_portfolio_return += portfolio_return
    print(f" Your portfolio return in month {months} was {portfolio_return}")

print(total_portfolio_return)