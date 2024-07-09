from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ContactoForm, ProductoForm, CustomUserCreationForm, DatosEnvioForm
from .models import Pedido, PedidoItem, Producto, Carro
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from shop.carro import Carrito
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.


@permission_required('shop.view_producto')
def index (request):
    productos = Producto.objects.all()
    page = request.GET.get('page', 1)
    
    try:
        paginator = Paginator(productos, 10)
        productos = paginator.page(page)
    except:
        raise Http404
    
    data = {
        'entity': productos,
        'paginator': paginator,
        
    }
    return render(
        request,
        'index.html',
        context={
            'productos': productos,
            'paginator': paginator}
    )



def detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto = Producto.objects.get(id=producto_id)
        
    return render(
        request, 
        'detalle.html', 
        context= {'producto': producto})
    

    
def stickers(request):
    productos = Producto.objects.filter(categoria_id=1)
    return render(request, 'stickers.html', {'productos': productos})

def llantas(request):
    productos = Producto.objects.filter(categoria_id=2)
    return render(request, 'llantas.html', {'productos': productos})

def accesorios(request):
    productos = Producto.objects.filter(categoria_id=3)
    return render(request, 'accesorios.html', {'productos': productos})

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/shop/contacto')  
    else:
        form = ContactoForm()

    data = {
        'contacto_form': form
    }
    return render(request, 'contacto.html', data)

def tienda(request):

    return render(request, 'tienda.html')




@permission_required('shop.add_producto')
def agregar_producto (request):
    data= {
        'form': ProductoForm()
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Agregado Correctamente")
        else:
            data["form"] = formulario
    
    return render(request,'producto/agregar.html', data)



@permission_required('shop.change_producto')
def modificar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    data = {
        'form' : ProductoForm(instance=producto)
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente")
            return HttpResponseRedirect('/shop')
        else:
            data["form"] = formulario
    
    return render(request, 'producto/modificar.html',data)



@permission_required('shop.delete_producto')
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, "Eliminado Correctamente")
    return HttpResponseRedirect('/shop')
    
    
def registro (request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username= formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, "Registrado Correctamente")
            return redirect(to="inicio")
        data['form'] = formulario
    return render(request, 'registration/registro.html', data)


@login_required
def agregar_producto_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.agregar(producto)
    
    messages.success(request, f"Producto {producto.nombre} agregado al carrito.")
    return redirect('tienda')
@login_required
def agregar_producto_carrito_otro(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.agregar(producto)
    return redirect('carrito')
@login_required
def eliminar_producto_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("tienda")
@login_required
def restar_producto_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("carrito")
@login_required
def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("carrito")

def iniciar_carrito(request):
    if 'carrito' not in request.session:
        request.session['carrito'] = {}


@login_required
def carrito(request):
    if 'carrito' not in request.session:
        request.session['carrito'] = {}
    carrito = request.session['carrito']
    productos_carrito = []
    total = 0

    for key, value in carrito.items():
        producto = get_object_or_404(Producto, id=int(key))
        subtotal = producto.precio * value['cantidad']
        total += subtotal
        productos_carrito.append({
            'producto': producto,
            'cantidad': value['cantidad'],
            'subtotal': subtotal,
        })

    context = {
        'productos_carrito': productos_carrito,
        'total_carrito': total
    }
    return render(request, 'carrito.html', context)

@login_required
def comprar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    Carro.objects.create(usuario=request.user, producto=producto, cantidad=1, comprado=True)
    messages.success(request, "Producto comprado exitosamente.")
    return redirect('mis_pedidos')

@login_required
def mis_pedidos(request):

    pedidos = Pedido.objects.filter(usuario=request.user)
    context = {
        'pedidos': pedidos
    }
    return render(request, 'mis_pedidos.html', context)

@login_required
def procesar_pedido(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        if carrito:
            total = sum(item['acumulado'] for item in carrito.values())
            pedido = Pedido.objects.create(usuario=request.user, total=total)
            
            for item in carrito.values():
                producto = Producto.objects.get(id=item['producto_id'])
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    subtotal=item['acumulado']
                )
                
            request.session['carrito'] = {}
            
            return redirect('mis_pedidos')
        else:
            return redirect('carrito')
    else:
        return redirect('carrito')
    
    
@staff_member_required
def panel_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-creado_en')

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
        return redirect('panel_pedidos') 

    context = {
        'pedidos': pedidos
    }
    return render(request, 'panel_pedidos.html', context)

@staff_member_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    context = {
        'pedido': pedido,
    }
    return render(request, 'detalle_pedido.html', context)


def zona_pago(request):
    if request.method == 'POST':
        form = DatosEnvioForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                usuario=request.user,
                total=sum(item['acumulado'] for item in request.session['carrito'].values()),
            )
            
            carrito = request.session['carrito']
            for key, value in carrito.items():
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto_id=value['producto_id'],
                    cantidad=value['cantidad'],
                    subtotal=value['acumulado']
                )
            

            del request.session['carrito']
            
            return redirect('mis_pedidos') 
    else:
        form = DatosEnvioForm()

    carrito = request.session.get('carrito', {})
    total_carrito = sum(item['acumulado'] for item in carrito.values())

    context = {
        'form': form,
        'carrito': carrito,
        'total_carrito': total_carrito,
    }
    return render(request, 'zona_pago.html', context)