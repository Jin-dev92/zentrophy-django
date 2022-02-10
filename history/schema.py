from ninja import Schema


class HistoryListSchema(Schema):
    id: int = None


class AfterServiceInsertSchema(Schema):
    place_id: int
