
from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility


class SettingsAdapter(object):

    def __init__(self, context):
        self._id = context.getId()
        self._properties = getUtility(IPropertiesTool).elasticindex_properties

    @apply
    def index_name():

        def getter(self):
            if self._properties.index_name:
                return self._properties.index_name
            return self._id

        def setter(self, value):
            self._properties.index_name = value
            return value

        return property(getter, setter)

    @apply
    def server_urls():

        def getter(self):
            return self._properties.server_urls

        def setter(self, value):
            self._properties.server_urls = tuple(value)
            return self._properties.server_urls

        return property(getter, setter)
