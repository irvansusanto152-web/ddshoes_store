from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('kasir', 'Kasir')])
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Brands(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Suppliers(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Products(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    CONDITION_CHOICES = [
        ('Baru', 'Baru'),
        ('Like New', 'Like New'),
        ('Good', 'Good'),
        ('Fair', 'Fair')
    ]

    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brands, on_delete=models.SET_NULL, null=True)
    product_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Kode Produk')
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    description = models.TextField(null=True, blank=True)
    buy_price = models.IntegerField()
    sell_price = models.IntegerField()
    stock = models.IntegerField(default=0)
    image = models.FileField(upload_to='products/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.size}"

class StockIns(models.Model):
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    received_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StockIn {self.id} - {self.received_date}"

class StockInDetails(models.Model):
    stock_in = models.ForeignKey(StockIns, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    buy_price = models.IntegerField()

    def __str__(self):
        return f"{self.stock_in.id} - {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.buy_price

class Transactions(models.Model):
    PAYMENT_CHOICES = [
        ('tunai', 'Tunai'),
        ('transfer_bri', 'Transfer BRI'),
        ('qris', 'QRIS')
    ]

    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subtotal_amount = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0)
    total_amount = models.IntegerField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    cash_received = models.IntegerField(null=True, blank=True)
    change_amount = models.IntegerField(null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default='success', choices=[('success', 'Berhasil'), ('void', 'Dibatalkan')])
    voided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='voided_transactions')
    void_reason = models.TextField(null=True, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Trx {self.id} - {self.total_amount}"

class TransactionDetails(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    sell_price = models.IntegerField()
    subtotal = models.IntegerField()

    def __str__(self):
        return f"Trx {self.transaction.id} - {self.product.name}"

class CashClosings(models.Model):
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    closing_date = models.DateField()
    system_cash_total = models.IntegerField()
    system_transfer_total = models.IntegerField()
    system_qris_total = models.IntegerField()
    actual_cash = models.IntegerField()
    cash_difference = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # --- Audit: Buka Ulang Closing ---
    unlocked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='unlocked_closings', verbose_name='Dibuka oleh'
    )
    unlocked_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu dibuka')
    unlock_reason = models.TextField(null=True, blank=True, verbose_name='Alasan dibuka')
    unlock_count = models.PositiveSmallIntegerField(default=0, verbose_name='Jumlah dibuka ulang')

    def __str__(self):
        return f"Closing {self.cashier.username} - {self.closing_date}"

class StockAdjustments(models.Model):
    REASON_CHOICES = [
        ('rusak', 'Rusak / Cacat'),
        ('hilang', 'Hilang'),
        ('retur', 'Retur ke Supplier'),
        ('lainnya', 'Lainnya'),
    ]

    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, related_name='adjustments')
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()  # Negatif = pengurangan stok
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(null=True, blank=True)
    adjusted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Adj #{self.id} - {self.product} ({self.quantity})"
