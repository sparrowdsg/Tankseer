import cv2
import numpy as np
import os
import tensorflow as tf
import sys
import random
import os

cwd = os.getcwd()

image_folder = cwd + "/renders"         # Where to save pictures
model_path = cwd + "/model/model.keras" #Where to save the model
train_epochs = 10                       # How many epochs to train the model for

### EXECUTION ###########################################################

# Function to load and preprocess images
def preprocess_images(image_folder):
    images = []
    labels = []
    imglist = os.listdir(image_folder)
    for filename in imglist:
        if filename.endswith(".png") or filename.endswith(".bmp") or filename.endswith(".jpg"):
            try:
                img = cv2.imread(os.path.join(image_folder, filename))
                img = cv2.resize(img, (240, 180), interpolation=cv2.INTER_AREA)  # Resize image to a fixed size
                img = img.astype(np.float32) / 255.0  # Normalize pixel values to [0, 1]

                if(filename.split("_")[1].startswith('tank')):
                    labels.append([1, 0])  
                else:
                    labels.append([0, 1])

                images.append(img)
                if(len(images)%100 == 0):
                    print(str(len(images)) + '/' + str(len(imglist)) + ' completed')
            except: pass

    print('Shuffling sets...')
    # Combine the two lists into pairs
    combined_lists = list(zip(images, labels))

    # Shuffle the combined pairs
    random.shuffle(combined_lists)

    # Unzip the shuffled pairs back into separate lists
    images, labels = zip(*combined_lists)

    return np.array(images), np.array(labels)

# Load and preprocess images
print('Preprocessing images...')
images, labels = preprocess_images(image_folder)

# Split data into training and validation sets
print('Splitting set...')
split_ratio = 0.9
split_idx = int(len(images) * split_ratio)
train_images, val_images = images[:split_idx], images[split_idx:]
train_labels, val_labels = labels[:split_idx], labels[split_idx:]

print('Building model...')
model = tf.keras.models.Sequential([
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(240, 180, 3)),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(2, activation='sigmoid')])

print('Compiling model...')
model.compile(optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'])

print('Starting training...')
model.fit(train_images, train_labels, epochs = train_epochs, batch_size=16)
model.save(model_path)
model.evaluate(val_images, val_labels)