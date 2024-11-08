# 🎬 Movie Rating Prediction Project 📊

## Overview
This project is focused on building a system to predict movie ratings using different machine learning models. The goal is to explore various models and data preprocessing techniques to find the best-performing algorithm for predicting how much a user would like a movie. The project utilizes different data sources, such as movie metadata and ratings, to train the models.

The project is implemented in Python using libraries such as `pandas`, `numpy`, `scikit-learn`, and others. It involves steps like data cleaning (cleaning the features e.g., categorical to numerical values), feature engineering, model training, evaluation, and prediction.

## Features
- **Data Preprocessing**: Cleans and transforms raw movie data into usable formats.
- **Feature Engineering**: Creates new features from the existing data (e.g., runtime normalization, box office adjustments, genre encoding).
- **Dimensionality Reduction (PCA)**: Applies Principal Component Analysis to reduce the dimensionality of features and improve model performance.
- **Model Training & Evaluation**: Trains and compares various regression models (e.g., Ridge, Lasso, Random Forest, KNN, SVR, Gradient Boosting, and more.).
- **Prediction Pipeline**: Uses the trained models to predict ratings for new movies based on unseen data.
- **Visualization**: Provides PCA visualizations to understand the variance explained by different components.

## Getting Started
### Prerequisites
Make sure you have the following libraries installed:

```bash
pip install numpy pandas scikit-learn requests matplotlib openpyxl
```

# Notes for myself.

`C:\Users\simon\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\pyinstaller --onefile --windowed --icon=icon.ico add_movie_gui.py`

- Before deciding, it’s helpful to take a quick look at your data distribution. Even though it’s subjective, you can still visualize the distribution to get an idea of its shape. You can use a histogram or summary statistics to understand whether your data is skewed or if there are any outliers.

- `movies_data['metacritic_cleaned'].hist(bins=20)`
- `print(movies_data['metacritic_cleaned'].describe())`
