from django import forms
from .models import Agente


class FormAgente(forms.ModelForm):
    class Meta:
        model = Agente

        fields = [
            'NombreHost',
            'Ip',
            'Ip_publica',
            'Protocolo',
            'Puerto',
            'Comunidad',
            'Administrador_Agente',
        ]

        labels = {
            'NombreHost': 'Nombre del Host',
            'Ip': 'Ip del Agente',
            'Ip_publica': 'Ip publica del dispositivo',
            'Protocolo': 'Tipo de protocolo',
            'Puerto': 'Puerto',
            'Comunidad': 'Nombre de la comunidad',
            'Administrador_Agente': 'Administrador del Agente',
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
            'Administrador_Agente': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Huitzoo'}),
        }
