from django.shortcuts import render
import cv2
import numpy as np
from django.core.files.storage import FileSystemStorage
import os
from django.core.mail import send_mail
from keras.models import load_model





# Create your views here...
def home(request):
    if request.method=="POST" and 'video_file' in request.FILES:
        videofile =request.FILES['video_file']
        file_storage=FileSystemStorage()
        filename=file_storage.save(videofile.name,videofile)
        # video_path =file_storage.url(filename)
        video_path =os.path.join(file_storage.location,filename)
        if not os.path.exists(video_path):
            error_message = "Video file does not exist."
            return render(request, 'detection_error.html', {'error': error_message})
        
        cap= cv2.VideoCapture(video_path)
        import tensorflow as tf
        print("TensorFlow version:", tf.__version__)

        # Load the entire model (including architecture and weights)
        model = load_model('C:/Users/syamp/Desktop/fog_detection/fog_detection_project/keras_model.h5')  

        total_fog_percetage = []

        if not cap.isOpened():
            error_message="Error opening video file."
            return render(request,'detection_error.html',{'error':error_message})

        # Process each frame in the video
        while True:
            # Read a frame from the video
            ret, frame = cap.read()

            # Break the loop if the video has ended
            if not ret:
                break

                
            # Resize the frame to match the input shape of the model (224x224)
            resized_frame = cv2.resize(frame, (224, 224))

            # Normalize pixel values if necessary
            # ...

            # Make predictions using the loaded model
            fog_probability = model.predict(np.expand_dims(resized_frame, axis=0))[0, 0]


            # Set a threshold (adjust as needed)
            threshold = 0.5
            
           
            # Determine fog presence based on the threshold 
            if fog_probability > threshold:
        
                total_fog_percetage.append(fog_probability*100)
                percentage_text = f"Fog detection percentage: {fog_probability * 100:.2f}%"
                cv2.putText(frame, percentage_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                # Display fog detection message on the frame
                
                cv2.putText(frame, "Fog detected!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
               
                no_fog_percentage = 0
                # Display no fog message on the frame
                cv2.putText(frame, "No fog detected", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

             # Display the frame
            cv2.imshow('Video Frame', frame)


            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture and close any open windows
        cap.release()
        cv2.destroyAllWindows()
        
        # Calculate the average fog percentage with a check for ZeroDivisionError
        try:
            average_fog_percentage = sum(total_fog_percetage) / len(total_fog_percetage)

             #sent mail if fog percentage is more than 50%
            if  average_fog_percentage >= 50 :
                subject = 'Fog detection'
                mail_content =f'warning : fog detection percentage is {average_fog_percentage}'
                from_mail = 'fogdetectiontrial@gmail.com'
                recipient_list = ['traficunofficial@gmail.com']
                send_mail(subject, mail_content, from_mail, recipient_list)
                
                return render(request,'fog_percentage.html',{'f': average_fog_percentage })

        except ZeroDivisionError:
            print("Error: Division by zero. Unable to calculate the average.")

            return render(request,'fog_percentage.html',{'f':no_fog_percentage})
    else:
        return render(request,'home.html')
          





