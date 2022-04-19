from typing import List, Optional

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, Router, File
from ninja.responses import Response

from conf.custom_exception import DisplayLineExceededSizeException
from product.constant import ProductListSort
from product.models import Product, ProductDisplayLine, ProductOptions, ProductImage, Vehicle, VehicleColor, \
    VehicleImage
from product.schema import ProductListSchema, ProductInsertSchema, ProductDisplayLineSchema, ProductDisplayInsertSchema, \
    VehicleListSchema, VehicleInsertSchema
from util.default import ResponseDefaultHeader \
    # , CommonBase64FileSchema
from util.file import base64_decode
from util.params import prepare_for_query

product_router = Router()
vehicle_router = Router()
display_line_router = Router()

current_product_sort = ProductListSort.CREATED_AT
vehicle_color_size = 5
vehicle_image_size = 5


@product_router.get("/",
                    description="상품 리스트 가져오기    UPDATED_AT = 0, SALE = 1, STOCK_COUNT = 2, DISPLAY_LINE = 3",
                    response=List[ProductListSchema],
                    tags=["product"],
                    auth=None
                    )
def get_product_list(request, id: int = None, sort: ProductListSort = ProductListSort.CREATED_AT):
    params = prepare_for_query(request, ['sort'])
    if sort == ProductListSort.CREATED_AT:
        field_name = "is_created"
    elif sort == ProductListSort.SALE_COUNT:
        field_name = 'productoptions__sale_count'
    elif sort == ProductListSort.DISPLAY_LINE:
        field_name = 'productoptions__stock_count'
    elif sort == ProductListSort.DISPLAY_LINE:
        field_name = 'product_display_line__id'

    global current_product_sort
    # noinspection PyUnboundLocalVariable
    if current_product_sort == field_name:
        if field_name[0] != '-':
            field_name = '-' + field_name
        else:
            field_name = field_name[1:]
    else:
        pass
    current_product_sort = field_name
    # print(current_product_sort)

    products = Product.objects.get_queryset(**params).prefetch_related(
        Prefetch('productoptions_set', to_attr='product_options'),
        Prefetch('productimage_set', to_attr='product_image'),
        'product_display_line',
    ).order_by(current_product_sort)
    return products


@transaction.atomic(using='default')
@product_router.post("/", description="상품 등록/수정", tags=["product"], response=ResponseDefaultHeader.Schema)
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options: list = payload.dict()['product_options']
    product_display_line_id_list = payload.dict()['product_display_line_id']
    if len(product_display_line_id_list) > 2:
        raise DisplayLineExceededSizeException
    try:
        with transaction.atomic():
            product_queryset = Product.objects.update_or_create(**product)
            bulk_prepare_product_options_list = [
                ProductOptions(product=Product.objects.get(id=product_queryset[0].id),
                               **product_option) for product_option in product_options]
            bulk_prepare_file_list = [
                ProductImage(product=Product.objects.get(id=product_queryset[0].id), origin_image=file) for file in
                files]
            if product_queryset[1]:
                ProductOptions.objects.bulk_create(objs=bulk_prepare_product_options_list)
            else:
                # delete_files(files)
                # ProductImage.objects.get_queryset(product=product_queryset[0]).soft_delete()
                for image in ProductImage.objects.get_queryset(product=product_queryset[0]):
                    image.soft_delete()
                # product_queryset[0].objects.update(**product)
                if len(product_options) == 0:
                    # ProductOptions.objects.get_queryset(product=product_queryset[0]).soft_delete()
                    for option in ProductOptions.objects.get_queryset(product=product_queryset[0]):
                        option.soft_delete()
                else:
                    for option in product_options:
                        ProductOptions.objects.update_or_create(**option)
            product_queryset[0].product_display_line.add(
                *ProductDisplayLine.objects.in_bulk(id_list=product_display_line_id_list)
            )
            ProductImage.objects.bulk_create(bulk_prepare_file_list)
            product_queryset[0].save()
    except Exception as e:
        raise Exception(e)

    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 생성/수정이 성공적으로 되었습니다.",
        data=None
    )


@product_router.delete("/", description="상품 삭제", tags=["product"], response=ResponseDefaultHeader.Schema)
def delete_product(request, id: int):
    qs = get_object_or_404(Product, id=id).soft_delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
    )


@display_line_router.get("/",
                         description="상품 진열 라인 조회",
                         response={200: List[ProductDisplayLineSchema]},
                         tags=["product"],
                         auth=None
                         )
def get_display_line(request):
    qs = ProductDisplayLine.objects.all()
    return qs


@display_line_router.post("/", description="상품 진열 라인 등록", tags=["product"], response=ResponseDefaultHeader.Schema)
def create_display_line(request, payload: ProductDisplayInsertSchema):
    ProductDisplayLine.objects.create(**payload.dict())
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 진열 생성이 성공적으로 되었습니다.",
    )


@display_line_router.put('/', description="상품 진열 라인 수정", tags=['product'], response=ResponseDefaultHeader.Schema)
def modify_display_line(request, payload: ProductDisplayInsertSchema, id: int):
    obj = get_object_or_404(ProductDisplayLine, id=id)
    for k, v in payload.dict().items():
        setattr(obj, k, v)
    obj.save()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 진열 수정이 성공적으로 되었습니다.",
    )


@display_line_router.delete("/", tags=["product"], response=ResponseDefaultHeader.Schema)
def delete_display_line_by_id(request, id: int):
    get_object_or_404(ProductDisplayLine, id=id).soft_delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 진열 삭제가 성공적으로 되었습니다.",
    )


@vehicle_router.get("/", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"], auth=None)
def get_vehicle_list(request, id: Optional[int] = None):
    params = prepare_for_query(request)
    result = Vehicle.objects.get_queryset(**params).prefetch_related(
        Prefetch(lookup='vehiclecolor_set',
                 queryset=VehicleColor.objects.all().prefetch_related(
                     Prefetch(lookup='vehicle__vehicleimage_set',
                              to_attr='vehicle_image'
                              )
                 ),
                 to_attr='vehicle_color')
    )
    return result


@transaction.atomic(using='default')
@vehicle_router.post("/", description="모터사이클 등록/수정")
def create_vehicle(request, payload: VehicleInsertSchema):
    global vehicle_color_size
    global vehicle_image_size
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color_params = payload.dict().get('vehicle_color')
    vehicle_color = [{k: v for k, v in color.items() if k not in {'files'}} for color in
                     vehicle_color_params]
    files_list = [color['files'] for color in vehicle_color_params]
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.update_or_create(**vehicle)
            color_is_updated_or_created = [VehicleColor.objects.update_or_create(vehicle=vehicle_queryset[0], **color)
                                           # 선언 할 때마다 db에 hit 하는가?
                                           for color in vehicle_color]
            obj_image = [
                [VehicleImage(vehicle_color=color[0], origin_image=base64_decode(file)) for file in
                 files_list[idx]]
                for idx, color in enumerate(color_is_updated_or_created)
            ]
            if len(obj_image) > 0:
                for temp in obj_image:
                    VehicleImage.objects.bulk_create(objs=temp,
                                                     batch_size=vehicle_color_size * vehicle_image_size)  # 최대 25개 생성

    except Exception as e:
        raise Exception(e)
    return True


@vehicle_router.delete("/", description="모터사이클 삭제", response=ResponseDefaultHeader.Schema)
def delete_vehicle(id: int):
    qs = get_object_or_404(Vehicle, id=id).soft_delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
    )
