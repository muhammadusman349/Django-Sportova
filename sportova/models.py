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
        message = f"Hi, I'm interested in {self.name} - ${self.price}"
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
        return (
            f"Hi,\n\nI'm interested in the following product:\n\n"
            f"Product: {self.name}\nPrice: ${self.price}\n"
            f"Description: {self.description}\n\n"
            f"Please provide more details.\n\nThank you!"
        )


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
