from django.shortcuts import render, redirect
from .forms import (AdministradorForm,
                    ProductoForm,
                    CategoriaForm,
                    CategoriaPadreForm,
                    MetodoDePagoForm)
from apps.Administrador.models import Perfil
from apps.Producto.models import (Producto,
                                  Categoria,
                                  CategoriaPadre,
                                  MetodoDePago)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test


def staff_required(login_url=None):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def ProductoVista(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('Administrador:ProductoVista')
    else:
        form = ProductoForm()
    producto = Producto.objects.all()
    contexto = {'productos': producto,
                'form': form}
    return render(request,
                  'Administrador/producto_vista.html',
                  contexto)


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def AdministradorVista(request):
        if request.method == 'POST':
            action = request.POST.get('action', None)
            if action == 'user':
                username = request.POST.get('username', None)
                password = request.POST.get('password', None)
                first_name = request.POST.get('first_name', None)
                last_name = request.POST.get('last_name', None)
                email = request.POST.get('email', None)
                is_staff = True
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_staff=is_staff)
                user.save()
            elif action == 'extend':
                form = AdministradorForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
            return redirect('Administrador:AdministradorVista')
        else:
            form = AdministradorForm()
            administrador = Perfil.objects.all()
            contexto = {'administradores': administrador,
                        'form': form}
        return render(request,
                      'Administrador/administrador_vista.html',
                      contexto)


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def AdministradorEditar(request, Id):
    admin = Perfil.objects.get(id=Id)
    if request.method == 'GET':
        form = AdministradorForm(instance=admin)
    else:
        form = AdministradorForm(request.POST, request.FILES, instance=admin)
        if form.is_valid():
            form.save()
        return redirect('Administrador:AdministradorVista')
    return render(request,
                  'Administrador/administrador_form.html',
                  {'form': form,
                   'admin': admin})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def AdministradorEliminar(request, Id):
    admin = Perfil.objects.get(id=Id)
    if request.method == 'POST':
        admin.delete()
        return redirect('Administrador:AdministradorVista')
    return render(request,
                  'Administrador/administrador_borrar.html',
                  {'admin': admin})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def ProductoEditar(request, Id):
    producto = Producto.objects.get(Id_Producto=Id)
    if request.method == 'GET':
        form = ProductoForm(instance=producto)
    else:
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
        return redirect('Administrador:ProductoVista')
    return render(request,
                  'Administrador/producto_form.html',
                  {'form': form,
                   'producto': producto})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def ProductoEliminar(request, Id):
    prod = Producto.objects.get(Id_Producto=Id)
    if request.method == 'POST':
        prod.delete()
        return redirect('Administrador:ProductoVista')
    return render(request,
                  'Administrador/producto_borrar.html',
                  {'producto': prod})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def CategoriaVista(request):
    if request.method == 'POST':
        action = request.POST.get('action', None)
        if action == 'categoriapadre':
            form2 = CategoriaPadreForm(request.POST)
            if form2.is_valid():
                form2.save()
            return redirect('Administrador:CategoriaVista')
        elif action == 'categoria':
            form = CategoriaForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect('Administrador:CategoriaVista')
    else:
        form = CategoriaForm()
        form2 = CategoriaPadreForm()
    categoria = Categoria.objects.all()
    categoria2 = CategoriaPadre.objects.all()
    contexto = {'categorias': categoria,
                'categorias2': categoria2,
                'form': form,
                'form2': form2}
    return render(request,
                  'Administrador/categoria_vista.html',
                  contexto)


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def CategoriaEditar(request, Id):
    categoria = Categoria.objects.get(Id_Categoria=Id)
    if request.method == 'GET':
        form = CategoriaForm(instance=categoria)
    else:
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
        return redirect('Administrador:CategoriaVista')
    return render(request,
                  'Administrador/categoria_form.html',
                  {'form': form})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def CategoriaEliminar(request, Id):
    categoria = Categoria.objects.get(Id_Categoria=Id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('Administrador:CategoriaVista')
    return render(request,
                  'Administrador/categoria_borrar.html',
                  {'categoria': categoria})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def CategoriaPadreEditar(request, Id):
    categoriapadre = CategoriaPadre.objects.get(Id_CategoriaPadre=Id)
    if request.method == 'GET':
        form = CategoriaPadreForm(instance=categoriapadre)
    else:
        form = CategoriaPadreForm(request.POST, instance=categoriapadre)
        if form.is_valid():
            form.save()
        return redirect('Administrador:CategoriaVista')
    return render(request,
                  'Administrador/categoriapadre_form.html',
                  {'form': form})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def CategoriaPadreEliminar(request, Id):
    categoriapadre = CategoriaPadre.objects.get(Id_CategoriaPadre=Id)
    if request.method == 'POST':
        categoriapadre.delete()
        return redirect('Administrador:CategoriaVista')
    return render(request,
                  'Administrador/categoriapadre_borrar.html',
                  {'categoriapadre': categoriapadre})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def MetodoDePagoVista(request):
    if request.method == 'POST':
        form = MetodoDePagoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('Administrador:MetodoDePagoVista')
    else:
        form = MetodoDePagoForm()
    metododepago = MetodoDePago.objects.all()
    contexto = {'metodosdepago': metododepago,
                'form': form}
    return render(request,
                  'Administrador/metododepago_vista.html',
                  contexto)


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def MetodoDePagoEditar(request, Id):
    metododepago = MetodoDePago.objects.get(Id_MetodoDePago=Id)
    if request.method == 'GET':
        form = MetodoDePagoForm(instance=metododepago)
    else:
        form = MetodoDePagoForm(request.POST, instance=metododepago)
        if form.is_valid():
            form.save()
        return redirect('Administrador:MetodoDePagoVista')
    return render(request,
                  'Administrador/metododepago_form.html',
                  {'form': form})


@staff_required(login_url='Producto:ProductoList')
@login_required(login_url='/Administrador/')
def MetodoDePagoEliminar(request, Id):
    metododepago = MetodoDePago.objects.get(Id_MetodoDePago=Id)
    if request.method == 'POST':
        metododepago.delete()
        return redirect('Administrador:MetodoDePagoVista')
    return render(request,
                  'Administrador/metododepago_borrar.html',
                  {'metododepago': metododepago})


def LoginAdministrador(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('Administrador:MetodoDePagoVista')
    context = {}
    return render(request, 'Administrador/login.html', context)


def Registrar(request):
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            email = request.POST.get('email', None)
            is_staff = False
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=is_staff)
            user.save()
            return redirect('Administrador:LoginAdministrador')
        else:
            form = AdministradorForm()
            contexto = {'form': form}
        return render(request,
                      'Administrador/registrar.html',
                      contexto)
