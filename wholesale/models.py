import uuid
from django.db import models
from django.db.models.deletion import DO_NOTHING
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Product(models.Model):
    id = models.AutoField(verbose_name="product id", unique=True, primary_key=True, db_index=True, null=False, blank=False)
    name = models.CharField(verbose_name="product name", max_length=256, null=False, blank=False)
    price = models.PositiveIntegerField(verbose_name="product price", null=False, blank=False)
    quantity = models.IntegerField(verbose_name="product quantity", default=25000, null=False, blank=False)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    uuid = models.UUIDField(verbose_name="purchase id", unique=True, default=uuid.uuid4, db_index=True, null=False, blank=False)
    quantity = models.IntegerField(verbose_name="purchase quantity", null=False, blank=False)
    product = models.ForeignKey(to=Product, null=False, blank=False, on_delete=DO_NOTHING)

    def __str__(self):
        return str(self.uuid)


@receiver(pre_save, sender=Purchase)
def handle_purchase(sender, instance, **kwargs):
    is_update = instance.id
    product = instance.product
    previous_quantity = product.quantity

    if is_update:
        # NOTE: When a purchase is updated we have to normalize the previous purchase quantity -
        # so that we don't have miss calculated values for the quantity
        purchase = Purchase.objects.get(id=instance.id)
        previous_quantity += purchase.quantity
        current_quantity = previous_quantity - instance.quantity
        product.quantity = current_quantity
    else:
        current_quantity = previous_quantity - instance.quantity
        product.quantity = current_quantity

    product.save(update_fields=['quantity'])


@receiver(post_delete, sender=Purchase)
def handle_purchase_delete(sender, instance, **kwargs):
    product = instance.product
    previous_quantity = product.quantity

    current_quantity = previous_quantity + instance.quantity
    product.quantity = current_quantity

    product.save(update_fields=['quantity'])
