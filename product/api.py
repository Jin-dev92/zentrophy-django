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
    VehicleListSchema, VehicleInsertSchema, ProductOptionsInsertSchema

from util.default import ResponseDefaultHeader
from util.file import delete_files
from util.params import prepare_for_query

product_router = Router()
vehicle_router = Router()
display_line_router = Router()


# current_product_sort = ProductListSort.UPDATE_AT


@product_router.get("/",
                    description="상품 리스트 가져오기 sort 등록순: 0, 판매순 : 1 , 재고수량순: 2, 진열 라인 순: 3",
                    response=List[ProductListSchema],
                    tags=["product"],
                    auth=None
                    )
def get_product_list(request, sort: Optional[ProductListSort] = None, id: int = None):
    params = prepare_for_query(request, ['sort'])
    if sort == ProductListSort.RECENT:
        field_name = "is_created"
    elif sort == ProductListSort.LATEST:
        field_name = '-is_created'
    elif sort == ProductListSort.HIGH_SALE:
        field_name = 'productoptions__sale_count'
    elif sort == ProductListSort.LOW_SALE:
        field_name = '-productoptions__sale_count'
    elif sort == ProductListSort.HIGH_STOCK_COUNT:
        field_name = 'productoptions__stock_count'
    elif sort == ProductListSort.LOW_STOCK_COUNT:
        field_name = '-productoptions__stock_count'
    elif sort == ProductListSort.HIGH_DISPLAY_LINE:
        field_name = 'product_display_line__id'
    elif sort == ProductListSort.LOW_DISPLAY_LINE:
        field_name = "-product_display_line__id"
    else:
        field_name = "is_created"

    products = Product.objects.filter(**params).prefetch_related(
        Prefetch('productoptions_set', queryset=ProductOptions.objects.all(), to_attr='product_options'),
        Prefetch('productimage_set', queryset=ProductImage.objects.all(), to_attr='product_image'),
        'product_display_line',
    ).order_by(field_name)
    return products


@transaction.atomic(using='default')
@product_router.post("/", description="상품 등록/수정", tags=["product"], response=ResponseDefaultHeader.Schema)
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options: list = payload.dict()['product_options']
    product_options
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
                print("product 생성")
                ProductOptions.objects.bulk_create(objs=bulk_prepare_product_options_list)
            else:
                print("product 수정")
                delete_files(files)
                if len(product_options) == 0:
                    ProductOptions.objects.filter(product=get_object_or_404(Product, **product).delete())
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
    qs = get_object_or_404(Product, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
        data=qs
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


@display_line_router.post("/", description="상품 진열 라인 등록", tags=["product"])
def create_display_line(request, payload: ProductDisplayInsertSchema):
    ProductDisplayLine.objects.update_or_create(**payload.dict())


@display_line_router.delete("/", tags=["product"])
def delete_display_line_by_id(request, id: int):
    qs = get_object_or_404(ProductDisplayLine, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 진열 삭제가 성공적으로 되었습니다.",
        data=qs
    )


@vehicle_router.get("/", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"], auth=None)
def get_vehicle_list(request, id: Optional[int] = None):
    params = prepare_for_query(request)
    result = Vehicle.objects.filter(**params).prefetch_related(
        Prefetch('vehiclecolor_set', to_attr='vehicle_color'),
        Prefetch('vehicleimage_set', to_attr='vehicle_image'),
    )
    return result


@transaction.atomic(using='default')
@vehicle_router.post("/", description="모터사이클 등록", response=ResponseDefaultHeader.Schema)
def create_vehicle(request, payload: VehicleInsertSchema, files: List[UploadedFile] = None):
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color = payload.dict().get('vehicle_color')
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.update_or_create(**vehicle)
            color_list_for_bulk: list = [
                VehicleColor(vehicle=Vehicle.objects.get(id=vehicle_queryset[0].id), **color) for color in
                vehicle_color
            ]
            image_list_for_bulk: list = [
                VehicleImage(vehicle=Vehicle.objects.get(id=vehicle_queryset[0].id), origin_image=file) for file in
                files
            ]
            if vehicle_queryset[1]:
                VehicleColor.objects.bulk_create(objs=color_list_for_bulk)
            else:
                delete_files(files)  # async func

                VehicleColor.objects.bulk_update(objs=color_list_for_bulk, fields=VehicleInsertSchema.vehicle_color)
            VehicleImage.objects.bulk_create(objs=image_list_for_bulk)
            vehicle_queryset[0].save()
    except Exception as e:
        raise Exception(e)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="모터사이클이 성공적으로 추가 되었습니다"
    )


@vehicle_router.delete("/", description="모터사이클 수정", response=ResponseDefaultHeader.Schema)
def delete_vehicle(id: int):
    qs = get_object_or_404(Vehicle, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
        data=qs
    )
