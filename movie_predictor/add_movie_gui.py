import customtkinter as ctk
from lib import MovieDataUtil, UIUtil
from CTkMessagebox import CTkMessagebox
import pandas as pd
import os
import tkinter
import sys
from openpyxl import load_workbook

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



def save_movie():
    movie_title = title_entry.get()
    aoh = aoh_entry.get()
    fl = fl_entry.get()

    # check if movie exists
    movie_exists = MovieDataUtil.does_movie_exist(movie_title)
    if movie_exists:
        CTkMessagebox(
            title="Error", message=f"Movie '{movie_title}' already exists in the database.", icon="cancel")
        return

    # Validate inputs
    if not movie_title or not aoh or not fl:
        CTkMessagebox(title="Input Error",
                      message="Please fill in all fields.", icon="warning")
        return

    # Fetch movie info
    movie_data = MovieDataUtil.fetch_movie_info(movie_title, api_key)
    if "Error" in movie_data:
        CTkMessagebox(
            title="Error", message=movie_data["Error"], icon="cancel")
        return

    movie_data["Amount of Humor"] = aoh
    movie_data["Final Liking"] = fl

    df_new = pd.DataFrame([movie_data])

    excel_file = "movie_db_staging.xlsx" if not getattr(
        sys, 'frozen', False) else "movie_db_prod.xlsx"

    if os.path.exists(excel_file):
        df_existing = pd.read_excel(excel_file)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="w") as writer:
        df_combined.to_excel(writer, index=False, sheet_name="Movie Data")

    wb = load_workbook(excel_file)
    ws = wb.active

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    wb.save(excel_file)

    CTkMessagebox(
        title="Success", message=f"Data for {movie_title} appended to '{excel_file}'", icon="check")


# Function to handle movie rating prediction
def predict_movie_rating():
    movie_title = predict_title_entry.get()

    # Simulate fetching prediction (replace with actual model prediction logic)
    predicted_rating, movie_info = MovieDataUtil.predict_movie_rating(
        movie_title, api_key)

    if predicted_rating is None:
        CTkMessagebox(
            title="Error", message="An error occurred while predicting the rating.", icon="cancel")
        return

    # Display the predicted rating
    result_entry.delete(0, ctk.END)  # Clear previous result
    result_entry.insert(0, f"Predicted Rating: {predicted_rating:.2f}")

    # Fetch and display the movie poster
    poster_url = movie_info['Poster']
    if not poster_url or poster_url == "N/A":
        return

    poster_image = UIUtil.fetch_poster_image(poster_url)
    if poster_image:
        # Re-add the poster_label to the grid before displaying the image
        poster_label.grid(row=3, column=1, columnspan=2,
                          padx=20, pady=(10, 10))
        poster_label.configure(image=poster_image)
        poster_label.image = poster_image


def reset_input_fields_search_frame():
    # Clear result entry
    result_entry.delete(0, ctk.END)

    # Clear the predict title entry
    predict_title_entry.delete(0, ctk.END)

    # Clear and remove poster image
    poster_label.configure(image=None)
    poster_label.grid_remove()  # Removes the poster_label from the grid layout entirely

    # Force the window to recalculate the size based on new content
    app.update_idletasks()


# Function to switch views (Add Movie / Predict Rating)
def show_frame(frame):
    frame.tkraise()  # Bring the selected frame to the front


# CustomTkinter window setup
# CustomTkinter window setup
app = ctk.CTk()
app.title("Movie Data Management")

# After placing all widgets, update the window size based on content
app.update_idletasks()  # Forces the window to recalculate size
# Set the minimum size to the current width and height
app.minsize(app.winfo_width(), app.winfo_height())


# Sidebar frame with menu options
sidebar_frame = ctk.CTkFrame(app, width=140, corner_radius=0)
sidebar_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")
sidebar_frame.grid_rowconfigure(4, weight=1)

logo_label = ctk.CTkLabel(
    sidebar_frame, text="Movie Data Manager", font=ctk.CTkFont(size=20, weight="bold"))
logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

info_label = ctk.CTkLabel(
    sidebar_frame, text="Made by:\ngithub.com/simonsejse", anchor="w")
info_label.grid(row=1, column=0, padx=20, pady=10)

# Menu buttons to switch between "Add Movie" and "Predict Rating"
add_movie_button = ctk.CTkButton(
    sidebar_frame, text="Add New Movie", command=lambda: show_frame(add_movie_frame))
add_movie_button.grid(row=2, column=0, padx=20, pady=10)

predict_rating_button = ctk.CTkButton(
    sidebar_frame, text="Predict Movie Rating", command=lambda: show_frame(predict_rating_frame))
predict_rating_button.grid(row=3, column=0, padx=20, pady=10)

# Frame for adding a new movie
add_movie_frame = ctk.CTkFrame(app)
add_movie_frame.grid(row=0, column=1, columnspan=3, rowspan=10, sticky="nsew")

title_label = ctk.CTkLabel(add_movie_frame, text="Movie Title")
title_label.grid(row=0, column=1, padx=20, pady=(20, 5))
title_entry = ctk.CTkEntry(add_movie_frame, width=200)
title_entry.grid(row=0, column=2, padx=20, pady=(20, 5))

aoh_label = ctk.CTkLabel(add_movie_frame, text="Amount of Humor (1-10)")
aoh_label.grid(row=1, column=1, padx=20, pady=(5, 5))
aoh_entry = ctk.CTkEntry(add_movie_frame, width=200)
aoh_entry.grid(row=1, column=2, padx=20, pady=(5, 5))

fl_label = ctk.CTkLabel(add_movie_frame, text="Final Liking (1-10)")
fl_label.grid(row=2, column=1, padx=20, pady=(5, 5))
fl_entry = ctk.CTkEntry(add_movie_frame, width=200)
fl_entry.grid(row=2, column=2, padx=20, pady=(5, 5))

submit_button = ctk.CTkButton(
    add_movie_frame, text="Submit Data", command=save_movie)
submit_button.grid(row=4, column=1, columnspan=2, padx=20, pady=30)

# Frame for predicting movie rating
predict_rating_frame = ctk.CTkFrame(app)
predict_rating_frame.grid(
    row=0, column=1, columnspan=3, rowspan=10, sticky="nsew")

predict_title_label = ctk.CTkLabel(
    predict_rating_frame, text="Enter Movie Title")
predict_title_label.grid(row=0, column=1, padx=20, pady=(20, 5))
predict_title_entry = ctk.CTkEntry(predict_rating_frame, width=200)
predict_title_entry.grid(row=0, column=2, padx=20, pady=(20, 5))

# Configure columns for equal width
predict_rating_frame.grid_columnconfigure(1, weight=1)
predict_rating_frame.grid_columnconfigure(2, weight=1)

# Search button
search_button = ctk.CTkButton(
    predict_rating_frame, text="Search", command=predict_movie_rating)
search_button.grid(row=1, column=1, padx=(10, 5), pady=(10, 10), sticky="ew")

# Clear button
clear_button = ctk.CTkButton(
    predict_rating_frame, text="Clear", command=reset_input_fields_search_frame)
clear_button.grid(row=1, column=2, padx=(5, 10), pady=(10, 10), sticky="ew")

result_entry = ctk.CTkEntry(
    predict_rating_frame, width=200)
result_entry.grid(row=2, column=1, columnspan=2, padx=20, pady=(10, 10))

# Label for poster
poster_label = ctk.CTkLabel(predict_rating_frame, text="")
poster_label.grid(row=3, column=1, columnspan=2, padx=20, pady=(10, 10))

# Show the "Add Movie" frame by default
show_frame(add_movie_frame)

# Run the application
app.mainloop()
