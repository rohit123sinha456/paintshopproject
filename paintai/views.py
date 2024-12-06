from django.shortcuts import render
from .streamprocess.source.addCamera import create_new_camera_add_service,\
    delete_nssm_service,start_nssm_service,stop_nssm_service,get_camera_list_from_db
from .products import *
from .productprod import *
from .productprod import *
import json
from django.http import HttpResponse,JsonResponse
from datetime import datetime
import time 
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def addCamera(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cameraname = data.get("cameraname")
            ipaddr = data.get("ipaddr")
            create_new_camera_add_service(cameraname,ipaddr)
            return JsonResponse({"message": "Service Created", "name": cameraname, "IP": ipaddr})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            cameraid = data.get("cameraid")
            delete_nssm_service(cameraid)
            return JsonResponse({"message": "Camera Deleted", "name": cameraid})
        except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("Please send a post request")

def getAllCameras(request):
    data = None
    try:
        data = get_camera_list_from_db()
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def startService(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            servicename = data.get("servicename")
            start_nssm_service(servicename)
            return JsonResponse({"message": "Service Started", "name": servicename})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("Please send a post request")
    

def stopService(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            servicename = data.get("servicename")
            stop_nssm_service(servicename)
            return JsonResponse({"message": "Service Stopped", "name": servicename})
        except json.JSONDecodeError:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("Please send a post request")
    

def create_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            yoloid = data.get("yoloid")
            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)
            product = create_product_fn(name=name,yoloid=yoloid)
            return JsonResponse({"message": "Product created", "id": product.id, "name": product.name}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_product(request, product_id):
    if request.method == "GET":
        try:
            product = get_product_by_id_fn(product_id)
            return JsonResponse({"id": product.id, "name": product.name, "createdon": product.createdon}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def get_product_by_name(request, product_name):
    if request.method == "GET":
        try:
            product = get_product_by_name_fn(product_name)
            print(product)
            return JsonResponse({"id": product.id, "name": product.name, "createdon": product.createdon}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
def get_all_products(request):
    if request.method == "GET":
        try:
            products = get_all_products_fn()
            product_list = [{"id": p.id, "name": p.name, "createdon": p.createdon} for p in products]
            return JsonResponse({"products": product_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def soft_delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            product = soft_delete_product_fn(product_id)
            return JsonResponse({"message": "Product is deleted"},status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)



def get_all_production(request):
    if request.method == "GET":
        try:
            products = get_all_product_productions_fn()
            product_list = [{"id": p.id, "camera_id": p.cameraid.id,"productid": p.productid.id,"count": p.count, "starttime": p.starttime,"endtime": p.endtime} for p in products]
            return JsonResponse({"product_productions": product_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def get_production_by_date(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            starttime = datetime.strptime(data.get("starttime"), "%Y-%m-%dT%H:%M:%S.%f")
            endtime = datetime.strptime(data.get("endtime"), "%Y-%m-%dT%H:%M:%S.%f")
            products = get_product_counts(starttime,endtime)
            product_list =  list(products)
            return JsonResponse({"product_productions": product_list}, status=200,safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)




def create_production(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            return JsonResponse({"message": "Service Created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("Please send a post request")


def getCameraPayload(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            cameraid = data.pop('cameraid')
            starttime = datetime.strptime(data.pop('starttime'), "%Y-%m-%dT%H:%M:%S.%f")
            endtime = datetime.strptime(data.pop('endtime'), "%Y-%m-%dT%H:%M:%S.%f")
            for key,value in data.items():
                create_product_production(cameraid, key, starttime, endtime, sum(value.values()))
                time.sleep(1)
            return JsonResponse({"message": "Service Created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("Please send a post request")