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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
