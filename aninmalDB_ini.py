# upload data (animal figures and metadata) to MongonDB
# and retrive them
# animal data set: https://www.kaggle.com/datasets/iamsouravbanerjee/animal-image-dataset-90-different-animals?resource=download

from tkinter import *
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import pymongo
import gridfs
import os
from PIL import Image, ImageTk
import io

#print("Current working directory:", os.getcwd())

# Connect to MongoDB
path = os.getenv("MONGODB_VARIABLE")
#print(f"mogodb path: {path}")

client = pymongo.MongoClient(path)
#client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client.animal_database
fs = gridfs.GridFS(db)

data_path = "/home/bo/Desktop/AI_Utveckling/PythonMarsAssign2025/animal_dataset"

# Sample data: List of figures with text metadata

def upload_figures_with_metadata(folder_path):
    client = pymongo.MongoClient(path)
    #client = pymongo.MongoClient("mongodb://localhost:27017/")

    #db = client.figure_database
    fs = gridfs.GridFS(db)

    extenstions = ('.jpg', '.jpeg', '.png')
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(extenstions):
            print(os.path.splitext(filename)[0])

folder_path = "/home/bo/Desktop/AI_Utveckling/PythonMarsAssign2025/animal_dataset/"

upload_figures_with_metadata(folder_path)


figures = [
    {
        "title": "bat",
        "description": "It loves the night and enjoys eating insects. What makes this creature remarkable is its ability to navigate using ultrasound!",
        "image_path": f"{data_path}/bat.jpg"
    },
    {
        "title": "bear",
        "description": "This mighty creature is incredibly strong, adores berries and honey, and does something amazing—it sleeps through the entire winter!",
        "image_path": f"{data_path}/bear.jpg"
    },
    {
        "title": "bee",
        "description": "A tiny, hardworking insect dressed in yellow and black—always buzzing from flower to flower, tirelessly making honey!",
        "image_path": f"{data_path}/bee.jpg"
    },
    {
        "title": "crab",
        "description": "This quirky creature strolls sideways, proudly waving two giant claws as it scuttles along the shore!",
        "image_path": f"{data_path}/crab.jpg"
    },
    {
        "title": "dolphin",
        "description": "This intelligent creature is as clever as you are—and it’s also the most graceful dancer in the ocean!",
        "image_path": f"{data_path}/dolphin.jpg"
    }
]

# Check if collection is non empty
collection = db['figures']

if 'figures' in db.list_collection_names():
    count = collection.count_documents({})

if count > 0:
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} documents from 'figures' collection!")


# Store each figure
for f in figures:
    with open(f["image_path"], "rb") as img_file:
        image_id = fs.put(img_file, filename=f["title"])

        # Stor metadata in regular collection
        db.figures.insert_one({
            "title": f["title"],
            "description": f["description"],
            "image_id": image_id,
            "created_at": datetime.now()
        })
            
print(f"Stored {len(figures)} figures with metadata")

# Retrieve:
# Get metadata
animal = "crab"

metadata_animal = db.figures.find_one({"title": f"{animal}"})
image_animal_name = metadata_animal["title"]
image_animal_description = metadata_animal["description"]

# Fetch image from GridFS
image_animal = fs.get(metadata_animal["image_id"]).read()


# Save to file
#with open("./bat_saved.png", "wb") as f:
#    f.write(image_data)

# Try to dispaly animal pictures in tkinter
root = tk.Tk()
root.title("")
root.geometry("700x300")

# Convert to Tkinter-compatible image
image = Image.open(io.BytesIO(image_animal))
photo = ImageTk.PhotoImage(image)

# Display image
frame = tk.Frame(root)
frame.pack(expand=True, fill='both', padx=10, pady=10)

image_label = tk.Label(frame, 
                 image=photo, 
                 pady=10)

title_label = tk.Label(frame, 
                      text=f"This a {image_animal_name}! \n {image_animal_description}",
                      font=('Arial', 12, 'bold'),
                      pady=10)
title_label.pack()

image_label.pack(expand=True)

# Keep reference to prevent garbage collection
image_label.image = photo

root.mainloop()
