from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_transactions_discount_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashclosings',
            name='unlocked_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='unlocked_closings',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Dibuka oleh'
            ),
        ),
        migrations.AddField(
            model_name='cashclosings',
            name='unlocked_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Waktu dibuka'),
        ),
        migrations.AddField(
            model_name='cashclosings',
            name='unlock_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Alasan dibuka'),
        ),
        migrations.AddField(
            model_name='cashclosings',
            name='unlock_count',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Jumlah dibuka ulang'),
        ),
    ]
