from monki.boards.models import Category


def inject_categories(request):
    return {
        'categories': Category.objects.prefetch_related('boards')
    }
