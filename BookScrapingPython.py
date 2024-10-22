import csv
import requests
from bs4 import BeautifulSoup

## Etape 1 _ Récupération dees infos sur une page produit de https://books.toscrape.com/

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

# Récupération des infos de la page
def get_book_information(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  universal_product_code = soup.find("th", string="UPC").find_next("td").string
  title = soup.find("h1").string
  price_including_tax = soup.find("th", string="Price (incl. tax)").find_next("td").string.encode('utf-8').decode('utf-8')
  price_excluding_tax = soup.find("th", string="Price (excl. tax)").find_next("td").string.encode('utf-8').decode('utf-8')
  number_available = soup.find("th", string="Availability").find_next("td").string
  product_description = soup.find("h2", string="Product Description").find_next("p").string
  category = soup.find("ul", class_="breadcrumb").find_all("a")[2].string
  review_rating = soup.find("p", class_="star-rating").get("class")[1]
  image_url = soup.find("img").get("src").replace("../..", "https://books.toscrape.com")
  return url, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url

# Ecriture des infos dans un fichier CSV

with open("book_info.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"])
    writer.writerow(get_book_information(url))


## Etape 2 _ Récupération des infos de la page d'une catégorie

# Récupration de la liste des liens des catégories

url2 = "https://books.toscrape.com/catalogue/category/books_1/index.html"

response2 = requests.get(url2)
soup2 = BeautifulSoup(response2.text, "html.parser")
listCategories = soup2.find("ul", class_="nav nav-list").li.ul.find_all("a")
listTextCategories = [a.text.strip() for a in listCategories]
listLink = [a.get("href").replace("../", "https://books.toscrape.com/catalogue/category/") for a in listCategories]

# Récupération des infos de chaque livre de chaque catégorie

def get_books_information(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  books = soup.find_all("h3")
  books_links = [a.find("a").get("href").replace("../../../", "https://books.toscrape.com/catalogue/") for a in books]
  try:
    next_page = url.replace("index.html", soup.find("li", class_="next").a.get("href"))
    books_links += get_books_information(next_page)
  except AttributeError:
    pass
  return books_links

# Enregistrement des infos dans un fichier CSV
# Fonction pour enregister les infos de la catégorie de rang i

def write_books_information(category, books_links):
  with open(f"book_{category}.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"])
    for book in books_links:
      print(book)
      writer.writerow(get_book_information(book))


write_books_information(listTextCategories[1],get_books_information(listLink[1]))