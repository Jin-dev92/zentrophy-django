from typing import List

from django.db import transaction
from django.db.models import F
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import AlreadyExistsException, WrongParameterException, \
    NotEnoughStockException, UserNotAccessDeniedException, OrderStateCantChangeException, IncorrectTotalAmountException, \
    MustHaveDeliveryToException, IncorrectOrderStateException
from conf.settings import upload_exceed_count
from member.models import OwnedVehicle
from order.constant import OrderState, DeliveryMethod
from order.models import Order, Subside, DocumentFile, ExtraSubside, OrderedProductOptions, OrderedVehicleColor, \
    OrderLocationInfo, CustomerInfo, DocumentFormat, DeliveryTo, ProductDeliveryInfo
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema, \
    DocumentFormatListSchema, ApplySubSideSchema, DeliveryMethodInputSchema, ProductDeliveryInfoCreateSchema
from product.models import ProductOptions, VehicleColor
from util.number import check_invalid_product_params, generate_release_number
from util.permission import is_admin

router = Router()
subside_router = Router()
file_router = Router()


@router.get('/', response=List[OrderListSchema])
def get_order_list(request):
    """
    주문 목록 API
    어드민은 모든 주문 목록을 가져 오며, 일반 유저는 본인이 주문한 주문만 가져 온다.
    """
    if is_admin(request.auth):
        target = Order.objects.get_queryset()
    else:
        target = Order.objects.get_queryset(owner=request.auth)

    queryset = target.prefetch_related(
        'customer_info',
        'order_location_info',
        Prefetch(lookup='orderedproductoptions_set',
                 queryset=OrderedProductOptions.objects.select_related('product_options')
                 .annotate(product_image=F('product_options__product__productimage__origin_image')),
                 to_attr="ordered_product_options"),
        Prefetch(lookup='orderedvehiclecolor_set',
                 queryset=OrderedVehicleColor.objects.select_related('vehicle_color')
                 .prefetch_related(Prefetch('vehicle_color__vehicleimage_set', to_attr='vehicle_image')),
                 to_attr="ordered_vehicle_color"),
        Prefetch(lookup='documentfile_set', to_attr="files"),
    )

    return queryset


@router.get('/{id}',
            response=List[OrderListSchema])
def get_order_list_by_id(request, id: int):
    """
    주문 목록 API
    어드민은 모든 주문 목록을 가져 오며, 일반 유저는 본인이 주문한 주문만 가져 온다.
    """
    if is_admin(request.auth):
        target = Order.objects.get_queryset(id=id)
    else:
        target = Order.objects.get_queryset(id=id, owner=request.auth)

    queryset = target.prefetch_related(
        'customer_info',
        'order_location_info',
        Prefetch(lookup='orderedproductoptions_set',
                 queryset=OrderedProductOptions.objects.select_related('product_options')
                 .annotate(product_image=F('product_options__product__productimage__origin_image')),
                 to_attr="ordered_product_options"),
        Prefetch(lookup='orderedvehiclecolor_set',
                 queryset=OrderedVehicleColor.objects.select_related('vehicle_color')
                 .prefetch_related(Prefetch('vehicle_color__vehicleimage_set', to_attr='vehicle_image')),
                 to_attr="ordered_vehicle_color"),
        Prefetch(lookup='documentfile_set', to_attr="files"),
    )
    return queryset


@router.post('/delivery_method/{id}')
def delivery_method_input(request, id: int, payload: DeliveryMethodInputSchema):
    """
    모터 사이클 주문의 배달 정보 입력
    - :param id: 주문 id
    - :return:
    """
    params = payload.dict()
    delivery_method = params['delivery_method']
    delivery_to: dict = params['delivery_to']
    place_remote_pk = params['place_remote_pk']

    if delivery_method == DeliveryMethod.DEPEND_ON and not delivery_to:
        raise MustHaveDeliveryToException
    if delivery_method == DeliveryMethod.YOURSELF and not place_remote_pk:
        raise MustHaveDeliveryToException

    target = get_object_or_404(Order, id=id, owner=request.auth)
    target.delivery_method = delivery_method
    if delivery_method == DeliveryMethod.DEPEND_ON:
        target.delivery_to = DeliveryTo.objects.create(**delivery_to)
    else:
        target.place_remote_pk = place_remote_pk

    target.save(update_fields=['delivery_method', 'delivery_to', 'place_remote_pk'])


@router.post('/apply_subsides/{id}')
def apply_subsides_to_order(request, payload: ApplySubSideSchema, id: int):
    """
    주문에 보조금을 적용 하는 API, 기본 보조금은 주문한 모터사이클이 기본 보조금을 지원하는 상품이며, 유저가 기본 보조금을 원할 떄 적용 된다.
    - :param id: 주문 id
    - :return:
    """
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    try:
        discount = 0    # 1대당 할인 금액

        target = get_object_or_404(Order, id=id)
        extra_bulk = ExtraSubside.objects.in_bulk(id_list=payload.dict()['extra_subside'])
        # 1대당 할인 금액 계산
        for ordered_vehicle in target.orderedvehiclecolor_set.all():
            if ordered_vehicle.vehicle_color.vehicle.able_subsidy and target.customer_info.is_apply_subside:   # 기본 보조금 계산
                discount += Subside.objects.all().first().amount * ordered_vehicle.amount

            if ordered_vehicle.vehicle_color.vehicle.able_extra_subsidy and target.customer_info.is_apply_subside:
                for extra_id in extra_bulk:
                    discount += ExtraSubside.objects.get(id=extra_id).amount * ordered_vehicle.amount

        target.total -= discount
        target.discount_total = discount
        if target.total < 0:
            target.total = 0
        target.save(update_fields=['total', 'discount_total'])

    except Exception as e:
        raise e


@router.post('/is_request_submit/{id}')
def change_is_request_submit(request, id: int):
    """
    서류 재접수 토글, 해당 주문이 서류 검토 단계에 있을 때, 서류 재검토 기능을 이용 하기 위한 API
    - :param id: 주문 id
    - :return:
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    target = get_object_or_404(Order, id=id)
    if target.state != OrderState.REVIEW_DOCS:
        raise IncorrectOrderStateException
    target.is_request_submit = not target.is_request_submit
    target.save(update_fields=['is_request_submit'])


@transaction.atomic(using='default')
@router.post('/is_delivery/{id}')
def change_is_delivery(request, id: int):
    """
    출고 준비 -> 배송중, 배송중 -> 출고 준비 상태 토글, 배송 준비 단계 에서 배송 중일 때와 출고 준비를 분별 하기 위한 값을 토글 해준다.
    배송 중으로 변했을 경우, 출고 번호와 유저 에게 모터 사이클 소유 목록 부여 한다.
    - :param id: 주문 아이디
    - :return:
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException

    target = get_object_or_404(Order, id=id)
    if target.state != OrderState.PREPARE_DELIVERY:
        raise IncorrectOrderStateException
    try:
        with transaction.atomic():
            if not target.is_delivery:
                for ordered_vehicle in target.orderedvehiclecolor_set.all():
                    print(ordered_vehicle.amount)
                    for i in range(ordered_vehicle.amount):
                        release_number = generate_release_number()
                        is_pass = len(OwnedVehicle.objects.filter(release_number__exact=release_number)) == 0
                        if is_pass:
                            OwnedVehicle.objects.create(user=request.auth,
                                                        order=target,
                                                        vehicle_color=ordered_vehicle.vehicle_color,
                                                        release_number=release_number)

            target.is_delivery = not target.is_delivery
            target.save(update_fields=['is_delivery'])
            # 출고 되었을 경우, 유저가 소유한 모터사이클 목록 추가 후 출고 번호를 적어준다.
    except Exception as e:
        raise e


@transaction.atomic(using='default')
@router.post('/')
def update_or_create_order(request, payload: OrderCreateSchema, id: int = None):
    """
    주문 생성 / 수정
    - :param id: 주문 아이디, 수정 할 때 파라 미터에 같이 보내 준다.
    - :return:
    """
    if not is_admin(request.auth) and (id and id > -1):  # 일반 유저가 id 를 보냈을 경우에 예외 처리 해준다.
        raise UserNotAccessDeniedException
    try:
        with transaction.atomic():
            params = payload.dict()
            order_params = {k: v for k, v in params.items() if
                            k not in {'ordered_product_options', 'ordered_vehicle_color', 'extra_subside',
                                      'customer_info', 'order_location_info'}
                            }
            order_location_info_params = params['order_location_info']
            customer_info_params = params['customer_info']
            extra_subside_params: list = params.get('extra_subside')

            ordered_vehicle_color = params['ordered_vehicle_color']
            ordered_product_options = params['ordered_product_options']
            total = params['total']

            if id and id > -1:  # 수정 로직 수행 전 데이터 세팅
                target = get_object_or_404(Order, id=id)
                # 수정이면 갖고 있던 foreign_key 데이터를 삭제한다.
                target.extra_subside.remove()
                target.customer_info.delete()
                target.order_location_info.delete()
                target.orderedproductoptions_set.all().delete()
                target.orderedvehiclecolor_set.all().delete()
                order_params['owner'] = target.owner
            else:   # 생성 로직 수행 전 데이터 세팅
                target = None
                order_params['owner'] = request.auth

            customer_object = CustomerInfo.objects.update_or_create(order=target, defaults=customer_info_params)
            location_object = OrderLocationInfo.objects.update_or_create(order=target, defaults=order_location_info_params)

            order_params['customer_info'] = customer_object[0]
            order_params['order_location_info'] = location_object[0]

            order_queryset = Order.objects.update_or_create(id=id, defaults=order_params)  # 주문 생성

            if extra_subside_params and len(extra_subside_params) > 0 and extra_subside_params.count(0) == 0:
                order_queryset[0].extra_subside.add(
                    *ExtraSubside.objects.in_bulk(id_list=params.get('extra_subside')))  # manytomany field

            if ordered_product_options and len(ordered_product_options) > 0:    #   주문한 상품이 존재할 경우
                if not check_invalid_product_params(ordered_product_options):     # 파라미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                acc_total = 0   # 가격 검증을 위한 변수
                for index, po in enumerate(ordered_product_options):    # 상품 주문 생성 시 판매량, 재고량 조절
                    po_target = get_object_or_404(ProductOptions, id=po.get('product_options_id'))
                    acc_total += po_target.product.product_price * po.get('amount')
                    if po.get('amount') > po_target.stock_count:
                        raise NotEnoughStockException
                    po_target.sale_count = po_target.sale_count + po.get('amount')
                    po_target.stock_count = po_target.stock_count - po.get('amount')
                    po_target.save(update_fields=['sale_count', 'stock_count'])

                if total != acc_total:  # 가격 검증의 결과와 요청한 금액이 맞지 않을 때 에러를 띄워 준다.
                    raise IncorrectTotalAmountException

                po_list = OrderedProductOptions.objects.bulk_create(
                    objs=[
                        OrderedProductOptions(**ordered_po,
                                              order=order_queryset[0])
                        for ordered_po in ordered_product_options]
                )

            elif ordered_vehicle_color and len(ordered_vehicle_color) > 0:  #   주문한 모터 사이클이 존재할 경우
                if not check_invalid_product_params(ordered_vehicle_color): # 파라 미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                acc_total = 0   # 가격 검증을 위한 변수
                for index, vc in enumerate(ordered_vehicle_color):  # 모터 사이클 주문 생성시 판매량, 재고량 조절
                    vc_target = get_object_or_404(VehicleColor, id=vc.get('vehicle_color_id'))
                    acc_total += vc_target.price * vc.get('amount')
                    if vc.get('amount') > vc_target.stock_count:
                        raise NotEnoughStockException
                    vc_target.sale_count = vc_target.sale_count + vc.get('amount')
                    vc_target.stock_count = vc_target.stock_count - vc.get('amount')
                    vc_target.save(update_fields=['sale_count', 'stock_count'])

                if total != acc_total:  # 가격 검증의 결과와 요청한 금액이 맞지 않을 때 에러를 띄워 준다.
                    raise IncorrectTotalAmountException

                vc_list = OrderedVehicleColor.objects.bulk_create(
                    objs=[OrderedVehicleColor(**ordered_vc, order=order_queryset[0]) for ordered_vc in ordered_vehicle_color])

            else:
                raise WrongParameterException

    except Exception as e:
        raise e


@router.put('/')
def change_order_state(request, id: int, state: OrderState):
    """
    주문 상태 수정
    - :param id: 주문 아이디
    - :param state:
    ACCEPT_ORDER(주문 접수) = 0
    REVIEW_DOCS(서류 검토) = 1
    WAIT_PAYMENT(결제 대기) = 2
    PREPARE_DELIVERY(배달 준비) = 3
    IS_COMPLETE(완료됨) = 4
    IS_CANCELED(취소됨) = 5
    - :return:
    """
    # orderState가 3일 경우 유저 접근 가능하도록.
    if not is_admin(request.auth):  # 어드민 접근 제한
        if state != OrderState.PREPARE_DELIVERY:
            raise UserNotAccessDeniedException

    try:
        target = get_object_or_404(Order, id=id)
        if target.state == OrderState.IS_CANCELED:
            raise OrderStateCantChangeException
        if target.state > OrderState.REVIEW_DOCS and target.is_request_submit:
            target.is_request_submit = False
        if state == OrderState.PREPARE_DELIVERY:
            target.is_delivery = False   # 출고 준비 중

        target.state = state
        target.save(update_fields=['state', 'is_request_submit'])

        if state == OrderState.IS_CANCELED:  # 주문 취소 하였을 때 재고량과 판매량을 원복 해줘야 한다.
            ordered_product_options = target.orderedproductoptions_set.all()
            ordered_vehicle_colors = target.orderedvehiclecolor_set.all()

            if len(ordered_product_options) > 0:
                for ordered_product_option in ordered_product_options:
                    amount = ordered_product_option.amount
                    ordered_product_option.product_options.stock_count += amount
                    ordered_product_option.product_options.sale_count -= amount

                    if ordered_product_option.product_options.sale_count < 0:
                        ordered_product_option.product_options.sale_count = 0
                    ordered_product_option.product_options.save(update_fields=['stock_count', 'sale_count'])

            elif len(ordered_vehicle_colors) > 0:
                for ordered_vehicle_color in ordered_vehicle_colors:
                    amount = ordered_vehicle_color.amount
                    ordered_vehicle_color.vehicle_color.stock_count += amount
                    ordered_vehicle_color.vehicle_color.sale_count -= amount

                    if ordered_vehicle_color.vehicle_color.sale_count < 0:
                        ordered_vehicle_color.vehicle_color.sale_count = 0
                    ordered_vehicle_color.vehicle_color.save(update_fields=['stock_count', 'sale_count'])

    except Exception as e:
        raise e


@router.delete('/', description="주문 삭제")
def delete_order_list_by_id(request, id: int):
    target = get_object_or_404(Order, id=id)
    queryset = target.soft_delete()


@subside_router.get('/', response=List[SubsideListSchema], description="보조금 목록")
def get_list_subside(request):
    queryset = Subside.objects.get_queryset().prefetch_related(
        Prefetch('extrasubside_set', to_attr="extra")
    )
    return queryset


@transaction.atomic(using='default')
@subside_router.post('/')
def create_subside(request, payload: SubsideInsertSchema):
    """
    보조금 생성
    기본 보조금(Subside)는 한 개만 생성 할 수 있고, put method 를 사용 하여 보조금의 양을 수정 할 수 있다.
    추가 보조금(ExtraSubside)는 Subside를 forienkey 로 갖고 있으며, 마찬가지로 put method로 수정 할 수 있다.
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    subside_amount = len(Subside.objects.all())
    try:
        with transaction.atomic():
            if subside_amount == 0:
                subside = Subside.objects.create(amount=payload.dict().get('amount'))
            else:
                raise AlreadyExistsException
            extra_list = [ExtraSubside(**item, subside=subside) for item in payload.dict().get('extra')]
            ExtraSubside.objects.bulk_create(objs=extra_list)

    except Exception as e:
        raise e

    return True


@subside_router.put('/', description="보조금 수정")
def modify_subside(request, payload: SubsideInsertSchema = None):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    for extra_subside in ExtraSubside.objects.get_queryset():
        extra_subside.soft_delete()
    if payload:
        subside = Subside.objects.all().first()
        subside.amount = payload.amount
        subside.save(update_fields=['amount'])
        extra_list = [ExtraSubside(**item, subside=subside) for item in payload.dict().get('extra')]
        queryset = ExtraSubside.objects.bulk_create(objs=extra_list)
    return True


@file_router.post('/')
def upload_files(request, order_id: int, files: List[UploadedFile]):
    """
    계획서 및 보조금 신청서 업로드, 주문에 서류가 필요한 경우 파일을 업로드 해주기 위한 API
    - :param order_id: 주문 아이디
    - :param files:  계획서 및 보조금 신청서 파일
    - :return:
    """
    order = get_object_or_404(Order, id=order_id)
    if order.state == OrderState.REVIEW_DOCS and order.is_request_submit:
        order.is_request_submit = False
        order.save(update_fields=['is_request_submit'])

    queryset = DocumentFile.objects.bulk_create(
        objs=[DocumentFile(order=order, file=file) for file in files], batch_size=upload_exceed_count)


@file_router.delete('/', description="계획서 및 보조금 신청서 삭제")
def delete_files(request, id: int):
    queryset = get_object_or_404(DocumentFile, id=id).delete()


@file_router.get('/format', response=List[DocumentFormatListSchema])
def get_format_list(request):
    """
    보조금 신청서 에 관한 양식의 리스트를 갖고 오는 API
    """
    queryset = DocumentFormat.objects.get_queryset()
    return queryset


@file_router.post('/format')
def upload_format_files(request, file: UploadedFile):
    """
    보조금 신청서 에 관한 양식을 업로드, 어드민만 접근 가능하다.
    - :param file: 보조금 신청서 파일
    - :return:
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    queryset = DocumentFormat.objects.create(file=file)


@file_router.delete('/format', description="보조금 신청서 포맷 삭제")
def delete_format_files(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    target = get_object_or_404(DocumentFormat, id=id)
    queryset = target.soft_delete()


@router.post('/product_delivery_info')
def update_or_create_product_delivery_info(request, payload: ProductDeliveryInfoCreateSchema, order_id: int):
    '''
    주문한 물건이 상품이고 택배사 이름 및 운송장 번호를 입력할 때 사용하는 api
    - :param payload: ProductDeliveryInfoCreateSchema
    - :param order_id: 주문 아이디
    :return:
    '''
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    try:
        target = get_object_or_404(Order, id=order_id)
        if target.orderedproductoptions_set:    # 주문한 물건이 상품일 경우 에만
            if target.product_delivery_info:    # 수정
                target.product_delivery_info.delete()

            delivery_info = ProductDeliveryInfo.objects.create(**payload.dict())
            target.product_delivery_info = delivery_info
            target.save(update_fields=['product_delivery_info'])

    except Exception as e:
        raise e