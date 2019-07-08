from Producto.models import Producto, CategoriaPadre, Carrito
from django.shortcuts import render, redirect
from Administrador.forms import CarritoForm
from django.contrib.auth.decorators import login_required


def ProductoList(request):
    producto = Producto.objects.all()
    categoriapadre = CategoriaPadre.objects.all()
    contexto = {'productos': producto,
                'categoriapadre': categoriapadre}
    return render(request, 'Producto/producto_list.html', contexto)


@login_required(login_url='/Administrador/')
def ProductoDetalle(request, Id_Producto):
    producto = Producto.objects.get(Id_Producto=Id_Producto)
    productos = Producto.objects.all()

    if request.method == 'POST':
        form = CarritoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('Producto:ProductoCarrito')
    else:
        form = CarritoForm()
    context = {'producto': producto,
               'productos': productos,
               'form': form}
    return render(request,
                  'Producto/producto_detail.html',
                  context)


@login_required(login_url='/Administrador/')
def ProductoCarrito(request):
    productos = Producto.objects.all()
    carrito = Carrito.objects.all()
    context = {'carrito': carrito,
               'productos': productos}
    return render(request,
                  'Producto/carrito.html',
                  context)


@login_required(login_url='/Administrador/')
def ProductoEditar(request, Id):
    carrito = Carrito.objects.get(Id_Pago_Producto=Id)
    if request.method == 'GET':
        form = CarritoForm(instance=carrito)
    else:
        form = CarritoForm(request.POST, instance=carrito)
        if form.is_valid():
            form.save()
        return redirect('Producto:ProductoCarrito')
    return render(request,
                  'Producto/carrito_form.html',
                  {'form': form,
                   'carrito': carrito})


@login_required(login_url='/Administrador/')
def ProductoEliminar(request, Id):
    carrito = Carrito.objects.get(Id_Pago_Producto=Id)
    if request.method == 'POST':
        carrito.delete()
        return redirect('Producto:ProductoCarrito')
    return render(request,
                  'Producto/carrito_borrar.html',
                  {'carrito': carrito})


def Busqueda(request, Id_CategoriaPadre):
    categoriapadre = CategoriaPadre.objects.get(
        Id_CategoriaPadre=Id_CategoriaPadre)
    producto = Producto.objects.all()
    contexto = {'productos': producto,
                'categoriapadre': categoriapadre}
    return render(request,
                  'Producto/busqueda.html',
                  contexto)
