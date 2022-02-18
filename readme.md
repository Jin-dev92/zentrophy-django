#zentrophy-django

* url
  * /v1/docs -API List Swagger
  * /admin - django admin page
  * /accounts/login/ -  # 로그인 기본값, user_name이 아이디
  * /accounts/logout/ -  # 로그아웃 기본값
  * LOGIN_REDIRECT_URL = '/'  # 반드시 정의할 것!


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

