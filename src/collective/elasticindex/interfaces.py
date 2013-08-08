
from zope import schema
from zope.interface import Interface


class IElasticSettings(Interface):
    index_name = schema.TextLine(
        title=u"Index name",
        required=True)
    server_urls = schema.List(
        title=u"Server URLs",
        value_type=schema.URI(),
        required=True)


