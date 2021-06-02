from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .tasks import get_products
from .models import Products
import json, os

@login_required()
def main(request):
    '''
    My Home Page.
    '''
    all_products = Products.objects.all()

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

    context = {
        "products":all_products,
        "urls":urls,
    }

    return render(request, "sales/ship.html", context)

@login_required()
@staff_member_required
def populate_products(request):
    get_products()
    return HttpResponseRedirect("/ship")