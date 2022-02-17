from typing import List, Optional

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, File, Router
from ninja.responses import Response
from conf.message import DISPLAY_LINE_DONT_EXCEEDED_SIZE
from product.constant import ProductListSort, ProductOptionsLabel
from product.models import Product, ProductDisplayLine, ProductOptions, ProductImage, Vehicle, VehicleColor, \
    VehicleImage
from product.schema import ProductListSchema, ProductInsertSchema, ProductDisplayLineSchema, ProductDisplayInsertSchema, \
    VehicleListSchema, VehicleInsertSchema
from util.default import ResponseDefaultHeader
from util.params import prepare_for_query

product_router = Router()
vehicle_router = Router()
display_line_router = Router()
current_product_sort = ProductListSort.UPDATE_AT


@product_router.get("/",
                    description="상품 리스트 가져오기 sort 등록순: 0, 판매순 : 1 , 재고수량순: 2, 진열 라인 순: 3",
                    response=List[ProductListSchema],
                    # response=ResponseDefaultHeader.Schema,
                    tags=["product"]
                    )
def get_product_list(request, sort: Optional[ProductListSort] = None, id: int = None):
    params = prepare_for_query(request, ['sort'])
    global current_product_sort
    if sort == ProductListSort.UPDATE_AT:
        field_name = "is_created"
    elif sort == ProductListSort.SALE:
        field_name = "productoptions__sale_count"
    elif sort == ProductListSort.STOCK_COUNT:
        field_name = "productoptions__stock_count"
    elif sort == ProductListSort.DISPLAY_LINE:
        field_name = "product_display_line__id"
    else:
        field_name = "is_created"

    if sort == current_product_sort:
        field_name = "-" + field_name
    else:
        current_product_sort = sort

    products = Product.objects.prefetch_related(
        Prefetch('productoptions_set', queryset=ProductOptions.objects.all(), to_attr='product_options'),
        Prefetch('productimage_set', queryset=ProductImage.objects.all(), to_attr='product_image'),
        'product_display_line',
    ).filter(**params).order_by(field_name)
    return products
    # return ResponseDefaultHeader(
    #     code=Response.status_code,
    #     data=products
    # )


@transaction.atomic(using='default')
@product_router.post("/", description="상품 등록", tags=["product"], response=ResponseDefaultHeader.Schema)
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options = payload.dict()['product_options']
    product_display_line_id_list = list(payload.dict()['product_display_line_id'])
    if len(product_display_line_id_list) > 2:
        raise Exception(DISPLAY_LINE_DONT_EXCEEDED_SIZE)
    try:
        with transaction.atomic():
            product_queryset = Product.objects.create(**product)
            product_queryset.product_display_line.in_bulk(id_list=product_display_line_id_list)
            bulk_prepare_product_options_list = [ProductOptions(product=Product.objects.get(id=product_queryset.id),
                                                                **product_option) for product_option in product_options]
            bulk_prepare_file_list = [
                ProductImage(product=Product.objects.get(id=product_queryset.id), origin_image=file) for file in files]
            ProductOptions.objects.bulk_create(bulk_prepare_product_options_list)
            ProductImage.objects.bulk_create(bulk_prepare_file_list)

    except Exception as e:
        raise Exception(e)
    finally:
        return ResponseDefaultHeader(
            code=Response.status_code,
            message="상품 생성이 성공적으로 되었습니다.",
            data=None
        )


@transaction.atomic(using='default')
@product_router.put("/", description="상품 수정", tags=["product"])
def modify_product(request, payload: ProductInsertSchema, id: int, files: List[UploadedFile] = File(...)):
    try:
        with transaction.atomic():
            product = get_object_or_404(Product, id=id)
            product_params = {k: v for k, v in payload.dict().items() if
                              k not in {'product_display_line_id', 'product_options'}}
            product.objects.update(**product_params)
            bulk_prepare_product_options_list = [ProductOptions(product=product.id, **payload.dict()['product_options'])
                                                 for
                                                 product_option in payload.dict()['product_options']]
            product.product_display_line.bulk_update(payload.dict()['product_display_line_id'])  # product_display_line
            product.product_options.bulk_update(bulk_prepare_product_options_list)
            ProductImage.objects.filter(product=product.id).bulk_update(files)
    except Exception as e:
        raise Exception(e)


@product_router.delete("/", description="상품 삭제", tags=["product"])
def delete_product(request, id: int):
    get_object_or_404(Product, id=id).delete()


@display_line_router.get("/",
                         description="상품 진열 라인 조회",
                         response={200: List[ProductDisplayLineSchema]},
                         tags=["product"])
def get_display_line(request):
    qs = ProductDisplayLine.objects.all()
    return qs


@display_line_router.post("/", description="상품 진열 라인 등록", tags=["product"])
def create_display_line(request, payload: ProductDisplayInsertSchema):
    display_line = payload.dict()
    ProductDisplayLine.objects.create(
        display_line_name=display_line['display_line_name']
    )


@display_line_router.put("/", tags=["product"])
def modify_display_line_by_id(request, payload: ProductDisplayInsertSchema, id: int):
    qs = get_object_or_404(ProductDisplayLine, id=id)
    qs.objects.update(**payload.dict())


@display_line_router.delete("/", tags=["product"])
def delete_display_line_by_id(request, id: int):
    get_object_or_404(ProductDisplayLine, id=id).delete()


@vehicle_router.get("/", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"])
def get_vehicle_list(request, id: Optional[int] = None):
    params = dict()
    if id is not None:
        params['id'] = id

    result = Vehicle.objects.filter(**params).prefetch_related('vehicle_color').all()
    return result


@transaction.atomic(using='default')
@vehicle_router.post("/", description="모터사이클 등록")
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
@vehicle_router.put("/", description="모터사이클 수정")
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


@vehicle_router.delete("/", description="모터사이클 수정")
def delete_vehicle(id: int):
    get_object_or_404(Vehicle, id=id).delete()

# @vehicle_router.delete("/vehicle_color", description="모터사이클 수정")
# def delete_vehicle_color(id: int):
#     get_object_or_404(VehicleColor, id=id).delete()
