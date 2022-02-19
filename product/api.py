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


@transaction.atomic(using='default')
@product_router.post("/", description="상품 등록", tags=["product"], response=ResponseDefaultHeader.Schema)
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = None):
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
@product_router.put("/", description="상품 수정, @todo files 관련 이슈로 디버깅 필요", response=ResponseDefaultHeader.Schema)
def modify_product(request, id: int, payload: ProductInsertSchema):
    try:
        with transaction.atomic():
            product_list = Product.objects.filter(id=id)
            product_queryset = get_object_or_404(Product, id=id)
            product_params = {k: v for k, v in payload.dict().items() if
                              k not in {'product_display_line_id', 'product_options'}}

            product_list.update(**product_params)
            try:
                product_queryset.product_display_line.all().delete()
                product_queryset.productoptions_set.all().delete()
            except Exception as e:
                raise Exception(e)
            finally:
                product_queryset.product_display_line.in_bulk([payload.dict().get('product_display_line_id')])
                product_queryset.productoptions_set.bulk_create(
                    objs=[ProductOptions(product=product_queryset, **option) for option in
                          payload.dict().get('product_options')]
                )
    except Exception as e:
        raise Exception(e)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 수정이 성공적으로 되었습니다."
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
            vehicle_queryset = Vehicle.objects.create(**vehicle)
            VehicleColor.objects.bulk_create([
                VehicleColor(vehicle=Vehicle.objects.get(id=vehicle_queryset.id), **color) for color in vehicle_color
            ])
            VehicleImage.objects.bulk_create([
                VehicleImage(vehicle=Vehicle.objects.get(id=vehicle_queryset.id), origin_image=file) for file in files
            ])
    except Exception as e:
        raise Exception(e)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="모터사이클이 성공적으로 추가 되었습니다"
    )


@transaction.atomic(using='default')
@vehicle_router.put("/", description="모터사이클 수정 @todo 기능오류있음", response=ResponseDefaultHeader.Schema)
def modify_vehicle(request, payload: VehicleInsertSchema):
    vehicle_field = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color_field = payload.dict().get('vehicle_color')
    vehicle = get_object_or_404(Vehicle, id=id)
    try:
        with transaction.atomic():
            Vehicle.objects.filter(id=id).update(**vehicle_field)
            try:
                vehicle.vehiclecolor_set.all().delete()
            except Exception as e:
                raise Exception(e)
            finally:
                VehicleColor.objects.bulk_create(
                    [VehicleColor(vehicle=vehicle, **color) for color in vehicle_color_field])
            # if files is None:
            #     VehicleImage.objects.filter(vehicle=vehicle).delete()
            # else:
            #     for file in files:
            #         VehicleImage.objects.update_or_create(*file)
    except Exception as e:
        raise Exception(e)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="모터사이클이 성공적으로 수정되었습니다."
    )


@vehicle_router.delete("/", description="모터사이클 수정", response=ResponseDefaultHeader.Schema)
def delete_vehicle(id: int):
    qs = get_object_or_404(Vehicle, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
        data=qs
    )
