from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from .models import Platillo 

class RegistroForm(UserCreationForm): 
    email = forms.EmailField(required=True)

    class Meta: 
        model = User
        fields = ["username", "email", "password1", "password2"]

class PlatilloForm(forms.ModelForm):
    class Meta:
        model = Platillo
        fields = ["nombre", "descripcion", "precio", "imagen", "ingredientes"]