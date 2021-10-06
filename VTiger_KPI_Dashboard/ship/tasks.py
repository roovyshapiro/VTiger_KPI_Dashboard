from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q
 
from .models import Products
import VTiger_API
import json, os, datetime

@shared_task
def get_products():
    '''
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
    '''
    db_products = Products.objects.all()

    active_product_list = retrieve_products()

    for product in active_product_list:
        #If the product_id exists in the database, then the product will be updated
        #If the product_id doesn't exist, then the product will be added to the db
        try:
            new_product = db_products.get(product_id = product['id'])
        except:
            new_product = Products()

        new_product.createdtime = make_aware(datetime.datetime.strptime(product['createdtime'],'%Y-%m-%d %H:%M:%S'))
        new_product.modifiedtime = make_aware(datetime.datetime.strptime(product['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

        new_product.assigned_user_id = product['assigned_user_id']
        new_product.created_user_id = product['created_user_id']
        new_product.modified_by = product['modifiedby']
        new_product.assigned_username = product['assigned_username']
        new_product.modified_username = product['modified_username']

        new_product.product_id = product['id']
        new_product.url_id = product['id'].replace('6x','')
        #Some products don't have images
        try:
            new_product.image_id = product['imageattachmentids']
            new_product.image_url_id = product['imageattachmentids'].replace('6x','')
        except KeyError:
            new_product.image_id = ''
            new_product.image_url_id = ''

        try:
            new_product.width = product['cf_products_widthin']
        except ValueError:
            new_product.width = 0.0
        try:
            new_product.length = product['cf_products_lengthin']
        except ValueError:
            new_product.length = 0.0
        try:
            new_product.height = product['cf_products_heightin']
        except ValueError:
            new_product.height = 0.0
        try:
            new_product.weight = product['cf_products_weightlbs']
        except ValueError:
            new_product.weight = 0.0

        new_product.description = product['description']
        new_product.packing_list = product['cf_products_packinglist']
        new_product.number = product['product_no']
        new_product.category = product['productcategory']
        new_product.name = product['productname']
        new_product.stock = product['qtyinstock']
        new_product.price = float(product['unit_price'])
        if product['discontinued'] == '1':
            status = "Active"
        else:
            status = "InActive"
        new_product.status = status

        new_product.save()
    print('get_products() complete! ship.tasks')


def retrieve_products():
    '''
    Prior to running this function,
    Create a file named 'credentials.json' with VTiger credentials
    and put it in the main sales_dashboard directory.
    It should have the following format:
    {"username": "(user)", "access_key": "(access_key)", "host": "(host)"}
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    active_product_list = vtigerapi.retrieve_all_products()    

    return active_product_list