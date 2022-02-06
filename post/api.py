from typing import List
from ninja import Router
from django.shortcuts import get_list_or_404, get_object_or_404

# from conf.api import api
from post.models import Post
from post.schema import PostListSchema, PostInsertSchema, PostModifySchema

router = Router()


@router.get("/{post_type}", response={200: List[PostListSchema]},
            description="타입으로 글 관련 데이터를 obj로 가져옴. FAQ = 0, 공지사항 = 1",
            tags=["post"]
            )
def get_post_list_by_type(request, post_type: int):
    return get_list_or_404(Post, post_type=post_type)


@router.get("/{id}", response={200: PostListSchema},
            description="pk로 글 관련 데이터를 obj로 가져옴.",
            tags=["post"]
            )
def get_post_list_by_id(request, id: int):
    qs = get_object_or_404(Post, id=id)
    return qs


@router.post("",
             description="글 관련 데이터 삽입",
             tags=["post"]
             )
def create_post(request, payload: PostInsertSchema):
    Post.objects.create(**payload.dict())


@router.put("/{id}", description="글 수정", tags=["post"])
def update_post_list_by_id(request, payload: PostModifySchema, id: int):
    qs = get_object_or_404(Post, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@router.delete("/{id}", description="글 삭제", tags=["post"])
def delete_post_by_id(request, id: int):
    get_object_or_404(Post, id=id).delete()
