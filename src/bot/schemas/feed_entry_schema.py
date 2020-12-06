from marshmallow import Schema, fields


class FeedEntrySchema(Schema):
    published = fields.Str(required=True, allow_none=True)
    title = fields.Str(required=True, allow_none=True)
    url = fields.Str(required=True, allow_none=True)
    author = fields.Str(required=True, allow_none=True)
