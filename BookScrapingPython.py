import csv
import requests
import os
from bs4 import BeautifulSoup

validCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
def cleanName(name):
  return ''.join(c for c in name if c in validCharacters)

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
  try :
    product_description = soup.find("h2", string="Product Description").find_next("p").string
  except :
    product_description = "No description available"
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
  if soup.find("li", class_="next"):
    next_page = url.replace(url.split("/")[-1], soup.find("li", class_="next").a.get("href"))
    books_links += get_books_information(next_page)
  return books_links

# Enregistrement des infos dans un fichier CSV
# Fonction pour enregister les infos de la catégorie de rang i

def write_books_information(category, books_links):
  category = cleanName(category)
  with open(f"book_{category}.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"])
    for book in books_links:
      writer.writerow(get_book_information(book))

category_index = 4
#write_books_information(listTextCategories[category_index],get_books_information(listLink[category_index]))


## Etape 3 _ Récupération des images

# Récupération de l'image d'un livre et enregistrement dans un fichier

url2 = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

def getBookImage(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  bookImage = soup.find("img").get("src").replace("../..", "https://books.toscrape.com")
  bookCategory = soup.find("ul", class_="breadcrumb").find_all("a")[2].string
  bookTitle = soup.find("h1").string
  response = requests.get(bookImage)
  if not os.path.exists(f"images/{cleanName(bookCategory)}"):
    os.makedirs(f"images/{cleanName(bookCategory)}")
  with open(f"images/{cleanName(bookCategory)}/{cleanName(bookTitle)}.jpg", "wb") as img_file:
    img_file.write(response.content)

################################################ getBookImage(url2)

## Etaoe 4 _ Récupération des infos de tous les livres par catégorie

# Récupération des infos des livres par categorie + images de tous les livres par catégorie

def move_csv_to_folder(category):
  os.rename(f"book_{cleanName(category)}.csv", f"images/{cleanName(category)}/book{cleanName(category)}.csv")

def get_all_info():
  for i in range(len(listTextCategories)):
    print(listTextCategories[i])
    write_books_information(listTextCategories[i],get_books_information(listLink[i]))
    for book in get_books_information(listLink[i]):
      getBookImage(book)
    move_csv_to_folder(listTextCategories[i])

get_all_info()