from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
import re
from urllib.parse import quote


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sportova:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=100, default='N/A')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sportova:product_detail', kwargs={'slug': self.slug})

    # WhatsApp contact
    def get_whatsapp_url(self):
        size_info = f" (Size: {self.size})" if self.size and self.size != 'N/A' else ""
        message = f"Hi, I'm interested in {self.name}{size_info} - ${self.price}"
        # Clean number to digits only for wa.me compatibility
        raw = getattr(settings, 'WHATSAPP_NUMBER', '')
        phone_number = re.sub(r"\D", "", raw)
        return f"https://wa.me/{phone_number}?text={quote(message)}"

    # Email contact
    def get_email_recipient(self):
        return settings.CONTACT_EMAIL

    def get_email_subject(self):
        return f"Inquiry about {self.name}"

    def get_email_body(self):
        size_info = f"\nSize: {self.size}" if self.size and self.size != 'N/A' else ""
        return (
            f"Hi,\n\nI'm interested in the following product:\n\n"
            f"Product: {self.name}\nPrice: ${self.price}{size_info}\n"
            f"Description: {self.description}\n\n"
            f"Please provide more details.\n\nThank you!"
        )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per product
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Shipment(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='shipment/icons/', blank=True, null=True)
    description = models.TextField()
    delivery_time = models.CharField(max_length=100)
    cost = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class BackgroundImage(models.Model):
    SECTION_CHOICES = [
        ('hero', 'Hero Section'),
        ('categories', 'Premium Categories'),
        ('featured', 'Featured Products'),
        ('about', 'About Section'),
        ('contact', 'Contact Section'),
    ]
    
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)
    image = models.ImageField(upload_to='backgrounds/')
    overlay_opacity = models.FloatField(default=0.8, help_text="Overlay opacity (0.0 to 1.0)")
    overlay_color = models.CharField(max_length=7, default='#0E1C36', help_text="Overlay color (hex code)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section']
        verbose_name = 'Background Image'
        verbose_name_plural = 'Background Images'

    def __str__(self):
        return f"{self.get_section_display()} - {self.name}"

    def get_css_background(self):
        """Generate CSS background property with overlay"""
        return f"""
            background: 
                linear-gradient(135deg, rgba({self.hex_to_rgb(self.overlay_color)}, {self.overlay_opacity}) 0%, rgba({self.hex_to_rgb(self.overlay_color)}, {self.overlay_opacity - 0.05}) 100%),
                url('{self.image.url}') center/cover !important;
            background-attachment: fixed;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
        """

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


class BannerPicture(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banner/')
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
