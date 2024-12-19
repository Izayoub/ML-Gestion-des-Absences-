# models.py
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
import face_recognition
import numpy as np
import os


class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='student_photos/')
    face_encoding = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """
        Validation lors de la sauvegarde pour vérifier qu'une photo est bien ajoutée
        et qu'un visage est détectable sur la photo.
        """
        if not self.photo:
            raise ValidationError("L'étudiant doit avoir une photo.")

        try:
            # Charger l'image depuis le fichier
            image_path = self.photo.file
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                raise ValidationError("Aucun visage détecté sur la photo. Veuillez utiliser une photo valide.")
        except Exception as e:
            raise ValidationError(f"Erreur lors du traitement de la photo : {e}")

    def save(self, *args, **kwargs):
        # Generate face encoding when saving with a photo
        if self.photo:
            image = face_recognition.load_image_file(self.photo)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                self.face_encoding = face_encodings[0].tobytes()
        super().save(*args, **kwargs)
        try:
            if self.photo:
                # Charger l'image à partir du chemin du fichier
                image_path = self.photo.path
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)

                # Vérifier si un visage est détecté
                if face_encodings:
                    self.face_encoding = face_encodings[0].tobytes()
                    super().save(update_fields=["face_encoding"])  # Mise à jour uniquement de l'encodage
                else:
                    print(f"Aucun visage détecté pour {self.first_name} {self.last_name}.")
            else:
                print("Aucune photo n'est associée à cet étudiant.")
        except Exception as e:
            print(f"Erreur lors de l'encodage du visage pour {self.first_name} {self.last_name} : {e}")


class ClassGroup(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'class_group', 'date']

        def __init__(self):
            self.is_present = None
            self.date = None
            self.student = None
            self.class_group = None

        def __str__(self):
            status = "Présent" if self.is_present else "Absent"
            return f"{self.student} - {self.class_group} ({self.date}): {status}"


