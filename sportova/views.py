from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Shipment, BannerPicture


def home(request):
    """Homepage with featured products and categories"""
    categories = Category.objects.all()[:3]  # Main categories
    featured_products = Product.objects.filter(is_featured=True)[:6]
    banner_pictures = BannerPicture.objects.all()[:5]
    # banner_products = Product.objects.filter(image__in=banner_pictures.values('image'))

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'banner_pictures': banner_pictures,
        # 'banner_products': banner_products,

    }
    return render(request, 'sportova/home.html', context)


def product_list(request):
    """View to display all products"""
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Get category filter from query parameters
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
    }
    return render(request, 'sportova/product_list.html', context)


def product_detail(request, slug):
    """Product detail page showing image, price, description and contact options"""
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:3]
    context = {
        'product': product,
        'category': product.category,
        'related_products': related_products,
    }
    return render(request, 'sportova/product_detail.html', context)


def category_detail(request, slug):
    """Category page showing all products in that category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'sportova/category_detail.html', context)


def shipment(request):
    """Shipment detail page showing image, description, delivery time and cost"""
    shipment = Shipment.objects.all()
    context = {
        'shipment': shipment,
    }
    return render(request, 'sportova/shipment.html', context)
