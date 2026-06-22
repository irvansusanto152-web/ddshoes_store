from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0002_alter_products_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockAdjustments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('reason', models.CharField(choices=[('rusak', 'Rusak / Cacat'), ('hilang', 'Hilang'), ('retur', 'Retur ke Supplier'), ('lainnya', 'Lainnya')], max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('adjusted_at', models.DateTimeField(auto_now_add=True)),
                ('adjusted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adjustments', to='core.products')),
            ],
        ),
    ]
