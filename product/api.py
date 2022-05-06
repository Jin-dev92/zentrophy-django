from typing import List

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, Router, File

from conf.custom_exception import DisplayLineExceededSizeException, WrongParameterException
from product.constant import ProductListSort, ProductLabel
from product.models import Product, ProductDisplayLine, ProductOptions, ProductImage, Vehicle, VehicleColor, \
    VehicleImage
from product.schema import ProductListSchema, ProductInsertSchema, ProductDisplayLineSchema, ProductDisplayInsertSchema, \
    VehicleListSchema, VehicleInsertSchema
from util.file import base64_decode
from util.params import prepare_for_query

product_router = Router()
vehicle_router = Router()
display_line_router = Router()

current_product_sort = ProductListSort.CREATED_AT
product_option_exceed = 5
product_image_exceed = 5
vehicle_color_exceed = 5
vehicle_image_exceed = 5


@product_router.get("/",
                    description="상품 리스트 가져오기    생성 순 = 0, 판매량 순 = 1, 재고량 순 = 2 두번 호출 시 역순",
                    response=List[ProductListSchema],
                    tags=["product"],
                    auth=None
                    )
def get_product_list(request,
                     product_label: ProductLabel = ProductLabel.NEW,
                     display_line_id: int = None,
                     sold_out: bool = False,
                     sort: ProductListSort = ProductListSort.CREATED_AT
                     ):
    global current_product_sort
    params = prepare_for_query(request, ['sort', 'sold_out'])
    if sort == ProductListSort.CREATED_AT:
        field_name = "is_created"
    elif sort == ProductListSort.SALE_COUNT:
        field_name = 'productoptions__sale_count'
    elif sort == ProductListSort.STOCK_COUNT:
        field_name = 'productoptions__stock_count'
    else:
        raise WrongParameterException

    if current_product_sort == field_name:
        if field_name[0] != '-':
            field_name = '-' + field_name
        else:
            field_name = field_name[1:]

    current_product_sort = field_name

    if display_line_id:
        get_object_or_404(ProductDisplayLine, id=display_line_id)

    if sold_out:
        params['productoptions__stock_count'] = 0

    products = Product.objects.get_queryset(**params).prefetch_related(
        Prefetch('productoptions_set', to_attr='product_options'),
        Prefetch('productimage_set', to_attr='product_image'),
        'product_display_line',
    ).order_by(current_product_sort)
    return products


@transaction.atomic(using='default')
@product_router.post("/", description="상품 등록/수정 (수정 기능의 경우 id param 필수)", tags=["product"])
def create_product(request, payload: ProductInsertSchema, id: int = None, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options: list = payload.dict()['product_options']
    product_display_line_id_list = payload.dict()['product_display_line_id']
    global product_option_exceed
    global product_image_exceed
    if len(product_display_line_id_list) > 2:
        raise DisplayLineExceededSizeException
    try:
        with transaction.atomic():
            product_queryset = Product.objects.update_or_create(id=id, defaults=product)
            bulk_prepare_product_options_list = [
                ProductOptions(product=Product.objects.get(id=product_queryset[0].id),
                               **product_option) for product_option in product_options]
            bulk_prepare_file_list = [
                ProductImage(product=Product.objects.get(id=product_queryset[0].id), origin_image=file) for file in
                files]
            if not product_queryset[1]:
                for image in ProductImage.objects.get_queryset(product=product_queryset[0]):
                    image.soft_delete()
                for option in ProductOptions.objects.get_queryset(product=product_queryset[0]):
                    option.soft_delete()
            ProductOptions.objects.bulk_create(objs=bulk_prepare_product_options_list, batch_size=product_option_exceed)
            product_queryset[0].product_display_line.add(
                *ProductDisplayLine.objects.in_bulk(id_list=product_display_line_id_list)
            )
            ProductImage.objects.bulk_create(bulk_prepare_file_list, batch_size=product_image_exceed)
            product_queryset[0].save()
    except Exception as e:
        raise Exception(e)


@product_router.delete("/", description="상품 삭제", tags=["product"])
def delete_product(request, id: int):
    qs = get_object_or_404(Product, id=id).soft_delete()
    return qs


@display_line_router.get("/",
                         description="상품 진열 라인 조회",
                         response={200: List[ProductDisplayLineSchema]},
                         tags=["product"],
                         auth=None
                         )
def get_display_line(request):
    qs = ProductDisplayLine.objects.all()
    return qs


@display_line_router.post("/", description="상품 진열 라인 등록", tags=["product"])
def create_display_line(request, payload: ProductDisplayInsertSchema):
    ProductDisplayLine.objects.create(**payload.dict())


@display_line_router.put('/', description="상품 진열 라인 수정", tags=['product'])
def modify_display_line(request, payload: ProductDisplayInsertSchema, id: int):
    obj = get_object_or_404(ProductDisplayLine, id=id)
    for k, v in payload.dict().items():
        setattr(obj, k, v)
    obj.save()


@display_line_router.delete("/", tags=["product"])
def delete_display_line_by_id(request, id: int):
    return get_object_or_404(ProductDisplayLine, id=id).soft_delete()


@vehicle_router.get("/", description="모터 사이클 리스트", response={200: List[VehicleListSchema]}, auth=None)
def get_vehicle_list(request):
    params = prepare_for_query(request)
    result = Vehicle.objects.get_queryset(**params).prefetch_related(
        Prefetch(lookup='vehiclecolor_set',
                 queryset=VehicleColor.objects.get_queryset().prefetch_related(
                     Prefetch(lookup='vehicleimage_set', to_attr='vehicle_image')
                 ),
                 to_attr='vehicle_color')
    )
    return result


@vehicle_router.get("/{id}", description="모터 사이클 get by id", response={200: List[VehicleListSchema]},
                    auth=None)
def get_vehicle_by_id(request, id: int):
    result = Vehicle.objects.get_queryset(id=id).prefetch_related(
        Prefetch(lookup='vehiclecolor_set',
                 queryset=VehicleColor.objects.get_queryset().prefetch_related(
                     Prefetch(lookup='vehicleimage_set', to_attr='vehicle_image')
                 ),
                 to_attr='vehicle_color')
    )
    return result


@transaction.atomic(using='default')
@vehicle_router.post("/", description="모터 사이클 등록 / 수정")
def update_or_create_vehicle(request, payload: VehicleInsertSchema, id: int = None):
    global vehicle_color_exceed
    global vehicle_image_exceed
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color_params = payload.dict().get('vehicle_color')
    vehicle_color = [{k: v for k, v in color.items() if k not in {'files'}} for color in
                     vehicle_color_params]
    files_list = [color['files'] for color in vehicle_color_params]
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.update_or_create(id=id, defaults=vehicle)
            if not vehicle_queryset[1]:
                for color in vehicle_queryset[0].vehiclecolor_set.all():
                    color.soft_delete()

            color_bulk_create_list = VehicleColor.objects.bulk_create(
                objs=[VehicleColor(vehicle=vehicle_queryset[0], **color) for color in vehicle_color],
                batch_size=vehicle_color_exceed)
            if len(files_list) > 0:
                objs = []
                for idx, file_list in enumerate(files_list):
                    for file in file_list:
                        objs.append(
                            VehicleImage(vehicle_color=color_bulk_create_list[idx], origin_image=base64_decode(file)))
                VehicleImage.objects.bulk_create(
                    objs=objs,
                    batch_size=vehicle_color_exceed * vehicle_image_exceed
                )  # 최대 25개 생성

    except Exception as e:
        raise Exception(e)


# @transaction.atomic(using='default')
# @vehicle_router.post("/{id}", description="모터사이클 수정")
# def modify_vehicle(request, id: int, payload: VehicleInsertSchema):
#     global vehicle_color_exceed
#     global vehicle_image_exceed
#     target = Vehicle.objects.get_queryset(id=id)
#     vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
#     vehicle_color_params = payload.dict().get('vehicle_color')
#     vehicle_color = [{k: v for k, v in color.items() if k not in {'files'}} for color in
#                      vehicle_color_params]
#     files_list = [color['files'] for color in vehicle_color_params]
#     try:
#         with transaction.atomic():
#             target.update(**vehicle)
#             for color in VehicleColor.objects.get_queryset(vehicle_id=id):
#                 color.soft_delete()
#             for image in VehicleImage.objects.get_queryset(vehicle__vehiclecolor__id=id):
#                 image.soft_delete()
#
#             color_bulk_create_list = VehicleColor.objects.bulk_create(
#                 objs=[VehicleColor(vehicle_id=id, **color) for color in vehicle_color], batch_size=vehicle_color_exceed)
#             VehicleImage.objects.bulk_create(
#                 objs=[VehicleImage(vehicle_color=color, origin_image=base64_decode(file)) for color in
#                       color_bulk_create_list for file in files_list],
#                 batch_size=vehicle_color_exceed * vehicle_image_exceed
#             )
#
#     except Exception as a:
#         raise a


@vehicle_router.delete("/", description="모터사이클 삭제")
def delete_vehicle(id: int):
    queryset = get_object_or_404(Vehicle, id=id).soft_delete()
    return queryset
