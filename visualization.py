import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from app import Destination, app
import os
import joblib

def generate_visualizations():
    with app.app_context():
        # Fetch data from database
        destinations = Destination.query.all()
        
        # Prepare data for visualization
        data = []
        for d in destinations:
            budget = {'Low': 0, 'Medium': 1, 'High': 2}.get(d.budget_category, 1)
            climate = {'Tropical': 0, 'Savanna': 1, 'Arid': 2, 'Temperate': 3}.get(d.climate, 1)
            rating = d.rating if d.rating is not None else 0
            data.append({
                'id': d.id,
                'name': d.name,
                'budget': budget,
                'climate': climate,
                'rating': rating,
                'budget_category': d.budget_category,
                'climate_type': d.climate
            })

        df = pd.DataFrame(data)
        
        # Load the trained model and clusters
        model = joblib.load('kmeans_model.pkl')
        scaler = joblib.load('scaler.pkl')
        clusters_df = pd.read_csv('clusters.csv')
        
        # Add cluster information to the dataframe
        df = df.merge(clusters_df, on='id')
        
        # Create visualizations directory
        os.makedirs('static/visualizations', exist_ok=True)
        
        # 1. Budget vs Rating by Cluster
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='budget', y='rating', hue='cluster', style='budget_category', s=100)
        plt.title('Destination Clusters: Budget vs Rating')
        plt.xlabel('Budget Category (0=Low, 1=Medium, 2=High)')
        plt.ylabel('Rating')
        plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('static/visualizations/budget_rating_clusters.png')
        plt.close()
        
        # 2. Climate vs Rating by Cluster
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='climate', y='rating', hue='cluster', style='climate_type', s=100)
        plt.title('Destination Clusters: Climate vs Rating')
        plt.xlabel('Climate Type (0=Tropical, 1=Savanna, 2=Arid, 3=Temperate)')
        plt.ylabel('Rating')
        plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('static/visualizations/climate_rating_clusters.png')
        plt.close()
        
        # 3. 3D Visualization
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        scatter = ax.scatter(df['budget'], df['climate'], df['rating'],
                           c=df['cluster'], cmap='viridis',
                           s=100)
        
        ax.set_xlabel('Budget Category')
        ax.set_ylabel('Climate Type')
        ax.set_zlabel('Rating')
        plt.title('3D Visualization of Destination Clusters')
        plt.colorbar(scatter, label='Cluster')
        plt.tight_layout()
        plt.savefig('static/visualizations/3d_clusters.png')
        plt.close()
        
        # Generate cluster statistics
        cluster_stats = df.groupby('cluster').agg({
            'budget': ['mean', 'count'],
            'climate': 'mean',
            'rating': 'mean'
        }).round(2)
        
        cluster_stats.columns = ['Avg Budget', 'Count', 'Avg Climate', 'Avg Rating']
        cluster_stats.to_csv('static/visualizations/cluster_statistics.csv')
        
        print("Visualizations generated successfully!")

if __name__ == "__main__":
    generate_visualizations()