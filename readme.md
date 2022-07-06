#zentrophy-django

#  URL 상세
```
* [API Swagger] {root_url}/v1/docs
* [django admin] {root_url}/admin
* [이미지 파일 경로] {root_url}/media/{파일 경로}
```
---
# 슈퍼 유저(어드민) 계정 생성 방법 
  터미널 루트 폴더 내에서 가상 환경 실행 후 `python3 manage.py createsuperuser` 실행

---
# Used package
    * Python 3.10.1
    * pip	22.0.3
    * Django	4.0.2
      * django-rest-swagger	2.2.0
      * django-phonenumber-field	6.0.0
      * django-ninja	v0.16.1
    * sorl-thumbnail	v12.7.0
    * Pillow	9.0.0
    * pydantic	1.8.2
    * orjson	3.6.5
    * numpy	1.22.1
---
# Project Structure
해당 프로젝트의 내에 존재 하는 모든 앱들은 파일 구조가 같으므로 대표 적으로 external 앱 하나만 설명 한다.
  * `conf`
    * `api` - 모든 API 에 대한 명세가 정의 되어 있는 파일
    * `constant` - conf 내에서 사용 되는 상수를 모아둔 파일
    * `custom_exception` - 기획에 따라 에러를 부여 해야 하는 곳에 사용 되는 exception 을 모아둔 파일
    * `settings` - 장고에 대한 설정 값이나 전역 상수를 모아둔 파일
---
  * `external` - 외부 api 를 사용 하는 앱
    * `admin` - 어드민 페이지 에 관련된 내용을 모아둔 파일
    * `constant` - 해당 앱에서 사용 되는 상수를 모아둔 파일
    * `models` - 모델
    * `schema` - API 나 모델에서 사용하는 스키마를 모아둔 파일
---
  * `history` - 환불 내역, A/S 내역, 보증 관련, 장바구니, 가견적 관련 내용을 갖고 있는 앱
  * `member` - 유저, 유저가 갖는 결제 수단 관련 내용을 갖고 있는 앱
  * `order` - 주문 관련 내용을 갖고 있는 앱
  * `placement` - 플레이스 관련 내용을 갖고 있는 앱
  * `post` - FAQ, 공지 사항에 관련 된 내용을 갖고 있는 앱
  * `product` - 모터사이클, 상품 관련 내용을 갖고 있는 앱
---
  * `util`
    * `exception`
      * `constant` - exception 에 사용 되는 상수를 모아둔 파일
    * `file` - 파일 관련 함수를 모아 둔 파일
    * `models` - 다른 앱에서 공통 으로 사용 되는 모델을 모아 둔 파일
    * `number` - 숫자 관련된 함수를 모아둔 파일
    * `params` - api request 를 받았 거나 요청을 할 경우 파라미터 변조 혹은 가공에 관련된 함수 들을 모아둔 파일 
    * `permission` - 어드민 권한 관련 함수를 모아둔 파일
    * `util` - 분류 하기 힘들 거나 애매한 함수를 모아둔 파일
---
# Exception response 코드에 관한 내용
  * 모든 exception 에는 `code` 와 `desc` 값을 가진다.
  * `code` 는 상태 코드 (3자리) + 에러 종류 코드 (4자리)로 구분 된다.
  * `desc` 에는 에러에 관한 내용이 적혀 있다.
  * 자세한 내용은 `util/exception/constant.py` 파일에 명시 되어 있음.

