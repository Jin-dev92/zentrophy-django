from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, File, Router
# from conf.api import api
# from util.globalVar import GlobalVar
from conf.globalVar import GlobalVar
from product.constant import ProductListSort
from product.models import Product, ProductDisplayLine, ProductOptions, ProductImage, Vehicle, VehicleColor, \
    VehicleImage
from product.schema import ProductListSchema, ProductInsertSchema, ProductDisplayLineSchema, ProductDisplayInsertSchema, \
    VehicleListSchema, VehicleInsertSchema

router = Router()
current_product_sort = ProductListSort.UPDATE_AT


@router.get("",
            description="상품 리스트 가져오기 sort 등록순: 0, 판매순 : 1 , 재고수량순: 2, 진열 라인 순: 3",
            response={200: List[ProductListSchema]},
            tags=["product"]
            )
def get_product_list(request, sort: ProductListSort):
    field_name = None
    global current_product_sort
    if sort == ProductListSort.UPDATE_AT:
        field_name = "is_created"
    elif sort == ProductListSort.SALE:
        field_name = "sale_count"
    elif sort == ProductListSort.STOCK_COUNT:
        field_name = "stock_count"
    elif sort == ProductListSort.DISPLAY_LINE:
        field_name = "product_display_line"

    if sort == current_product_sort:
        field_name = "-" + field_name
    else:
        current_product_sort = sort

    return Product.objects.all().prefetch_related(
        'product_options',
        'product_display_line',
        'product_image').order_by(current_product_sort)


@router.get("/{id}",
            description="해당 상품 가져오기",
            response={200: ProductListSchema},
            tags=["product"]
            )
def get_product_list_by_id(request, id: int):
    return get_object_or_404(Product, id=id)


@router.post("", description="상품 등록", tags=["product"])
@transaction.atomic(using='default')
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options = payload.dict()['product_options']
    product_display_line_id_list = list(payload.dict()['product_display_line_id'])
    if len(product_display_line_id_list) > 2:
        raise Exception(GlobalVar.ErrorMessage.DISPLAY_LINE_DONT_EXCEEDED_SIZE)  # 나중에 defaultReponse 만들기
    try:
        with transaction.atomic():
            product_queryset = Product.objects.create(**product)
            product_queryset.product_display_line.in_bulk(id_list=product_display_line_id_list)
            bulk_prepare_product_options_list = [ProductOptions(product=Product.objects.get(id=product_queryset.id),
                                                                **product_option) for product_option in product_options]
            ProductOptions.objects.bulk_create(bulk_prepare_product_options_list)
            bulk_prepare_file_list = [
                ProductImage(product=Product.objects.get(id=product_queryset.id), origin_image=file) for file in files]
            ProductImage.objects.bulk_create(bulk_prepare_file_list)

    except Exception as e:
        raise e


@router.get("/display_line",
            description="상품 진열 라인 조회",
            response={200: List[ProductDisplayLineSchema]},
            tags=["product"])
def get_display_line(request):
    qs = ProductDisplayLine.objects.all()
    return qs


@router.post("/display_line", description="상품 진열 라인 등록", tags=["product"])
def create_display_line(request, payload: ProductDisplayInsertSchema):
    display_line = payload.dict()
    ProductDisplayLine.objects.create(
        display_line_name=display_line['display_line_name']
    )


@router.put("/display_line", tags=["product"])
def modify_display_line_by_id(request, payload: ProductDisplayInsertSchema, id: int):
    qs = get_object_or_404(ProductDisplayLine, id=id)
    qs.objects.update(**payload.dict())


@router.delete("/display_line", tags=["product"])
def delete_display_line_by_id(request, id: int):
    get_object_or_404(ProductDisplayLine, id=id).delete()


@router.get("/vehicle", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"])
def get_vehicle_list(request):
    result = Vehicle.objects.prefetch_related('vehicle_color').all()
    return result


@router.get("/vehicle/{id}", description="pk로 모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"])
def get_vehicle_list_by_id(request, id: int):
    return get_object_or_404(Vehicle, id=id).objects.prefetch_related('vehicle_color').all()


@transaction.atomic(using='default')
@router.post("/vehicle", description="모터사이클 등록", tags=["vehicle"])
def create_vehicle(request, payload: VehicleInsertSchema):
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color', 'vehicle_image'}}
    vehicle_color = payload.dict().get('vehicle_color')
    vehicle_image = payload.dict().get('vehicle_image')

    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.create(**vehicle)
            for color in vehicle_color:
                VehicleColor.objects.create(
                    vehicle=Vehicle.objects.get(id=vehicle_queryset.id),
                    color_name=color['color_name'],
                    stock_count=color['stock_count'],
                    hex_code=color['hex_code'],
                    on_sale=color['on_sale'],
                    price=color['price']
                )
            for image in vehicle_image:
                VehicleImage.objects.create(
                    vehicle=Vehicle.objects.get(id=vehicle_queryset.id),
                    origin_image=image
                )
    except Exception as e:
        print(e)


@transaction.atomic(using='default')
@router.put("/vehicle", description="모터사이클 수정", tags=["vehicle"])
def modify_vehicle(request, payload: VehicleInsertSchema, id: int):
    payload_vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color', 'vehicle_image'}}
    payload_vehicle_color = payload.dict().get('vehicle_color')
    payload_vehicle_image = payload.dict().get('vehicle_image')

    vehicle = Vehicle.objects.filter(id=id)
    vehicle_color = VehicleColor.objects.filter(vehicle=id)
    vehicle_image = VehicleImage.objects.filter(vehicle=id)

    try:
        with transaction.atomic():
            vehicle.update(**payload_vehicle)
            vehicle_color.update_or_create(**payload_vehicle_color)
            vehicle_image.update_or_create(**payload_vehicle_image)
    except Exception as e:
        return e


@router.delete("/vehicle", description="모터사이클 수정", tags=["vehicle"])
def delete_vehicle(id: int):
    get_object_or_404(Vehicle, id=id).delete()


@router.delete("/vehicle_color/{id}", description="모터사이클 수정", tags=["vehicle"])
def delete_vehicle_color(id: int):
    get_object_or_404(VehicleColor, id=id).delete()
