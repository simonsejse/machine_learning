from sklearn.preprocessing import MultiLabelBinarizer
import sys
import pandas as pd
import os
import requests
from CTkMessagebox import CTkMessagebox
from sklearn.linear_model import Ridge
import customtkinter as ctk
from PIL import Image, ImageTk
from io import BytesIO
import numpy as np


# Predicted Rating: 6.34

api_key = "f182ce56"


class UIUtil:
    @staticmethod
    def fetch_poster_image(poster_url):
        """Fetch and resize the movie poster image for display."""
        try:
            response = requests.get(poster_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 300), Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(
                light_image=img, dark_image=img, size=(200, 300))
            return ctk_image
        except Exception as e:
            print(f"Error fetching poster: {e}")
            return None


class MovieDataUtil:
    mlb_genre = MultiLabelBinarizer()
    mlb_writer = MultiLabelBinarizer()
    mlb_actor = MultiLabelBinarizer()
    box_office_median = 0.0
    feature_columns = []  # Store feature columns for consistency

    @staticmethod
    def load_and_clean_movie_data(file_path='movie_db_staging.xlsx'):
        """Load and clean movie data from the specified Excel file."""
        try:
            file_path = "movie_db_prod.xlsx" if getattr(
                sys, 'frozen', False) else file_path
            movies_data = pd.read_excel(file_path)
            X, Y = MovieDataUtil.clean_movie_data(movies_data)
            MovieDataUtil.feature_columns = X.columns.tolist()  # Store feature columns
            return X, Y
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except pd.errors.EmptyDataError:
            print("Error: No data found in the provided Excel file.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None, None

    @staticmethod
    def clean_movie_data(movies_data):
        """Clean and transform movie data into a usable format."""
        # Convert 'Year' and 'IMDB Rating' columns to numeric
        movies_data['Year'] = pd.to_numeric(
            movies_data['Year'], errors='coerce')
        movies_data['IMDB Rating'] = pd.to_numeric(
            movies_data['IMDB Rating'], errors='coerce')

        # One-hot encode genres, writers, actors, and directors
        genre_df = MovieDataUtil.encode_column(
            movies_data, 'Genre', MovieDataUtil.mlb_genre)
        writer_df = MovieDataUtil.encode_column(
            movies_data, 'Writer', MovieDataUtil.mlb_writer)
        actor_df = MovieDataUtil.encode_column(
            movies_data, 'Actors', MovieDataUtil.mlb_actor)
        director_encoded = pd.get_dummies(
            movies_data['Director'], prefix='Director')

        # Combine all encoded data with the original DataFrame
        movies_data = pd.concat(
            [movies_data, genre_df, writer_df, actor_df, director_encoded], axis=1)

        # Clean runtime and box office columns
        movies_data['Runtime_cleaned'] = movies_data['Runtime'].apply(
            lambda x: float(x.split()[0]) if isinstance(x, str) else None)
        movies_data['BoxOffice_cleaned'] = pd.to_numeric(movies_data['Box Office'].replace(
            {'\$': '', ',': '', 'N/A': None}, regex=True), errors='coerce').fillna(MovieDataUtil.box_office_median)

        MovieDataUtil.box_office_median = movies_data['BoxOffice_cleaned'].median(
        )

        # Clean additional features like Rotten Tomatoes, Metacritic, imdbVotes
        movies_data['Rottentomatoes_cleaned'] = movies_data['Rotten Tomatoes Critic Score'].replace(
            {'%': ''}, regex=True).astype(float)
        movies_data['Metacriticscore_cleaned'] = pd.to_numeric(
            movies_data['Metacritic Score'], errors='coerce')
        movies_data['imdbVotes_cleaned'] = pd.to_numeric(
            movies_data['imdbVotes'].replace({',': ''}, regex=True), errors='coerce')

        # Define features (X) and target variable (Y)
        feature_columns = ['Year', 'IMDB Rating', 'Rottentomatoes_cleaned', 'Metacriticscore_cleaned', 'imdbVotes_cleaned',
                           'Runtime_cleaned', 'BoxOffice_cleaned'] \
            + list(genre_df.columns) + list(writer_df.columns) + \
            list(actor_df.columns) + list(director_encoded.columns)

        X = movies_data[feature_columns].dropna()
        Y = movies_data['Final Liking'].replace({'': np.nan, ',': '.'}, regex=True).astype(float).dropna() \
            if 'Final Liking' in movies_data.columns else None

        return X, Y

    @staticmethod
    def encode_column(movies_data, column_name, mlb):
        """Split and one-hot encode multi-label columns like genres, writers, and actors."""
        movies_data[f'{column_name}_list'] = movies_data[column_name].apply(
            lambda x: x.split(', ') if isinstance(x, str) else [])
        encoded = mlb.fit_transform(movies_data[f'{column_name}_list'])
        return pd.DataFrame(encoded, columns=mlb.classes_)

    @staticmethod
    def build_movie_data(movie_info):
        """Build movie data from raw input, cleaning and preparing features for prediction."""
        new_movie_data = pd.DataFrame([movie_info])

        # One-hot encode genres, writers, actors, and director with proper prefixes
        genre_df = MovieDataUtil.transform_column(
            new_movie_data, 'Genre', MovieDataUtil.mlb_genre, prefix='Genre')
        writer_df = MovieDataUtil.transform_column(
            new_movie_data, 'Writer', MovieDataUtil.mlb_writer, prefix='Writer')
        actor_df = MovieDataUtil.transform_column(
            new_movie_data, 'Actors', MovieDataUtil.mlb_actor, prefix='Actor')
        director_encoded = pd.get_dummies(
            new_movie_data['Director'], prefix='Director')

        # Combine the new movie data with one-hot encoded genres, writers, actors, and director
        new_movie_data = pd.concat(
            [new_movie_data, genre_df, writer_df, actor_df, director_encoded], axis=1)

        # Clean runtime and box office columns
        new_movie_data['Runtime_cleaned'] = new_movie_data['Runtime'].apply(
            lambda x: float(x.split()[0]) if isinstance(x, str) else None)

        new_movie_data['BoxOffice_cleaned'] = pd.to_numeric(
            new_movie_data['Box Office'].replace(
                {'\$': '', ',': '', 'N/A': None}, regex=True),
            errors='coerce').fillna(MovieDataUtil.box_office_median)

        # Ensure the DataFrame has the same columns as the training data
        new_movie_data = new_movie_data.reindex(
            columns=MovieDataUtil.feature_columns, fill_value=0)

        return new_movie_data.values

    @staticmethod
    def transform_column(new_movie_data, column_name, mlb, prefix):
        """Transform multi-label columns for prediction and add prefix to avoid column duplication."""
        new_movie_data[f'{column_name}_list'] = new_movie_data[column_name].apply(
            lambda x: x.split(', ') if isinstance(x, str) else [])
        encoded = mlb.transform(new_movie_data[f'{column_name}_list'])
        return pd.DataFrame(encoded, columns=[f"{prefix}_{cls}" for cls in mlb.classes_])

    @staticmethod
    def predict_movie_rating(movie_title, api_key):
        """Predict the rating for a movie using movie_title and return the predicted rating and movie info."""
        movie_info = MovieDataUtil.fetch_movie_info(movie_title, api_key)

        if "Error" in movie_info:
            CTkMessagebox(
                title="Error", message=movie_info["Error"], icon="cancel")
            return None

        X, Y = MovieDataUtil.load_and_clean_movie_data()
        if X is None or Y is None:
            CTkMessagebox(
                title="Error", message="An error occurred while loading movie data.", icon="cancel")
            return None

        # Train the model
        model = Ridge(alpha=2.0)
        model.fit(X, Y)

        # Build data for the new movie and predict
        X_new = MovieDataUtil.build_movie_data(movie_info)
        predicted_rating = model.predict(X_new)
        return predicted_rating[0], movie_info

    @staticmethod
    def fetch_movie_info(movie_title_or_id, api_key):
        """Fetch movie information from OMDb API."""
        url = f"http://www.omdbapi.com/?{'i' if movie_title_or_id.startswith('tt') else 't'}={movie_title_or_id}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()

        if data['Response'] == 'True':
            return {
                "Movie Title": data.get("Title", ""),
                "Year": data.get("Year", ""),
                "Rated": data.get("Rated", ""),
                "Released": data.get("Released", ""),
                "Runtime": data.get("Runtime", ""),
                "Genre": data.get("Genre", ""),
                "Director": data.get("Director", ""),
                "Writer": data.get("Writer", ""),
                "Actors": data.get("Actors", ""),
                "Plot": data.get("Plot", ""),
                "Language": data.get("Language", ""),
                "Country": data.get("Country", ""),
                "Poster": data.get("Poster", ""),
                "IMDB Rating": data.get("imdbRating", ""),
                "Rotten Tomatoes Critic Score": next(
                    (rating['Value'] for rating in data['Ratings'] if rating['Source'] == 'Rotten Tomatoes'), ""),
                "Metacritic Score": data.get("Metascore", ""),
                "Box Office": data.get("BoxOffice", ""),
                "imdbVotes": data.get("imdbVotes", ""),
                "imdbID": data.get("imdbID", ""),
                "Type": data.get("Type", ""),
                "DVD Release": data.get("DVD", ""),
                "Amount of Humor": "",
                "Final Liking": ""
            }
        else:
            return {"Error": data.get("Error", "Movie not found")}
