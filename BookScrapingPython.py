import csv
import requests
from bs4 import BeautifulSoup

## Etape 1 _ Récupération dees infos sur une page produit de https://books.toscrape.com/

url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Récupération des infos de la page
def get_book_information(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  universal_product_code = soup.find("th", text="UPC").find_next("td").text
  title = soup.find("h1").text
  price_including_tax = soup.find("th", text="Price (incl. tax)").find_next("td").text.encode('utf-8').decode('utf-8')
  price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next("td").text.encode('utf-8').decode('utf-8')
  number_available = soup.find("th", text="Availability").find_next("td").text
  product_description = soup.find("h2", text="Product Description").find_next("p").text
  category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
  review_rating = soup.find("p", class_="star-rating").get("class")[1]
  image_url = soup.find("img").get("src").replace("../..", "https://books.toscrape.com")
  return url, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url

# Ecriture des infos dans un fichier CSV

with open("book_info.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"])
    writer.writerow(get_book_information(url))
