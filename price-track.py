#!/usr/bin/env python

import requests
import urllib.request
import time
import datetime
import re
from bs4 import BeautifulSoup
import smtplib, ssl
#from dateutil import parser

port = 465  # For SSL
password = 'twist meal stra6ighten short class%'

# Create a secure SSL context
context = ssl.create_default_context()
sender_email = 'price.tracker.project.accnt@gmail.com'
receiver_email = "brargolf@gmail.com"

def send_email(link=None, old_price=None, now_price=None, message=None):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        # parser.parse(strtime)
        # datetime.datetime(2012, 11, 13, 17, 2, 22, 395000)
        if not message:
            message = f'''\
Subject: Price alert


The price of your tracked item has dropped.
Old Price:
${old_price['price']:.2f} (at {old_price['time']})
New Price:
${now_price['price']:.2f} (at {old_price['time']})

Go to {link} to check it out.'''

        # Send email here
        server.sendmail(sender_email, receiver_email, message)

def get_price_from_string(s):
    m = re.search(r'\$([0-9]+[\.]*[0-9]*)', s)
    return float(m.group()[1:]) if m else None

prices = [{'time':str(datetime.datetime.now()),'price':0.00}]
counter = 0

while True:
    counter += 1
    link =  'https://www.orvis.com/p/weatherbreaker-jacket/1z5b'
    response = requests.get(link)
    if response.status_code != 200:
        with open('logfile', 'a+') as log_file:
            logfile.write(response.status_code)
            logfile.write(response.text)
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    non_sale_element = soup.find_all('span', attrs = {'class' : 'MemPrice'})
    sale_element = soup.find_all('span', attrs = {'class' : 'MemSalePrice'})
    price = 0.00
    if len(sale_element) > 0:
        price = get_price_from_string(sale_element[0].text)
    else:
        price = get_price_from_string(non_sale_element[0].text)

    old_price = prices[-1]
    now_price = {'time' : str(datetime.datetime.now()),'price' : price}

    if price < old_price['price']:
        send_email(link=link, old_price=old_price, now_price=now_price)
        counter = 0

    elif counter % 24 == 0:
        # send daily update
        message=f'''\
Subject: Price is steady


The price of your tracked item is steady.
${price:.2f} (as of {now_price['time']}

View the item at {link}'''
        send_email(link=link, message=message)
        counter = 0
    
    prices.append(now_price)

    with open('output', 'a+') as out_file:
        out_file.write(f'${now_price["price"]:.2f now_price["time"]')
    # sleep for 1 hour
    time.sleep(60*60)


