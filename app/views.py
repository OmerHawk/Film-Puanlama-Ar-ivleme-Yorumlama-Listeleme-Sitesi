from flask import Blueprint, render_template

# Blueprint, uygulamanın bir parçası demek
views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>Proje düzenlendi. Arda</h1>"

# İleride ekleyeceğin sayfaları buraya yazacaksın.