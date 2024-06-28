from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="categorias", null=True)
    
    def __str__(self):
        return self.nombre
    
class Producto (models.Model):
    nombre = models.CharField(max_length=255)
    stock = models.IntegerField()
    precio = models.IntegerField(default=0)
    descripcion = models.TextField(null=True)
    categoria = models.ForeignKey(Categoria, on_delete= models.CASCADE)
    creado_en = models.DateTimeField(default=timezone.now)
    imagen = models.ImageField(upload_to="productos", null=True)
    
    def __str__(self):
        return self.nombre


class Carro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    comprado = models.BooleanField(default=False)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"


class Contacto (models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField()
    mensaje = models.TextField()
    
    
    
    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('DESPACHO', 'En Despacho'),
        ('TRANSITO', 'En Tránsito'),
        ('ENTREGADO', 'Entregado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.cantidad} de {self.producto.nombre}'