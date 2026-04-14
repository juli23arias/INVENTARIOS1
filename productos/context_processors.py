from .models import Categoria

def categorias_processor(request):
    return {
        'categorias_global': Categoria.objects.all().order_by('nombre')
    }
