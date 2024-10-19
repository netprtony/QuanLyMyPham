from flask import Blueprint, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
location_collection = db['Deliveries']
location_bp = Blueprint('location_bp', __name__)