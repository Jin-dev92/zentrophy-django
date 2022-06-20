from typing import List

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, Router, File

import conf.settings
from conf.custom_exception import DisplayLineExceededSizeException, WrongParameterException, \
    UserNotAccessDeniedException
from product.constant import ProductListSort, ProductLabel
from product.models import Product, ProductDisplayLine, ProductOptions, ProductImage, Vehicle, VehicleColor, \
    VehicleImage
from product.schema import ProductListSchema, ProductInsertSchema, ProductDisplayLineSchema, ProductDisplayInsertSchema, \
    VehicleListSchema, VehicleInsertSchema
from util.params import prepare_for_query
from util.permission import is_admin

product_router = Router()
vehicle_router = Router()
display_line_router = Router()

current_product_sort = ProductListSort.CREATED_AT


@product_router.get("/",
                    response=List[ProductListSchema],
                    tags=["product"],
                    auth=None
                    )
def get_product_list(request,
                     product_label: ProductLabel = ProductLabel.NEW,
                     # product_display_line_id: int = None,
                     sold_out: bool = False,
                     sort: ProductListSort = ProductListSort.CREATED_AT
                     ):
    """
    상품 리스트 가져 오는 API
    두번 호출 시 현재 설정의 역순 으로 호출 된다.
    - :param product_label:  HOT = 0, NEW = 1, SALE = 2, BEST = 3
    - :param sold_out: 재고량 유무
    - :param sort: CREATED_AT(생성순) = 0, SALE_COUNT(판매량 순) = 1, STOCK_COUNT(재고량 순) = 2
    - :return: list
    """
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

    # if product_display_line_id:
    #     get_object_or_404(ProductDisplayLine, id=product_display_line_id)

    if sold_out:
        params['productoptions__stock_count'] = 0
    products = Product.objects.get_queryset(**params).prefetch_related(
        Prefetch('productoptions_set', to_attr='product_options'),
        Prefetch('productimage_set', to_attr='product_image'),
        'product_display_line',
    ).order_by(current_product_sort)
    return products


@transaction.atomic(using='default')
@product_router.post("/",
                     tags=["product"])
def update_or_create_product(request, payload: ProductInsertSchema, id: int = None, files: List[UploadedFile] = File(...)):
    """
    상품 등록/수정
    - :param id: 수정일 경우 파라 미터에 추가 하여 보내 준다.
    - :param files: 상품에 첨부 되는 이미지 파일
    - :return: none
    """
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options: list = payload.dict()['product_options']
    product_display_line_id_list = payload.dict()['product_display_line_id']
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
            ProductOptions.objects.bulk_create(objs=bulk_prepare_product_options_list, batch_size=conf.settings.product_option_exceed)
            product_queryset[0].product_display_line.add(
                *ProductDisplayLine.objects.in_bulk(id_list=product_display_line_id_list)
            )
            ProductImage.objects.bulk_create(bulk_prepare_file_list, batch_size=conf.settings.product_image_exceed)
            product_queryset[0].save()
    except Exception as e:
        raise Exception(e)


@product_router.delete("/", description="상품 삭제", tags=["product"])
def delete_product(request, id: int):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
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
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    ProductDisplayLine.objects.create(**payload.dict())


@display_line_router.put('/', description="상품 진열 라인 수정", tags=['product'])
def modify_display_line(request, payload: ProductDisplayInsertSchema, id: int):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    obj = get_object_or_404(ProductDisplayLine, id=id)
    for k, v in payload.dict().items():
        setattr(obj, k, v)
    obj.save()


@display_line_router.delete("/", tags=["product"])
def delete_display_line_by_id(request, id: int):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
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
        Prefetch(
            lookup='vehiclecolor_set',
            queryset=VehicleColor.objects.get_queryset().prefetch_related(
                Prefetch(lookup='vehicleimage_set', to_attr='vehicle_image')
            ),
            to_attr='vehicle_color')
    )
    return result


@transaction.atomic(using='default')
@vehicle_router.post("/")
def update_or_create_vehicle(request, payload: VehicleInsertSchema, id: int = None,
                             color_file_0: List[UploadedFile] = None,
                             color_file_1: List[UploadedFile] = None,
                             color_file_2: List[UploadedFile] = None,
                             color_file_3: List[UploadedFile] = None,
                             color_file_4: List[UploadedFile] = None,
                             ):
    """
    모터 사이클 등록 / 수정, 각각의 vehicle_color 당 5개의 이미지 파일을 첨부 할 수 있다.
    - :param id: 수정일 경우 id 를 파라 미터에 넣어서 보내 준다.
    - :param color_file_0: 첫번째 vehicle_color 에서 사용 할 이미지 파일을 넣어 준다.
    - :param color_file_1: 두번째 vehicle_color 에서 사용 할 이미지 파일을 넣어 준다.
    - :param color_file_2: 세번째 vehicle_color 에서 사용 할 이미지 파일을 넣어 준다.
    - :param color_file_3: 네번째 vehicle_color 에서 사용 할 이미지 파일을 넣어 준다.
    - :param color_file_4: 다섯 번째 vehicle_color 에서 사용 할 이미지 파일을 넣어 준다.
    - :return: none
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    vehicle_color_params = payload.dict().get('vehicle_color')
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.update_or_create(id=id, defaults=vehicle)
            if not vehicle_queryset[1]:  # 수정
                for color in vehicle_queryset[0].vehiclecolor_set.all():
                    color.soft_delete()

            for idx, color in enumerate(vehicle_color_params):
                vc = VehicleColor.objects.create(vehicle=vehicle_queryset[0], **color)
                file_list = request.FILES.getlist('color_file_' + str(idx))
                if file_list:
                    for image in file_list:
                        VehicleImage.objects.create(vehicle_color=vc, origin_image=image)

            # color_bulk_create_list = VehicleColor.objects.bulk_create( # 로컬에서는 작동하는데 서버에서는 의도한 대로 작동하지 않아 임시 주석처리
            #     objs=[VehicleColor(vehicle=vehicle_queryset[0], **color) for color in vehicle_color_params],
            #     batch_size=vehicle_color_exceed)
            #
            # for color in color_bulk_create_list:  # 로컬에서 에러 나지 않지만, 서버에서는 나서 넣은 코드. 디버그모드에서는 에러를 무시 하는 듯
            #     color.save()
            #
            # for idx, color in enumerate(color_bulk_create_list):
            #     file_list = request.FILES.getlist('color_file_' + str(idx))
            #     if file_list:
            #         objs = [VehicleImage(vehicle_color=color, origin_image=image) for image in file_list]
            #         VehicleImage.objects.bulk_create(objs=objs, batch_size=vehicle_image_exceed)
            # )  # 최대 25개 생성

    except Exception as e:
        raise Exception(e)


@vehicle_router.delete("/", description="모터사이클 삭제")
def delete_vehicle(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    get_object_or_404(Vehicle, id=id).soft_delete()
