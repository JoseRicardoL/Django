from django import forms
from .models import Dispositivo


class FormDispositivo(forms.ModelForm):
    class Meta:
        model = Dispositivo

        fields = '__all__'

        labels = {
            'NombreHost': 'Nombre del Host',
            'Ip': 'Ip del Dispositivo',
            'Ip_publica': 'Ip publica del dispositivo',
            'Protocolo': 'Tipo de protocolo',
            'Puerto': 'Puerto',
            'Comunidad': 'Nombre de la comunidad',
            'Usuario_Dispositivo': 'Usuario del Dispositivo',
        }
        widgets = {
            'NombreHost': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Ubuntu'}),
            'Ip': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 10.0.0.2'}),
            'Ip_publica': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 198.64.120.12'}),
            'Protocolo': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. v1'}),
            'Puerto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 161'}),
            'Comunidad': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. SNMPescom'}),
            'Usuario_Dispositivo': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Tu cora'}),
        }
