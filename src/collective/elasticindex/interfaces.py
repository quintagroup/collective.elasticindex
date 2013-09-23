
from zope import schema
from zope.interface import Interface


class IElasticSettings(Interface):
    only_published = schema.Bool(
        title=u'Index only published content?',
        default=True)
    index_security = schema.Bool(
        title=u'Index security?',
        default=False)
    index_name = schema.TextLine(
        title=u"Index name",
        required=True)
    server_urls = schema.List(
        title=u"Server URLs",
        value_type=schema.URI(),
        required=True)
    public_server_urls = schema.List(
        title=u"Server URLs to use for the public search",
        description=u"If not specified regular server URLs will be used",
        value_type=schema.URI(),
        required=True)
    public_through_plone = schema.Bool(
        title=u"Proxy search requests through Plone and apply security filter?",
        description=u"Check this and index security if you want to have a private search",
        default=False)

    def get_search_urls():
        pass
