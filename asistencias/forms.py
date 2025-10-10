from django import forms
from .models import Diplomatura, Materia, Clase

class DiplomaturaForm(forms.ModelForm):
    class Meta:
        model = Diplomatura
        fields = ['nombre', 'descripcion']

class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['diplomatura', 'nombre', 'descripcion']

class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['materia', 'fecha', 'inicio_habilitacion', 'fin_habilitacion', 'tema']

class MarcarPresenteForm(forms.Form):
    dni = forms.CharField(label="DNI", max_length=20)
