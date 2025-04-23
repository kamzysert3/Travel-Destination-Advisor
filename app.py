from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from services.api_service import TravelAPI
import re
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

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

def train_kmeans_model():
    destinations = Destination.query.all()

    if not destinations:
        return None, None, None

    data = []
    for d in destinations:
        try:
            budget = {'Low': 0, 'Medium': 1, 'High': 2}.get(d.budget_category, 1)
            climate = {'Tropical': 0, 'Savannah': 1, 'Arid': 2, 'Temperate': 3}.get(d.climate, 1)
            rating = d.rating if d.rating is not None else 0
            data.append({'id': d.id, 'budget': budget, 'climate': climate, 'rating': rating})
        except:
            continue

    df = pd.DataFrame(data)
    scaler = StandardScaler()
    X = scaler.fit_transform(df[['budget', 'climate', 'rating']])
    model = KMeans(n_clusters=5, random_state=42)
    model.fit(X)
    df['cluster'] = model.labels_

    joblib.dump(model, 'kmeans_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    df[['id', 'cluster']].to_csv('clusters.csv', index=False)

    return model, scaler, df[['id', 'cluster']]

def get_user_cluster(user_prefs):
    if not os.path.exists('kmeans_model.pkl') or not os.path.exists('scaler.pkl'):
        train_kmeans_model()

    model = joblib.load('kmeans_model.pkl')
    scaler = joblib.load('scaler.pkl')

    user_vector = pd.DataFrame([{
        'budget': {'Low': 0, 'Medium': 1, 'High': 2}.get(user_prefs['budget'], 1),
        'climate': {'Tropical': 0, 'Savannah': 1, 'Arid': 2, 'Temperate': 3}.get(user_prefs['climate'], 1),
        'rating': float(user_prefs['rating'])
    }])
    X_user = scaler.transform(user_vector)
    return model.predict(X_user)[0]


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1

    cluster = get_user_cluster(user_prefs)
    cluster_df = pd.read_csv('clusters.csv')
    cluster_ids = cluster_df[cluster_df['cluster'] == cluster]['id'].tolist()

    destinations = Destination.query.all()

    cluster_dests = []
    other_dests = []

    for dest in destinations:
        dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
        price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
        dest.price = "NGN {:,}".format(price) if price else dest.price
        dest.score = calculate_score(dest, user_prefs)
        # Separate cluster and non-cluster
        if dest.id in cluster_ids:
            cluster_dests.append(dest)
        else:
            other_dests.append(dest)

    # Sort both lists by score
    cluster_dests.sort(key=lambda d: d.score, reverse=True)
    other_dests.sort(key=lambda d: d.score, reverse=True)

    # Merge results: cluster ones first
    sorted_destinations = cluster_dests + other_dests

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

@app.route('/suggest', methods=['GET', 'POST'])
def suggest_destinations():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1
    budget = request.form.get('budget') 
    weather = request.form.get('weather') 
    rating = request.form.get('rating')

    filter_data = {
        'budget': budget if budget else user_prefs['budget'],
        'climate': weather if weather else user_prefs['climate'],
        'rating': rating if rating else user_prefs['rating'],
    }

    try:
        cluster = get_user_cluster(filter_data)
        cluster_df = pd.read_csv('clusters.csv')
        cluster_ids = cluster_df[cluster_df['cluster'] == cluster]['id'].tolist()

        destinations = Destination.query.filter(Destination.id.in_(cluster_ids)).all()

        for dest in destinations:
            dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
            price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
            dest.price = "NGN {:,}".format(price) if price else dest.price
            dest.score = calculate_score(dest, filter_data)  # Now every result is relevant by cluster

    except Exception as e:
        print(f"Clustering error: {e}")
        destinations = []

    sorted_destinations = sorted(destinations, key=lambda d: d.rating or 0, reverse=True)
    total = len(sorted_destinations)
    paginated_destinations = sorted_destinations[(page - 1) * per_page : page * per_page]

    return render_template(
        'index.html',
        destinations=paginated_destinations,
        page=page,
        total_pages=(total + per_page - 1) // per_page,  # Ceiling division
        filtered=True,  # Indicate that this is a filtered result
        form_data={
            'budget': budget if budget else None,
            'climate': weather if weather else None,
            'rating': rating if rating else None,
        }
    )


@app.route('/search', methods=['GET', 'POST'])
def search_destinations():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1
    search_term = request.form.get('search_term')

    try:
        cluster = get_user_cluster(user_prefs)
        cluster_df = pd.read_csv('clusters.csv')
        cluster_ids = cluster_df[cluster_df['cluster'] == cluster]['id'].tolist()

        
        destinations = Destination.query.filter(
            (Destination.name.ilike(f'%{search_term}%')) |
            (Destination.city.ilike(f'%{search_term}%'))
        ).all()

        cluster_dests = []
        other_dests = []

        for dest in destinations:
            dest.name = re.sub(r'^\s*\d+[\.\-\s]*', '', dest.name)
            price = int(dest.price.replace("NGN", "").replace(",", "").strip()) if dest.price else dest.price
            dest.price = "NGN {:,}".format(price) if price else dest.price
            dest.score = calculate_score(dest, user_prefs)
            # Separate cluster and non-cluster
            if dest.id in cluster_ids:
                cluster_dests.append(dest)
            else:
                other_dests.append(dest)

        # Sort both lists by score
        cluster_dests.sort(key=lambda d: d.score, reverse=True)
        other_dests.sort(key=lambda d: d.score, reverse=True)

        # Merge results: cluster ones first
        sorted_destinations = cluster_dests + other_dests

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
        if not os.path.exists('clusters.csv'):
            train_kmeans_model()
    app.run(debug=True)