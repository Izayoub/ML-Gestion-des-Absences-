import os
from datetime import date

import face_recognition
import numpy as np
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from Ml_gestionABS_app.models import ClassGroup, Attendance, Student


def take_attendance(request, class_group_id):
    # Implémentez la logique ici
    return render(request, 'attendance/take_attendance.html', {'class_group_id': class_group_id})


@csrf_exempt
def process_attendance(request, class_group_id):
    if request.method == 'POST' and request.FILES.get('frame'):
        try:
            # Récupérer la photo téléchargée
            frame_file = request.FILES['frame']

            # Charger l'image pour la reconnaissance faciale
            frame_image = face_recognition.load_image_file(frame_file)

            # Trouver les positions et les encodages des visages
            face_locations = face_recognition.face_locations(frame_image)
            face_encodings = face_recognition.face_encodings(frame_image, face_locations)
            print(f"Nombre de visages détectés: {len(face_locations)}")

            if not face_encodings:
                return JsonResponse({'status': 'error', 'message': 'Aucun visage détecté dans l\'image'}, status=400)

            # Récupérer tous les étudiants dans le groupe de classe
            class_group = ClassGroup.objects.get(id=class_group_id)
            students = class_group.students.all()

            # Créer des listes des encodages connus et des IDs des étudiants
            known_encodings = []
            student_ids = []

            for student in students:
                if student.face_encoding:
                    known_encodings.append(np.frombuffer(student.face_encoding))
                    student_ids.append(student.id)

            # Liste des étudiants reconnus
            recognized_students = []

            # Parcourir chaque encodage de visage détecté
            for face_encoding in face_encodings:
                # Comparer l'encodage du visage détecté avec tous les encodages connus
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
                print(f"Correspondances pour ce visage: {matches}")

                # Si une correspondance est trouvée
                if True in matches:
                    match_index = matches.index(True)  # Trouver l'index du premier match
                    student_id = student_ids[match_index]  # Récupérer l'ID de l'étudiant correspondant
                    student = students.get(id=student_id)  # Trouver l'étudiant dans la base de données

                    # Marquer la présence de l'étudiant
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        class_group=class_group,
                        date=date.today(),
                        defaults={'is_present': True}
                    )

                    if not created:
                        attendance.is_present = True
                        attendance.save()

                    # Ajouter l'étudiant à la liste des étudiants reconnus
                    recognized_students.append({
                        'student_id': student.student_id,
                        'name': f"{student.first_name} {student.last_name}"
                    })
                else:
                    print("Aucun étudiant reconnu pour un visage.")

            if recognized_students:
                return JsonResponse({
                    'status': 'success',
                    'recognized_students': recognized_students
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Aucun étudiant reconnu'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Frame non reçue'}, status=400)


def home(request):
    # Redirige ou affiche une page d'accueil de ton choix
    return render(request, 'home.html')

