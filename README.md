# Travel Destination Advisor

A smart travel recommendation system that suggests destinations based on user preferences including weather, budget, and ratings.

## Features

- Personalized destination recommendations based on user preferences
- Multi-criteria scoring system for accurate matches
- Advanced filtering options (weather, budget, rating)
- Smart clustering algorithm for similar destinations
- Paginated results with destination cards
- Search functionality for destinations and cities
- Real-time price updates and formatting

## Technologies Used

- Python 3.x
- Flask (Web Framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- scikit-learn (Machine Learning)
- Bootstrap 5 (Frontend)
- Font Awesome (Icons)

## Setup Instructions

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Initialize the database:
```bash
python seed_data.py
```

5. Access the application at `http://localhost:5000`

## Project Structure

- `app.py` - Main application file with routes and core logic
- `seed_data.py` - Database seeding script
- `services/` - API services and utilities
- `templates/` - HTML templates
- `instance/` - Instance-specific configuration
- Machine Learning Models:
  - `kmeans_model.pkl` - Trained clustering model
  - `scaler.pkl` - Data scaling model
  - `clusters.csv` - Cluster assignments

## Data Sources

The application uses various travel APIs and data sources:
- TripAdvisor API
- Custom curated destination database
- Climate data integration

## Data Flow & API Integration

### Data Collection
- Utilizes TripAdvisor API to fetch real-world destination data
- Each destination request includes:
  - Geographic location (geoId)
  - Pricing in NGN (Nigerian Naira)
  - Ratings and reviews
  - Photo URLs and destination details

### Data Processing Pipeline
1. **API Data Fetching**:
   - Destinations are fetched per city using TripAdvisor's geoId
   - Fallback mechanism implemented for API downtime
   - Data is normalized and enriched with climate information

2. **Data Transformation**:
   - Price categorization (Low/Medium/High)
   - Climate classification (Tropical/Savanna/Arid/Temperate)
   - Image URL standardization
   - Rating normalization

3. **Database Storage**:
   - SQLite database with SQLAlchemy ORM
   - Structured schema for fast querying
   - Regular updates via seed_data.py

## AI Techniques & Implementation

### Machine Learning Integration

1. **K-Means Clustering**
   - Groups similar destinations based on:
     - Budget category
     - Climate type
     - User ratings
   - Helps identify destination clusters matching user preferences
   - Implemented using scikit-learn

2. **Scoring System**
   - Multi-criteria decision making algorithm
   - Weighted scoring based on:
     - Climate match (40% weight)
     - Budget alignment (30% weight)
     - Rating threshold (30% weight)
   - Scores normalized to 0-100 scale

3. **Recommendation Engine**
   - Hybrid approach combining:
     - Content-based filtering (climate, budget)
     - Collaborative features (user ratings)
     - Cluster-based recommendations
   - Real-time preference adjustment
   - Paginated results with sorted recommendations

### Technical Implementation
- Clustering model trained on application startup
- Model persistence using joblib
- Scalable architecture for future AI enhancements
- Efficient caching of cluster assignments

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
