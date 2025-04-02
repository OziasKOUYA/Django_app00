import MySQLdb

from django.shortcuts import render, redirect

def get_connection():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        password="",
        database="django_db"
        
    )
