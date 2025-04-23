from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from services.api_service import TravelAPI
import re
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = TravelAPI()

user_prefs = {
    'budget': 'Medium',
    'climate': 'Tropical',
    'rating': 4.0,
}
per_page = 5

# Database Models
class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    climate = db.Column(db.String(50))
    budget_category = db.Column(db.String(20))
    info = db.Column(db.String(255))
    rating = db.Column(db.Float)
    price = db.Column(db.String(50))
    image_url = db.Column(db.String(500))

def calculate_score(destination, user_prefs):
    climate_score = 1.0 if destination.climate == user_prefs['climate'] else 0.5
    budget_score = 1.0 if destination.budget_category == user_prefs['budget'] else 0.3
    # Safely handle None rating
    if destination.rating is not None and user_prefs.get('rating') is not None:
        rating_score = user_prefs['rating'] / 5.0 if destination.rating >= user_prefs['rating'] else 0.0
    else:
        rating_score = 0.5
    # Weighted sum (adjust these weights as needed)
    score = (0.4 * climate_score + 0.3 * budget_score + 0.3 * rating_score) * 100
    return round(score, 2)


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1

    destinations = Destination.query.all()
    for dest in destinations:
        dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
        price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
        dest.price = "NGN {:,}".format(price) if price else dest.price
        dest.score = calculate_score(dest, user_prefs)

    sorted_destinations = sorted(destinations, key=lambda d: d.score, reverse=True)

    # Paginate manually (slice the sorted list)
    total = len(sorted_destinations)
    paginated_destinations = sorted_destinations[(page - 1) * per_page : page * per_page]

    return render_template(
        'index.html',
        destinations=paginated_destinations,
        page=page,
        total_pages=(total + per_page - 1) // per_page,  # Ceiling division
        filtered=False,  # Indicate that this is not a filtered result
        form_data={
            'budget': None,
            'climate': None,
            'rating': None,
        }
    )

@app.route('/suggest', methods=['POST'])
def suggest_destinations():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1
    budget = request.form.get('budget') 
    weather = request.form.get('weather') 
    rating = request.form.get('rating')

    user_prefs['budget'] = budget if budget else user_prefs['budget']
    user_prefs['climate'] = weather if weather else user_prefs['climate']
    user_prefs['rating'] = rating if rating else user_prefs['rating']

    filter_data = {
        'budget': budget,
        'climate': weather,
        'rating': rating,
    }

    try:
        destinations = Destination.query.filter(
            (Destination.budget_category == budget if budget else True) &
            (Destination.climate == weather if weather else True) &
            ((Destination.rating != None) & (Destination.rating >= float(rating)) if rating else True)
        ).all()
        for dest in destinations:
            dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
            price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
            dest.price = "NGN {:,}".format(price) if price else dest.price
            dest.score = calculate_score(dest, user_prefs)
    except Exception as e:
        print(f"Error fetching destinations: {e}")
        destinations = []

    # Sort destinations by score
    sorted_destinations = sorted(destinations, key=lambda d: d.score, reverse=True)

    # Paginate manually (slice the sorted list)
    total = len(sorted_destinations)
    paginated_destinations = sorted_destinations[(page - 1) * per_page : page * per_page]

    return render_template(
        'index.html',
        destinations=paginated_destinations,
        page=page,
        total_pages=(total + per_page - 1) // per_page,  # Ceiling division
        filtered=True,  # Indicate that this is a filtered result
        form_data=filter_data
    )


@app.route('/search', methods=['POST'])
def search_destinations():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1
    search_term = request.form.get('search_term')

    try:
        destinations = Destination.query.filter(
            (Destination.name.ilike(f'%{search_term}%')) |
            (Destination.city.ilike(f'%{search_term}%'))
        ).all()
        for dest in destinations:
            dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
            price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
            dest.price = "NGN {:,}".format(price) if price else dest.price
            dest.score = calculate_score(dest, user_prefs)
    except Exception as e:
        print(f"Search error: {e}")
        destinations = []

    # Sort destinations by score
    sorted_destinations = sorted(destinations, key=lambda d: d.score, reverse=True)

    # Paginate manually (slice the sorted list)
    total = len(sorted_destinations)
    paginated_destinations = sorted_destinations[(page - 1) * per_page : page * per_page]

    return render_template(
        'index.html',
        destinations=paginated_destinations,
        page=page,
        total_pages=(total + per_page - 1) // per_page,  # Ceiling division
        filtered=False,  # Indicate that this is not a filtered result
        form_data={
            'budget': None,
            'climate': None,
            'rating': None,
        }
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)