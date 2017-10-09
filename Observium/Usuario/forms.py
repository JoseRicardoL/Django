from django import forms
from .models import Usuario
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class FormUsuario(forms.ModelForm):
    class Meta:
        model = Usuario

        fields = '__all__'

        widgets = {
            'Usuario': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Tu cora'}),
            'Descripcion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. El papi'}),
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
            'username': 'Nombre del usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email'
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. QWERTY'}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Alejandro'}),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Sanchez'}),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.Alejandro.Sanchez@gmail.com'}),
        }
