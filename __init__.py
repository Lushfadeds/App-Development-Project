from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('homepage.html')


if __name__ == '__main__':
    app.run(debug=True)
