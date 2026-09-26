import tkinter as tk
import requests
import csv
import random
from bs4 import BeautifulSoup
import urllib

# global variables
numbers=[]
url=("")
result=0
final_result=("")
nearly_url=[]
urls=[]
contents=("")

# permanent variables
keys=["a","b","c","d","e","f","h","g","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0","-","."]
with urllib.request.urlopen("https://data.iana.org") as response:
    tlds_text = response.read().decode('utf-8')


ends = [line.strip().lower() for line in tlds_text.split('\n') if line and not line.startswith('#')]
nr_of_ends=len(ends)

#limits
max_sites=100 #change to any number
min_sites=100 #change to any number
max_characters_in_site=20

def make_list_of_numbers():
    for i in range (random.randint(1,max_characters_in_site)):
        result= random.randint(1, len.keys)
        numbers.append(result)

def convert_to_url():
    for current in numbers:
        final_result=keys[current]	
        nearly_url.append (final_result)
        end=ends[random.randint (1, len.(ends))]
    nearly_url.append(end)
    url="".join (nearly_url)

def test ():
    check = request.get(url)
    if check.status_code == 200:
        urls.append(url)


        

        html_content = check.text
        content = BeautifulSoup(html_content, "html.parser")


        clean_text = content.get_text()
        contents.append(clean_text)
    else:
        pass
    
def write_csv():
    headers = ["url","content"]
    with open('hereherehereherehere.csv', mode='w', newline='', encoding='utf-8-sig') as file:
   	 writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(zip(list1, list2))

make_list_of_numbers()
convert_to_url()
test()
write_csv()
