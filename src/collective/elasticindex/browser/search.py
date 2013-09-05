
from Products.Five.browser import BrowserView
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from collective.elasticindex.interfaces import IElasticSettings
from zope.component import getUtility
import json


class SearchPage(BrowserView):

    def update(self):
        settings = IElasticSettings(getUtility(IPloneSiteRoot))
        self.server_urls = json.dumps(list(
                settings.public_server_urls or settings.server_urls))
        self.index_name = settings.index_name
        self.expanded = ''
        if 'advanced' in self.request.form:
            self.expanded = 'expanded'
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)

    def __call__(self):
        self.update()
        return super(SearchPage, self).__call__()
