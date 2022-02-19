from ninja.schema import Schema


class PostInsertSchema(Schema):
    title: str
    content: str


class FAQCategorySchema(Schema):
    id: int
    category_name: str


class FAQInsertSchema(PostInsertSchema):
    # title: str
    # content: str
    category: int


class FAQListSchema(Schema):
    id: int
    title: str
    content: str
    category: FAQCategorySchema = None


class NoticeListSchema(Schema):
    id: int
    title: str
    content: str


class NoticeInsertSchema(PostInsertSchema):
    pass


class FAQCategoryInsertSchema(Schema):
    category_name: str
