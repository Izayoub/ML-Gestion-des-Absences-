from Ml_gestionABS_app.models import Student
import os
import face_recognition

def register_face_encodings_from_folder():
    photo_folder = r'C:\Users\honor\PycharmProjects\Ml_gestionABS\media\students_photos'
    files = os.listdir(photo_folder)

    for file_name in files:
        file_path = os.path.join(photo_folder, file_name)

        try:
            # Charger l'image
            image = face_recognition.load_image_file(file_path)
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:
                # Si un visage est trouvé, enregistrez l'encodage
                encoding = face_encodings[0]

                # Extraire l'ID de l'étudiant à partir du nom du fichier (avant le '_')
                student_id = file_name.split('_')[0]  # Extrait l'ID avant le premier '_', par exemple '1'

                try:
                    # Récupérer l'étudiant en fonction de l'ID
                    student = Student.objects.get(student_id=student_id)
                except Student.DoesNotExist:
                    print(f"Erreur : L'étudiant avec l'ID {student_id} n'existe pas.")
                    continue  # Ignore ce fichier si l'étudiant n'existe pas

                # Convertir l'encodage en binaire et l'enregistrer dans la base de données
                student.face_encoding = encoding.tobytes()
                student.save()

                print(f"Encodage du visage pour l'étudiant {student.first_name} {student.last_name} enregistré.")
            else:
                print(f"Aucun visage trouvé dans l'image {file_name}.")

        except Exception as e:
            print(f"Erreur pour le fichier {file_name}: {e}")
