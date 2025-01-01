from flask import Flask

app = Flask(__name__)
app.config["DATABASE"] = "app/events.db"

from app import routes
