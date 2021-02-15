import csv

from io import StringIO
from wholesale.utils import get_file_details, get_last_created_file

from wholesale.serializer import FilesSerializer, ProductSerializer, PurchaseDetailedSerializer, PurchaseSerializer, RefillSerializer
from wholesale.models import Purchase, Product

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, ValidationError

from django.db import transaction
from django.http import HttpResponse
from django.db.models import F


class ProductAPIView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    serializer_action_classes = {
        "refill": RefillSerializer,
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return self.serializer_class

    @action(methods=['get'], detail=True, permission_classes=[])
    def purchases(self, request, pk=True):
        purchases = Purchase.objects.filter(product__id=pk)
        purchases_list = PurchaseSerializer(purchases, many=True)
        return Response(purchases_list.data)

    @action(methods=['get', 'post'], detail=True, permission_classes=[])
    def refill(self, request, pk=True):
        product = self.get_object()
        if request.method == 'POST':
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            product.quantity = F('quantity') + int(serializer.data.get("refill_count", 0))
            product.save()

        product.refresh_from_db()
        product_details = self.serializer_class(instance=product)
        return Response(product_details.data)


class PurchaseAPIView(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    csv_required_columns = ['Product Id', 'Purchased Id', 'Purchased Qty', 'Product Name', 'Price Per Quantity']
    serializer_action_classes = {
        "existing_files": FilesSerializer
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return self.serializer_class

    def save_purchase(self, file):
        purchase_list = []
        with file as fp:
            try:
                file_content = fp.read()
                file_content = file_content.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            csv_file = StringIO(file_content)
            csv_dict_reader = csv.DictReader(csv_file)
            column_names = csv_dict_reader.fieldnames
            if not all(item in column_names for item in self.csv_required_columns):
                return ValidationError("Provided files doesn't have the required columns")
            purchase_list = list(csv_dict_reader)

        for purchase in purchase_list:
            product_id = int(purchase['Product Id'])
            purchase_uuid = purchase['Purchased Id']
            purchase_qty = int(purchase['Purchased Qty'])
            product_name = purchase['Product Name'].strip()
            product_price = int(purchase['Price Per Quantity'])
            product_ins, _ = Product.objects.get_or_create(id=product_id, defaults={'name': product_name, 'price': product_price})
            purchase, _ = product_ins.purchase_set.get_or_create(uuid=purchase_uuid, defaults={'quantity': purchase_qty})
        return True

    @action(methods=['post'], detail=False, permission_classes=[])
    def upload(self, request):
        with transaction.atomic():

            file = request.FILES.get('file')
            self.save_purchase(file)
        return Response("Updated/Added")

    @action(methods=['post'], detail=False, permission_classes=[])
    def report(self, request, pk=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        csv_required_columns = ['Product Id', 'Purchased Id', 'Purchased Qty', 'Product Name', 'Price Per Quantity']

        writer = csv.writer(response)
        writer.writerow(csv_required_columns)

        purchase_list = Purchase.objects.all()
        for purchase in purchase_list:
            writer.writerow([purchase.product.id, purchase.uuid, purchase.quantity, purchase.product.name, purchase.product.price])
        return response


    @action(methods=['get', 'post'], detail=False, permission_classes=[])
    def existing_files(self, request, pk=True):
        if request.method == 'POST':
            file_path = request.POST.get('file')
            if file_path:
                file_obj = open(file_path, 'r')
                self.save_purchase(file_obj)
            else:
                _, file_path = get_last_created_file()
                if not file_path:
                    return ValidationError("No file found")
                file_obj = open(file_path, 'r')
                try:
                    self.save_purchase(file_obj)
                    return Response("Details saved successfully")
                except Exception as ex:
                    return NotAcceptable("Something unexpected happened")

        file_list = get_file_details()
        return Response(file_list)
