import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil

# Charger le modèle entraîné
model = tf.keras.models.load_model('rank_model.h5', compile=False)

def predict_image_rank(img_path):
    # Charger et préparer l'image
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Prédire le rang
    predictions = model.predict(img_array)
    rank = np.argmax(predictions) + 1  # Ajouter +1 car les classes sont de 1 à num_classes

    return rank

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        rank = predict_image_rank(file_path)
        messagebox.showinfo("Résultat", f"L'image est classée au rang : {rank}")

def sort_images_by_rank():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    # Demander les ranks à trier
    selected_ranks = simpledialog.askstring("Sélection de ranks", "Entrez les ranks à trier (ex: 1,2,3):")
    if not selected_ranks:
        return

    selected_ranks = [int(rank.strip()) for rank in selected_ranks.split(",")]

    # Créer le dossier parent "rank"
    parent_folder = os.path.join(os.path.dirname(folder_path), "rank")
    os.makedirs(parent_folder, exist_ok=True)

    # Créer les sous-dossiers pour chaque rank sélectionné
    for rank in selected_ranks:
        os.makedirs(os.path.join(parent_folder, f"rank_{rank:02d}"), exist_ok=True)

    # Parcourir et trier les images
    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)
        if os.path.isfile(img_path):
            rank = predict_image_rank(img_path)
            if rank in selected_ranks:
                target_folder = os.path.join(parent_folder, f"rank_{rank:02d}")
                shutil.copy(img_path, target_folder)

    messagebox.showinfo("Tri terminé", f"Images triées par ranks dans le dossier: {parent_folder}")

# Interface graphique
root = tk.Tk()
root.title("Classement d'image IA")
root.geometry("300x200")

open_button = tk.Button(root, text="Ouvrir une image", command=open_image)
open_button.pack(pady=10)

sort_button = tk.Button(root, text="Trier les images par rank", command=sort_images_by_rank)
sort_button.pack(pady=10)

root.mainloop()
