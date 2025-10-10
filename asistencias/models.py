from django.db import models
from django.utils import timezone

class Diplomatura(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Materia(models.Model):
    diplomatura = models.ForeignKey(Diplomatura, on_delete=models.CASCADE, related_name='materias')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        unique_together = ('diplomatura', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.diplomatura})"

class Alumno(models.Model):
    apellido1 = models.CharField(max_length=150)
    apellido2 = models.CharField(max_length=150, blank=True)
    nombre1 = models.CharField(max_length=150)
    nombre2 = models.CharField(max_length=150, blank=True)
    dni = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.apellido1}, {self.nombre1} ({self.dni})"

class Clase(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='clases')
    fecha = models.DateField()
    inicio_habilitacion = models.DateTimeField(help_text='Inicio de ventana para marcar presente')
    fin_habilitacion = models.DateTimeField(help_text='Fin de ventana para marcar presente')
    tema = models.CharField(max_length=255, blank=True)

    def esta_habilitada(self):
        now = timezone.now()
        return self.inicio_habilitacion <= now <= self.fin_habilitacion

    def __str__(self):
        return f"{self.materia} - {self.fecha}"

class Asistencia(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='asistencias')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='asistencias')
    presente = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('clase', 'alumno')

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        return f"{self.alumno} - {self.clase} - {estado}"
