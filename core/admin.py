from django.contrib import admin
from .models import UserProfile, Categories, Brands, Suppliers, Products, StockIns, StockInDetails, Transactions, TransactionDetails, CashClosings

admin.site.register(UserProfile)
admin.site.register(Categories)
admin.site.register(Brands)
admin.site.register(Suppliers)
admin.site.register(Products)
admin.site.register(StockIns)
admin.site.register(StockInDetails)
admin.site.register(Transactions)
admin.site.register(TransactionDetails)
admin.site.register(CashClosings)
