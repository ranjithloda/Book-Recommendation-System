#!/usr/bin/python3
import csv

def get_book_by_id(book_id):
    """ 
        function gets the id of a specific book based on the id assigned to that book
    """
    import csv

def get_book_by_id(book_id):
    """ 
    function gets the id of a specific book based on the id assigned to that book
    """
    with open('books_data.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] == book_id:
                return row


