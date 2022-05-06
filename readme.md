#zentrophy-django

* url
  * /v1/docs -API List Swagger
  * /admin - django admin page

* 슈퍼 유저 계정 (말하면 만들어 드릶)
* /media 이미지 파일 생성 경로
* config/setting 파일들 참조.

* used package
  * Python 3.10.1
  * pip	22.0.3
  * Django	4.0.2
    * django-rest-swagger	2.2.0
    * django-phonenumber-field	6.0.0
    * django-ninja	v0.16.1 (core)
  * sorl-thumbnail	v12.7.0
  * Pillow	9.0.0
  * pydantic	1.8.2
  * orjson	3.6.5
  * numpy	1.22.1
  * 추후 배포할 때 라이브러리 버전 업데이트에 대한 문서 최신화 예정. 

# error response 코드에 관한 내용
  * 모든 에러에는 code 와 desc 값을 가진다.
  * code는 상태코드 (3자리) + 에러 종류 코드 (4자리)로 구분 된다.
  * desc 에는 에러에 관한 내용이 적혀 있다.