# Script d'entraînement (train_model.py)

import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

# Dossier contenant les données d'entraînement
training_data_dir = "/Users/alexandrelaroumet/Dropbox/PERSO/ALEXANDRE/Script/Ai_Image_Classifier/TrainingFolder"

# Préparation des données

datagen = ImageDataGenerator(rescale=1.0/255, validation_split=0.2)

train_generator = datagen.flow_from_directory(
    training_data_dir,
    target_size=(150, 150),  # Taille des images
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = datagen.flow_from_directory(
    training_data_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Définition du modèle CNN

num_classes = len(train_generator.class_indices)

model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dense(num_classes, activation='softmax')  # Nombre de classes dynamiques
])

# Compilation et entraînement du modèle

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    epochs=10,  # Ajuste le nombre d'époques selon besoin
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size
)

# Sauvegarde du modèle
model.save('rank_model.h5')

print("Modèle sauvegardé sous 'rank_model.h5'")

