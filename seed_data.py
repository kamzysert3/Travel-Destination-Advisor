from app import app, db, Destination
from services.api_service import TravelAPI
from instance.location_map import location_map

def get_budget_category(price_str):
    # Remove "NGN", commas, etc.
    if not price_str:
        return "Unknown"
    try:
        amount = int(price_str.replace("NGN", "").replace(",", "").strip())
        if amount < 50_000:
            return "Low"
        elif amount < 200_000:
            return "Medium"
        else:
            return "High"
    except ValueError:
        return "Unknown"

def seed_destinations():
    api = TravelAPI()
    
    destinations_data = []

    for city_key, city_data in location_map.items():
        # Fetch destinations from API for each combination
        response = api.fetch_destinations(geoId=city_data['geoId'], page=1, currency='NGN')
        # Extract actual results list
        results = response.get('data', {}).get('data', [])
        # Add city information to each destination
        for result in results:
            result['city'] = city_key
            result['climate'] = city_data['climate']
            result['budget_category'] = get_budget_category(result.get('priceForDisplay', {}))
            photos = result.get('cardPhotos', [])
            result['image_url'] = photos[0].get('sizes', {}).get('urlTemplate').replace("{width}", "800").replace("{height}", "800") if photos else None
        destinations_data.extend(results)

        

    if len(destinations_data) == 0:
        print("No data fetched from API. Please check the API or your internet connection.")
        results = api.get_fallback_data()
        destinations_data.extend(results)

    with app.app_context():
        # Clear existing data
        db.session.query(Destination).delete()
        
        # Add new destinations from API
        for dest_data in destinations_data:
            destination = Destination(
                name=dest_data.get('title'),
                city=dest_data.get('city'),
                climate=dest_data.get('climate'),
                budget_category=dest_data.get('budget_category'),
                info=dest_data.get('primaryInfo') or "No additional info",
                rating=dest_data.get('bubbleRating', {}).get('rating'),
                price=dest_data.get('priceForDisplay', {}),
                image_url=dest_data.get('image_url', None),
            )
            db.session.add(destination)
        
        db.session.commit()
        print(f"Database seeded successfully with {len(destinations_data)} destinations!")

if __name__ == '__main__':
    seed_destinations()