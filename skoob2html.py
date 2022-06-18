#!/usr/bin/python3
import requests
import json
import os
from urllib.parse import urlparse
from os.path import exists

#Based on https://github.com/GuidoBR/skoober

BASE_URL = "https://www.skoob.com.br"
COVERS_FOLDER = "covers/"

def get_fname_url(url):
    pfilename = urlparse(url)
    bfilename=os.path.basename(pfilename.path)
    return bfilename

def get_books(user_id):
    api = "{}/{}/{}".format(BASE_URL, "v1/bookcase/books", user_id)
    print("Request to {}".format(api))

    user = requests.get(api)
    total = user.json().get("paging").get("total")
    total_api = "{}/shelf_id:0/page:1/limit:{}".format(api, total)

    books_json = requests.get(total_api).json().get("response")
    return books_json

def save_html(data, filename="skoob.html"):
    flag=0
    header = ["Título","Status<br>1-Lido<br>2-Quero Ler", "Autor", "Ranking", "Favorito", 
            "Editora", "Páginas", "Ano", "Capa grande"]
    html = open(filename, "w")
    html.write('<html><table border=1><tr>')
    for item in header:
        html.write('<th>{}</th>'.format(item))
    html.write('</tr>\n')
    for line in data:
        html.write('<tr>')
        count=0
        for item in line:
            if count == 8:
                html.write('<td><img src={}></td>'.format(COVERS_FOLDER+get_fname_url(item)))
            else:
                html.write('<td>{}</td>'.format(item))
            count=count+1
        html.write('</tr>\n')
    html.write('</table></html>')
    html.close()

def export_data(data):
    books = []
    for book in data:
        b = book['edicao']
        goodread_book = [b['titulo'], book['tipo'], b['autor'], book['ranking'],book['favorito'], b['editora'], book['paginas'], b['ano'], b['capa_grande']]
        books.append(goodread_book)
    return books

def retrieve_covers(all_books):
    for book in all_books:
        if not exists(COVERS_FOLDER+get_fname_url(book[8])):
            img_data = requests.get(book[8]).content
            with open(COVERS_FOLDER+get_fname_url(book[8]), 'wb') as handler:
                handler.write(img_data)

def main(user_id):
    json_books = (get_books(user_id))
    all_books = export_data(json_books)
    save_html(all_books)
    retrieve_covers(all_books)

if __name__ == "__main__":
    import sys
    argumentos = sys.argv
    
    main(argumentos[1])
