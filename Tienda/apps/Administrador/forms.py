from django import forms
from .models import Perfil
from apps.Producto.models import (Producto,
                                  Categoria,
                                  CategoriaPadre,
                                  MetodoDePago,
                                  Carrito)


class AdministradorForm(forms.ModelForm):
    class Meta:
        model = Perfil

        fields = '__all__'
        widgets = {
            'Tipo': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Luis'}),
            'Telefono': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 14114901'}),
            'Direccion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Polanco'}),
            'user': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Luis'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'Nombre_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Saco'}),
            'Marca_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Hugo Boss'}),
            'Modelo_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Cartagena'}),
            'Precio_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 1000.00'}),
            'Stock_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 10'}),
            'Talla_Producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. md'}),
            'Administrador_Producto':  forms.CheckboxSelectMultiple(),
            'CategoriaPadre_Producto': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Caballero'}),
            'Categoria_Producto': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Saco'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = [
            'Nombre_Categoria',
        ]
        labels = {
            'Nombre_Categoria': 'Nombre de la Categoria',
        }
        widgets = {
            'Nombre_Categoria': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Zapatos'}),
        }


class CategoriaPadreForm(forms.ModelForm):
    class Meta:
        model = CategoriaPadre
        fields = [
            'Nombre_CategoriaPadre',
        ]
        labels = {
            'Nombre_CategoriaPadre': 'Nombre de la Categoria Padre',
        }
        widgets = {
            'Nombre_CategoriaPadre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Caballero'}),
        }


class MetodoDePagoForm(forms.ModelForm):
    class Meta:
        model = MetodoDePago
        fields = [
            'Nombre_MetodoDePago',
        ]
        labels = {
            'Nombre_MetodoDePago': 'Nombre del Metodo de Pago',
        }
        widgets = {
            'Nombre_MetodoDePago': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. Efectivo'}),
        }


class CarritoForm(forms.ModelForm):
    class Meta:
        model = Carrito

        fields = [
            'Cantidad',
            'Cliente_Carrito',
            'Producto_Carrito',
        ]
        labels = {
            'Cantidad': 'Cantidad',
            'Cliente_Carrito': 'Cliente',
            'Producto_Carrito': 'Producto',
        }
        widgets = {
            'Cliente_Carrito': forms.Select(attrs={
                'class': 'form-control'}),
            'Cantidad': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex. 12 '}),
            'Producto_Carrito': forms.Select(attrs={
                'class': 'form-control'}),
        }
