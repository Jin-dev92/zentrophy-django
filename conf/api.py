from typing import List
from ninja import NinjaAPI

from member.models import Member
from member.schema import MemberListSchema, MemberInsertScheme

api = NinjaAPI()


@api.get("/member", response=List[MemberListSchema], description="DB 내의 모든 멤버 list")
def getMemberList(request):
    queryset = Member.objects.all()
    return queryset


@api.get("/member/{member_id}", response=MemberListSchema, description="id로 해당 멤버 검색")
def getMemberbyId(request, member_id: int):
    queryset = Member.objects.get(id=member_id)
    return queryset


@api.post("/member", description="멤버 생성")
def createMember(request, payload: MemberInsertScheme):
    member = Member.objects.create(**payload.dict())
    return {"id": member.id}


@api.put("/member/{member_id}", description="멤버 수정")
def modifyMember(request, member_id: int, payload: MemberInsertScheme):
    qs = Member.objects.get(id=member_id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()
    return qs


@api.delete("/member/{member_id}", description="멤버 삭제")
def deleteMemberById(request, member_id: int):
    queryset = Member.objects.get(id=member_id).delete()
    return queryset
