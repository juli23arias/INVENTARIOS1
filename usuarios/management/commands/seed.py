from django.core.management.base import BaseCommand
from decimal import Decimal

from usuarios.models import Usuario
from productos.models import Producto
from proveedores.models import Proveedor, Compra, DetalleCompra
from inventario.models import InventarioHistorial
from ventas.models import Venta, DetalleVenta


class Command(BaseCommand):
    help = 'Carga datos iniciales del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando carga de datos iniciales...")

        # 1. Usuarios
        admin_user, _ = Usuario.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@correo.com', 'rol': 'ADMIN'}
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        cajero_user, _ = Usuario.objects.get_or_create(
            username='cajero',
            defaults={'email': 'cajero@correo.com', 'rol': 'CAJERO'}
        )
        cajero_user.set_password('cajero123')
        cajero_user.save()

        cliente_user, _ = Usuario.objects.get_or_create(
        username='cliente',
        defaults={'email': 'cliente@correo.com', 'rol': 'CLIENTE'}
        )
        cliente_user.set_password('cliente123')
        cliente_user.save()

        self.stdout.write("[OK] Usuarios cargados")

        # 2. Proveedores
        prov1, _ = Proveedor.objects.get_or_create(
            nombre='AgroInsumos S.A.',
            defaults={'contacto': 'Carlos Pérez', 'telefono': '0991234567', 'email': 'ventas@agroinsumos.com'}
        )

        prov2, _ = Proveedor.objects.get_or_create(
            nombre='Distribuidora Herramientas',
            defaults={'contacto': 'María López', 'telefono': '0987654321', 'email': 'contacto@distri.com'}
        )

        self.stdout.write("[OK] Proveedores cargados")

        # 3. Productos
        productos_data = [
            {'nombre': 'Pala Tramontina', 'precio': '15.50', 'stock': 20, 'categoria': 'Herramientas', 'stock_minimo': 5},
            {'nombre': 'Fertilizante NPK 50kg', 'precio': '45.00', 'stock': 10, 'categoria': 'Fertilizantes', 'stock_minimo': 3},
            {'nombre': 'Machete Collin', 'precio': '8.25', 'stock': 50, 'categoria': 'Herramientas', 'stock_minimo': 10},
            {'nombre': 'Semillas de Maíz Trueno 1kg', 'precio': '5.00', 'stock': 100, 'categoria': 'Semillas', 'stock_minimo': 20},
            {'nombre': 'Bomba Fumigadora 20L', 'precio': '35.00', 'stock': 2, 'categoria': 'Equipos', 'stock_minimo': 3},
        ]

        prods = []
        for pd in productos_data:
            p, created = Producto.objects.get_or_create(
                nombre=pd['nombre'],
                defaults={
                    'precio': Decimal(pd['precio']),
                    'stock': pd['stock'],
                    'categoria': pd['categoria'],
                    'stock_minimo': pd['stock_minimo']
                }
            )
            prods.append(p)

            if created:
                InventarioHistorial.objects.create(
                    producto=p,
                    tipo_movimiento='AJUSTE',
                    cantidad=p.stock
                )

        self.stdout.write("[OK] Productos cargados")

        # 4. Compras
        if Compra.objects.count() == 0:
            c1 = Compra.objects.create(proveedor=prov1)
            DetalleCompra.objects.create(compra=c1, producto=prods[1], cantidad=5, precio_compra=Decimal('40.00'))

            prods[1].stock += 5
            prods[1].save()

            InventarioHistorial.objects.create(producto=prods[1], tipo_movimiento='ENTRADA', cantidad=5)

        self.stdout.write("[OK] Compras creadas")

        # 5. Ventas
        if Venta.objects.count() == 0:
            v1 = Venta.objects.create(usuario=cajero_user)
            DetalleVenta.objects.create(venta=v1, producto=prods[3], cantidad=10, precio_unitario=prods[3].precio)

            v1.total = prods[3].precio * 10
            v1.save()

            prods[3].stock -= 10
            prods[3].save()

            InventarioHistorial.objects.create(producto=prods[3], tipo_movimiento='SALIDA', cantidad=10)

        self.stdout.write(self.style.SUCCESS("✅ Base de datos lista"))