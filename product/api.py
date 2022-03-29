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
        Prefetch('productoptions_set', to_attr='product_options'),
        Prefetch('productimage_set', to_attr='product_image'),
        'product_display_line',
    ).order_by(field_name)
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
                delete_files(files)
                ProductImage.objects.filter(product=product_queryset[0]).delete()
                # product_queryset[0].objects.update(**product)
                if len(product_options) == 0:
                    ProductOptions.objects.filter(product=product_queryset[0]).delete()
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
    get_object_or_404(ProductDisplayLine, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 진열 삭제가 성공적으로 되었습니다.",
    )


@vehicle_router.get("/", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"], auth=None)
def get_vehicle_list(request, id: Optional[int] = None):
    params = prepare_for_query(request)
    result = Vehicle.objects.filter(**params).prefetch_related(
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
def create_vehicle(request, payload: VehicleInsertSchema,
                   files1: List[UploadedFile] = None,
                   files2: List[UploadedFile] = None,
                   files3: List[UploadedFile] = None,
                   files4: List[UploadedFile] = None,
                   files5: List[UploadedFile] = None,
                   ):
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color: list[dict] = payload.dict().get('vehicle_color')
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.update_or_create(**vehicle)
            for idx, color in enumerate(vehicle_color):
                obj = VehicleColor.objects.update_or_create(vehicle=vehicle_queryset[0], **color)
                if idx == 0:
                    file_list = files1
                elif idx == 1:
                    file_list = files2
                elif idx == 2:
                    file_list = files3
                elif idx == 3:
                    file_list = files4
                elif idx == 4:
                    file_list = files5
                else:
                    raise ValueError('vehicle_color 갯수가 잘못됨.')
                if len(file_list) > 0:
                    image_list: list = [
                        VehicleImage(vehicle_color=obj[0], origin_image=file) for file in file_list
                    ]
                    VehicleImage.objects.bulk_create(obj=image_list, batch_size=5)
                else:
                    if not obj[1]:  # 수정일 경우 삭제해준다.
                        exist_image = VehicleImage.objects.filter(vehicle_color=obj[0])
                        exist_image.delete()
                        delete_files([image.origin_image for image in exist_image])
                    else:  # 생성인 경우 패스해줌
                        pass

    except Exception as e:
        raise Exception(e)
    if vehicle_queryset[1]:
        return_val = "추가"
    else:
        return_val = "수정"

    return ResponseDefaultHeader(
        code=Response.status_code,
        message="모터사이클이 성공적으로 {} 되었습니다".format(return_val)
    )


@vehicle_router.delete("/", description="모터사이클 삭제", response=ResponseDefaultHeader.Schema)
def delete_vehicle(id: int):
    qs = get_object_or_404(Vehicle, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="상품 삭제가 성공적으로 되었습니다.",
    )
