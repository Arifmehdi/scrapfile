from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import sys



def get_title(soup):
        try:
            title = soup.find('span',attrs={'id': 'productTitle'})
            title_value  = title.text
            title_string = title_value.strip()
        except AttributeError:
             title_string = ''
        return title_string


def get_price(soup):
        try:
            price = soup.find('span',attrs={'class': 'a-price a-text-price a-size-medium apexPriceToPay'})
            title_value  = price.string.strip()
            price = title_value.strip()

            # product_price = new_soup.find('span',attrs={'class': 'a-price a-text-price a-size-medium apexPriceToPay'})
            # if product_price:
            #     price = product_price.text.strip()
            # else:
            #         price = None
        except AttributeError:
             price = ''
        return price

def get_rating_count(soup):
        try:
            rating = soup.find('span',attrs={'class': 'a-size-base a-color-base'})
            rating_value  = rating.string.strip()
            # price = rating_value.strip()
            
        except AttributeError:
             try:
                  rating = soup.find('span',attrs={'class': 'a-icon-alt'}).string.strip()
                  
             except AttributeError: 
                  rating = ''
        return rating
# URL = "https://www.amazon.com/s?k=mens+fashion&crid=30QCZBQEV8NGO&sprefix=mens+fashion%2Caps%2C351&ref=nb_sb_noss_1"
# URL = "https://www.amazon.com/s?k=mens+fashion&crid=3UU0A90UY114U&sprefix=%2Caps%2C398&ref=nb_sb_ss_recent_1_0_recent"
# URL = "https://www.amazon.com/s?k=mens+fashion&crid=3UU0A90UY114U&sprefix=%2Caps%2C398&ref=nb_sb_ss_recent_1_0_recent"
# URL = "https://www.amazon.com/b/?_encoding=UTF8&node=1045624&bbn=7141123011&ref_=Oct_d_odnav_d_2476517011_0&pd_rd_w=V18dN&content-id=amzn1.sym.ed470844-7314-4717-8e3f-b384c77cdbd8&pf_rd_p=ed470844-7314-4717-8e3f-b384c77cdbd8&pf_rd_r=X2M1MN066SQWVX87CXNP&pd_rd_wg=sbgHT&pd_rd_r=095fa9a5-c908-44c2-9462-07b2998b110a"
URL = "https://www.amazon.com/s?k=womens+fashion&ref=nb_sb_noss"

HEADER = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36','Accept-Language' : 'en-US' 'en;q=0.5'})
webpage = requests.get(URL, headers=HEADER)
content = webpage.content
soup = BeautifulSoup(content,'html.parser')
links = soup.find_all("a",attrs={'class':'a-link-normal s-no-outline'})
# links = soup.find_all("a",attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})

links_list = []

for link in links:
    links_list.append(link.get('href'))
d = {'title':[], 'price':[], 'rating':[], 'reviews':[], 'availaivality':[]}

for link in links_list:
    # link = links[0].get('href')
    product_list = 'https://www.amazon.com'+link
    new_webpage = requests.get(product_list,headers=HEADER)
    time.sleep(3)
    new_soup = BeautifulSoup(new_webpage.content,'html.parser')

    d['title'].append(get_title(new_soup))
    d['price'].append(get_price(new_soup))
    d['rating'].append(get_rating_count(new_soup))
print(d)
sys.exit()
    # d['reviews'].append(get_reviews_count(new_soup))
    # d['availbility'].append(get_availbility(new_soup))



    # print(HEADER)
    # print(URL)
    # print(links)
    # print(title)
    # print(price)
    # print(link)
    # print(webpage)
    # print(soup)
    # print(product_list)
    # print(new_soup)
    # print(product_title)
    # print(product_price)
    # /html/body/div[2]/div[1]/div[2]/div[3]/div/div/div/div[3]/div[8]/span/div/div/div[2]/div[1]/h2/a


