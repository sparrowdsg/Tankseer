import cv2
import numpy as np
import tensorflow as tf
import os 

cwd = os.getcwd()

model_path = cwd + "/model/model.keras"

### EXECUTION ###########################################################

model = tf.keras.models.load_model(model_path)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if True:
        # Resize frame to the size expected by the model
        input_img = cv2.resize(frame, (240, 180))
        
        # Preprocess the frame
        input_img = np.expand_dims(input_img, axis=0)
        input_img = input_img / 255.0  # Normalize
        
        # Perform inference
        predictions = model.predict(input_img)

        # Get the predicted class
        predicted_class = np.argmax(predictions)
        
        # Get the class label
        class_label = classes[predicted_class]

        # Craft message for the viewer
        if predictions[0][0] > 0.5 and predictions[0][0] > predictions[0][1]:
            message = 'TANK ' + str(int(predictions[0][0] * 100)) + '%'

        else:
            message = 'NOT TANK'

        # Display the result
        cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Object Detection', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()