from django.contrib import admin
from .models import (Producto,
                     Pago,
                     MetodoDePago,
                     Imagen,
                     CategoriaPadre,
                     Categoria,
                     Carrito)
# Register your models here.


@admin.register(Producto)
class AdminProducto(admin.ModelAdmin):
    list_display = ('Id_Producto',
                    'Nombre_Producto',
                    'Marca_Producto',
                    'Modelo_Producto',
                    'Precio_Producto',
                    'Stock_Producto',
                    'Talla_Producto',
                    'Categoria_Producto',)
    list_filter = ('Nombre_Producto',)


@admin.register(Pago)
class AdminPago(admin.ModelAdmin):
    list_display = ('Id_Pago',
                    'Total_A_Pagar_Pago',
                    'Cliente_Pago',)
    list_filter = ('Id_Pago',)


@admin.register(MetodoDePago)
class AdminMetodoDePago(admin.ModelAdmin):
    list_display = ('Id_MetodoDePago',
                    'Nombre_MetodoDePago',)
    list_filter = ('Nombre_MetodoDePago',)


@admin.register(Imagen)
class AdminImagen(admin.ModelAdmin):
    list_display = ('Id_Imagen',
                    'Producto_Imagen',)


@admin.register(CategoriaPadre)
class AdminCategoriaPadre(admin.ModelAdmin):
    list_display = ('Id_CategoriaPadre',
                    'Nombre_CategoriaPadre',)


@admin.register(Categoria)
class AdminCategoria(admin.ModelAdmin):
    list_display = ('Id_Categoria',
                    'Nombre_Categoria',)
    list_filter = ('Nombre_Categoria',)


admin.site.register(Carrito)
