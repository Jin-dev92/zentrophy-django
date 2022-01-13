from typing import List

from ninja import NinjaAPI

from member.models import Member
from member.schema import MemberOut, MemberIn

api = NinjaAPI()


@api.get("/member", response=List[MemberOut])
def getMemberList(request):
    queryset = Member.objects.all()
    print(queryset)
    return queryset


@api.post("/member")
def createMember(request, payload: MemberIn):
    member = Member.objects.create(**payload.dict())
    return {"id": member.id}
