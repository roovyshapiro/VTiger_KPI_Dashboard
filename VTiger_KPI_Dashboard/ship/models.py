from django.db import models
from django.utils import timezone
import VTiger_API
import json, os

class Products(models.Model):
    '''
    Example Product:

    {
        "assigned_user_id": "19x65",
        "billing_type": "One time",
        "cf_1518": "",
        "cf_products_bundleditem": "0",
        "cf_products_heightin": "5",
        "cf_products_lengthin": "5",
        "cf_products_packinglist": " All the items that get packed into this product",
        "cf_products_weightlbs": "5",
        "cf_products_widthin": "5",
        "commissionrate": "",
        "created_user_id": "19x65",
        "createdtime": "2020-01-03 18:07:15",
        "description": "Advanced industrial grade mobile high-end product 3000.",
        "discontinued": "1", #If this is "0", then the product is not active.
        "expiry_date": "",
        "glacct": "",
        "id": "6x545516",
        "imageattachmentids": "6x743375",
        "imagename": "product_image.jpg",
        "isclosed": "0",
        "item_barcode": "",
        "manufacturer": "",
        "mfr_part_no": "",
        "modifiedby": "19x92",
        "modifiedtime": "2021-02-23 17:38:35",
        "product_no": "PRO445",
        "productcategory": "MainProductCat",
        "productcode": "",
        "productname": "Product3000",
        "productsheet": "",
        "productsubcategory": "",
        "purchase_cost": "",
        "qty_per_unit": "",
        "qtyindemand": "0",
        "qtyinstock": "411.000",
        "reorderlevel": "50",
        "sales_end_date": "",
        "sales_start_date": "",
        "serial_no": "",
        "source": "CRM",
        "starred": "0",
        "start_date": "",
        "tags": "",
        "taxclass": "on",
        "unit_price": "896.95000000",
        "usageunit": "",
        "vendor_id": "",
        "vendor_part_no": "",
        "website": ""
    },
    '''
    createdtime = models.DateTimeField(null=True)
    modifiedtime = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    assigned_user_id = models.CharField(max_length=50)
    created_user_id = models.CharField(max_length=50)
    modified_by = models.CharField(max_length=50)
    assigned_username = models.CharField(max_length=50)
    modified_username = models.CharField(max_length=75, default='')

    product_id = models.CharField(max_length=50)
    url_id = models.CharField(max_length=50, default='')
    image_id = models.CharField(max_length=50)
    image_url_id = models.CharField(max_length=50)
    
    width = models.IntegerField()
    length = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()

    description = models.TextField()
    packing_list = models.TextField()
    number = models.CharField(max_length=10)
    category = models.CharField(max_length=25)
    name = models.CharField(max_length=50)
    stock = models.CharField(max_length=50)
    price = models.FloatField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name} - {self.number}'