from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StockInDetails, TransactionDetails, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile whenever a new User is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'role': 'admin'})

@receiver(post_save, sender=StockInDetails)
def update_stock_on_stockin(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock += instance.quantity
        product.buy_price = instance.buy_price # Auto-update HPP (Last In)
        if product.stock > 0 and product.status == 'inactive':
            product.status = 'active'
        product.save()

@receiver(post_save, sender=TransactionDetails)
def update_stock_on_transaction(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock -= instance.quantity
        if product.stock < 0:
            product.stock = 0  # Guard: stok tidak boleh negatif
        if product.stock <= 0:
            product.status = 'inactive'
        product.save()
