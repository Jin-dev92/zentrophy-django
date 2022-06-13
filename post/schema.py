from ninja.schema import Schema


class PostInsertSchema(Schema):
    title: str
    content: str


class FAQCategorySchema(Schema):
    id: int
    category_name: str


class FAQInsertSchema(PostInsertSchema):
    category_id: int = None


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
