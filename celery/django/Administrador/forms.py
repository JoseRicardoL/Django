from django import forms
from .models import Administrador
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class FormAdministrador(forms.ModelForm):
    class Meta:
        model = Administrador

        fields = '__all__'

        widgets = {
            'Administrador': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Pamm'}),
            'Descripcion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. hecho en poli'}),
            'Telefono': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 5589472928'}),
        }


class FormUser(UserCreationForm):
    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email'
        ]
        labels = {
            'username': 'Nombre del Administrador',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email'
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. QWERTY'}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. jose'}),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. lopez'}),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.logjose.ri@gmail.com'}),
        }
