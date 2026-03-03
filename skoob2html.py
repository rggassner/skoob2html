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
    """
    Extract the filename component from a given URL.

    This function parses the provided URL and returns the basename
    of its path component. It is typically used to derive a local
    filename when downloading remote resources (e.g., book cover
    images), ensuring the saved file keeps its original name.

    Args:
        url (str): A full URL pointing to a remote resource.

    Returns:
        str: The filename extracted from the URL path. If the URL
        does not contain a valid path or filename, an empty string
        may be returned.
    """
    pfilename = urlparse(url)
    bfilename=os.path.basename(pfilename.path)
    return bfilename

def get_books(user_id):
    """
    Retrieve all books from a Skoob user's bookcase via the public API.

    This function performs two HTTP requests:
    1. An initial request to obtain pagination metadata, specifically
       the total number of books in the user's bookcase.
    2. A second request using that total as the limit parameter to
       retrieve the complete list of books in a single response.

    Args:
        user_id (str): The unique identifier of the Skoob user whose
            bookcase data should be fetched.

    Returns:
        list: A list of dictionaries representing the books returned
        by the API under the "response" field. Each dictionary contains
        metadata such as edition information, ranking, reading status,
        and other related attributes.

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If the response body is not valid JSON.
        KeyError or AttributeError: If expected JSON fields (e.g.,
        "paging" or "response") are missing from the API response.
    """
    api = "{}/{}/{}".format(BASE_URL, "v1/bookcase/books", user_id)
    print("Request to {}".format(api))

    user = requests.get(api)
    total = user.json().get("paging").get("total")
    total_api = "{}/shelf_id:0/page:1/limit:{}".format(api, total)

    books_json = requests.get(total_api).json().get("response")
    return books_json

def save_html(data, filename="skoob.html"):
    """
    Generate an HTML file containing a table representation of book data.

    This function creates a simple HTML document with a bordered table,
    where each row corresponds to a book and each column represents a
    specific attribute (e.g., title, status, author, ranking, etc.).
    The last column displays the book cover as an <img> tag, using the
    locally stored filename derived from the cover URL.

    Args:
        data (list[list]): A list of book records, where each record is
            a list containing the following fields in order:
            [title, status, author, ranking, favorite, publisher,
             pages, year, cover_url].
        filename (str, optional): The name of the output HTML file.
            Defaults to "skoob.html".

    Returns:
        None

    Side Effects:
        - Creates or overwrites the specified HTML file.
        - References image files inside the COVERS_FOLDER directory.

    Notes:
        - The function assumes that each inner list contains exactly
          nine elements and that the last element is a valid cover URL.
        - No HTML escaping or validation is performed on the data.
    """
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
    """
    Transform raw Skoob API response data into a simplified list structure.

    This function extracts relevant fields from the original JSON response
    returned by the Skoob API and converts each book entry into a flat list
    format suitable for HTML export or further processing.

    For each book, it retrieves nested edition ("edicao") data and builds
    a list with the following fields in order:
        [title, reading_status, author, ranking, favorite,
         publisher, pages, year, large_cover_url]

    Args:
        data (list[dict]): A list of dictionaries representing books
            as returned by the Skoob API "response" field.

    Returns:
        list[list]: A list of simplified book records, where each inner
        list contains selected attributes extracted from the original
        JSON structure.

    Raises:
        KeyError: If expected keys such as 'edicao', 'titulo', 'autor',
        or others are missing from the input data.
    """    
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
