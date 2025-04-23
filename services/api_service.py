import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime, timedelta

load_dotenv()

class TravelAPI:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://tripadvisor16.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
        }

    def fetch_destinations(self, geoId: Optional[int] = None, page: Optional[int] = None, currency: Optional[str] = None) -> List[Dict]:
        try:
            # Get current date for check-in and check-out dates
            check_in = datetime.now().strftime("%Y-%m-%d")
            check_out = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.base_url}/api/v1/hotels/searchHotels",
                headers=self.headers,
                params={
                    "geoId": geoId,
                    "checkIn": check_in,
                    "checkOut": check_out,
                    "pageNumber": page,
                    "currencyCode": currency,
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            # Return some fallback data in case of API failure
            return 
        
    def get_fallback_data(self) -> List[Dict]:
        # Fallback data in case the API is unavailable
        return [
            {
                'name': 'Bali',
                'country': 'Indonesia',
                'climate': 'Tropical',
                'budget_category': 'Medium',
                'description': 'A beautiful island known for its beaches, temples, and rice terraces.',
                'attractions': 'Tanah Lot Temple, Ubud Monkey Forest, Tegalalang Rice Terraces',
                'best_seasons': 'April to October'
            },
            {
                'name': 'Santorini',
                'country': 'Greece',
                'climate': 'Mediterranean',
                'budget_category': 'High',
                'description': 'Famous for its stunning sunsets and white-washed buildings.',
                'attractions': 'Oia, Akrotiri, Red Beach',
                'best_seasons': 'April to June, September to October'
            },
            {
                'name': 'Banff',
                'country': 'Canada',
                'climate': 'Continental',
                'budget_category': 'Medium',
                'description': 'Known for its stunning mountain scenery and outdoor activities.',
                'attractions': 'Lake Louise, Moraine Lake, Banff National Park',
                'best_seasons': 'June to September'
            },
            {
                'name': 'Reykjavik',
                'country': 'Iceland',
                'climate': 'Arctic',
                'budget_category': 'High',
                'description': 'The capital city known for its unique architecture and vibrant culture.',
                'attractions': 'Blue Lagoon, Golden Circle, Northern Lights',
                'best_seasons': 'June to August'
            },
            {
                'name': 'Dubai',
                'country': 'UAE',
                'climate': 'Desert',
                'budget_category': 'High',
                'description': 'Famous for luxury shopping, ultramodern architecture, and a lively nightlife scene.',
                'attractions': 'Burj Khalifa, Dubai Mall, Palm Jumeirah',
                'best_seasons': 'November to March'
            },
            {
                'name': 'Marrakech',
                'country': 'Morocco',
                'climate': 'Desert',
                'budget_category': 'Medium',
                'description': 'Known for its historical medina, vibrant souks, and beautiful gardens.',
                'attractions': 'Jemaa el-Fnaa, Koutoubia Mosque, Jardin Majorelle',
                'best_seasons': 'March to May, September to November'
            }
        ]