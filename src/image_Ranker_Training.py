import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Dossier contenant les données d'entraînement
training_data_dir = "data/TrainingFolder"

# Préparation des données avec augmentation
datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=20,  # Rotation aléatoire jusqu'à 20 degrés
    width_shift_range=0.2,  # Translation horizontale
    height_shift_range=0.2,  # Translation verticale
    shear_range=0.2,  # Cisaillement
    zoom_range=0.2,  # Zoom aléatoire
    horizontal_flip=True,  # Retournement horizontal
    fill_mode='nearest',
    validation_split=0.2  # Séparer 20% pour la validation
)

train_generator = datagen.flow_from_directory(
    training_data_dir,
    target_size=(512, 512),  # Taille plus grande pour les images
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = datagen.flow_from_directory(
    training_data_dir,
    target_size=(512, 512),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Chargement d'un modèle préentraîné (VGG16)
base_model = VGG16(input_shape=(512, 512, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Gèle les couches du modèle préentraîné

# Définition du modèle avec des couches additionnelles
model = models.Sequential([
    base_model,
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),  # Dropout pour éviter le sur-apprentissage
    layers.Dense(train_generator.num_classes, activation='softmax')
])

# Compilation du modèle
model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Vérifier si le dossier /results/ existe, sinon le créer
# Remplace /results par un chemin dans ton répertoire utilisateur
save_dir = 'results/'

# Vérifier si le dossier existe, sinon le créer
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Callbacks pour Early Stopping et Model Checkpoint
model_checkpoint = ModelCheckpoint(save_dir + 'best_model.keras', save_best_only=True)

# Sauvegarde du modèle final
model.save(save_dir + 'final_rank_model.keras')

# Callbacks pour Early Stopping et Model Checkpoint
early_stopping = EarlyStopping(monitor='val_loss', patience=5)
model_checkpoint = ModelCheckpoint('/results/best_model.keras', save_best_only=True)

# Entraînement du modèle
model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    epochs=50,  # Augmente le nombre d'époques
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size,
    callbacks=[early_stopping, model_checkpoint]
)

# Débloquer certaines couches du modèle pour fine-tuning
base_model.trainable = True

# Recompiler le modèle avec un learning rate plus bas pour le fine-tuning
model.compile(optimizer=Adam(learning_rate=1e-5),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Continuer l'entraînement pour fine-tuning
model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    epochs=10,  # Quelques époques supplémentaires
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size,
    callbacks=[early_stopping, model_checkpoint]
)

# Sauvegarde du modèle final dans le dossier /results/
model.save('/results/final_rank_model.keras')

print("Modèle sauvegardé sous '/results/final_rank_model.keras'")