from django.http import response
from django.http.response import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .tasks import get_products
from .models import Products
import json, os, requests

@login_required()
def main(request):
    '''
    My Home Page.
    '''
    all_products = Products.objects.all().order_by('name').filter(~Q(weight=0))

    product_selection = request.GET.get('product_dropdown')
    selected_product = all_products.filter(name=product_selection)
    for item in selected_product:
        print(item.name, item.number)

    #The VTiger hostnames are stored in the 'credentials.json' file.
    #The URLs themselves will look something like this:
    #"host_url_products": "https://my_vtiger_instance_name.vtiger.com/index.php?module=Products&view=Detail&record=", 
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    urls = {}
    urls['products_url'] = credential_dict['host_url_products']
    urls['image_url'] = credential_dict['host_url_products_image']

 
    #With the use of JSON Script we can get data from the Django model and then
    #access it with JS
    #https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#json-script
    products_json = {}
    for product in all_products:
        products_json[product.name] = {}
        products_json[product.name]['name'] = product.name
        products_json[product.name]['description'] = product.description
        products_json[product.name]['packing_list'] = product.packing_list
        products_json[product.name]['number'] = product.number
        products_json[product.name]['stock'] = product.stock
        products_json[product.name]['price'] = product.price
        products_json[product.name]['width'] = product.width
        products_json[product.name]['length'] = product.length
        products_json[product.name]['height'] = product.height
        products_json[product.name]['weight'] = product.weight


    context = {
        "products":all_products,
        "urls":urls,
        "products_json":products_json,
    }

    return render(request, "sales/ship.html", context)

@login_required()
@staff_member_required
def populate_products(request):
    get_products()
    return HttpResponseRedirect("/ship")

def rating(clientRequest):
    credentials_file = 'ups_credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
        credential_dict = json.loads(data)

    upsurl = "https://onlinetools.ups.com/ship/1801/rating/Shop"

    if clientRequest.method == 'POST':
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "AccessLicenseNumber": credential_dict['AccessLicenseNumber'],
            "Username": credential_dict['Username'],
            "Password": credential_dict['Password']
        }
        body = json.loads(clientRequest.body)

        try:
            response = requests.post(upsurl, headers=headers, json=body)
            return JsonResponse(response.json());
        except:
            print(response.status_code)