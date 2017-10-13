from django.db import models
from apps.Administrador.models import User
from apps.Administrador.models import Perfil


class MetodoDePago(models.Model):
    Id_MetodoDePago = models.AutoField(primary_key=True)
    Nombre_MetodoDePago = models.CharField(max_length=45)

    def __str__(self):
        return '{} {}'.format(
            self.Id_MetodoDePago,
            self.Nombre_MetodoDePago,)

    class Meta:
        verbose_name = 'MetodoDePago'
        verbose_name_plural = 'MetodosDePago'


class Pago(models.Model):
    Id_Pago = models.AutoField(primary_key=True)
    Total_A_Pagar_Pago = models.DecimalField(max_digits=6, decimal_places=2)
    Cliente_Pago = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    MetodoDePago = models.ForeignKey(
        MetodoDePago,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(
            self.Id_Pago,
            self.Total_A_Pagar_Pago,
            self.Cliente_Pago,
            self.MetodoDePago)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class CategoriaPadre(models.Model):
    Id_CategoriaPadre = models.AutoField(primary_key=True)
    Nombre_CategoriaPadre = models.CharField(max_length=45)

    def __str__(self):
        return '{} {}'.format(
            self.Id_CategoriaPadre,
            self.Nombre_CategoriaPadre,)

    class Meta:
        verbose_name = 'CategoriaPadre'
        verbose_name_plural = 'CategoriasPadres'


class Categoria(models.Model):
    Id_Categoria = models.AutoField(primary_key=True)
    Nombre_Categoria = models.CharField(max_length=45)

    def __str__(self):
        return '{} {}'.format(
            self.Id_Categoria,
            self.Nombre_Categoria,)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class Producto(models.Model):
    Id_Producto = models.AutoField(primary_key=True)
    Nombre_Producto = models.CharField(max_length=45)
    Marca_Producto = models.CharField(max_length=45)
    Modelo_Producto = models.CharField(max_length=45)
    Precio_Producto = models.DecimalField(max_digits=10, decimal_places=2)
    Stock_Producto = models.IntegerField()
    Talla_Producto = models.CharField(max_length=2)
    Administrador_Producto = models.ManyToManyField(Perfil)
    Imagen_Producto = models.ImageField(blank=True)

    Categoria_Producto = models.ForeignKey(
        Categoria,
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    CategoriaPadre_Producto = models.ForeignKey(
        CategoriaPadre,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {} {} {} {}'.format(
            self.Id_Producto,
            self.Nombre_Producto,
            self.Marca_Producto,
            self.Modelo_Producto,
            self.Precio_Producto,
            self.Stock_Producto,
            self.Talla_Producto,
            self.Administrador_Producto)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Imagen(models.Model):
    Id_Imagen = models.AutoField(primary_key=True)
    imagen = models.ImageField(blank=True)
    Producto_Imagen = models.ForeignKey(
        Producto,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(
            self.Id_Imagen,
            self.imagen,
            self.Producto_Imagen)

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'


class Carrito(models.Model):
    Id_Pago_Producto = models.AutoField(primary_key=True)
    Cantidad = models.IntegerField()
    Cliente_Carrito = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    Producto_Carrito = models.ForeignKey(
        Producto,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(
            self.Id_Pago_Producto,
            self.Cantidad,
            self.Cliente_Carrito,
            self.Producto_Carrito,)

    class Meta:
        verbose_name = 'Pago_Producto'
        verbose_name_plural = 'Pago_Productos'
