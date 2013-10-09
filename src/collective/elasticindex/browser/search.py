
from Acquisition import aq_base
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from collective.elasticindex.interfaces import IElasticSettings
from plone.memoize import ram
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
import json
import random
import urllib2
import time


class SearchPage(BrowserView):

    def update(self):
        settings = IElasticSettings(getUtility(IPloneSiteRoot))
        if settings.public_through_plone:
            urls = [absoluteURL(self.context, self.request) + '/search.json']
        else:
            urls = settings.get_search_urls()
        self.server_urls = json.dumps(urls)
        self.expanded = ''
        if 'advanced' in self.request.form:
            self.expanded = 'expanded'
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)

    def __call__(self):
        self.update()
        return super(SearchPage, self).__call__()


def cache_user(method):

    def get_cache_key(method, self, user):
        return '#'.join((user.getId() or '', str(time.time() // (5 * 60 * 60))))

    return ram.cache(get_cache_key)(method)


class SearchQuery(BrowserView):

    @cache_user
    def _listAllowedRolesAndUsers(self, user):
        """Makes sure the list includes the user's groups.
        """
        result = user.getRoles()
        if 'Anonymous' in result:
            # The anonymous user has no further roles
            return ['Anonymous']
        result = list(result)
        if hasattr(aq_base(user), 'getGroups'):
            groups = ['user:%s' % x for x in user.getGroups()]
            if groups:
                result = result + groups
        result.append('Anonymous')
        result.append('user:%s' % user.getId())
        return result

    def __call__(self):
        if self.request.method != 'POST':
            self.request.response.setStatus(405)
            return ''
        self.request.stdin.seek(0, 0)
        payload = json.load(self.request.stdin)
        if not isinstance(payload, dict):
            self.request.response.setStatus(400)
            return ''
        if 'fields' in payload:
            if (not isinstance(payload['fields'], list) or
                'contents' in payload['fields']):
                # Prevent people to retrieve the fulltext.
                self.request.response.setStatus(400)
                return ''
        authorizedFilter = {
            'terms': {
                'authorizedUsers': self._listAllowedRolesAndUsers(
                    _getAuthenticatedUser(self.context)),
                'execution': 'or'}}
        if 'query' in payload:
            if 'filtered' in payload['query']:
                filtered = payload['query']['filtered']
                if ('filter' not in filtered or
                    not isinstance(filtered['filter'], dict)):
                    self.request.response.setStatus(400)
                    return ''
                if 'and' not in filtered['filter']:
                    filters = [filtered.pop('filter')]
                    filtered['filter'] = {'and': filters}
                else:
                    filters = filtered['filter']['and']
                    if not isinstance(filters, list):
                        self.request.response.setStatus(400)
                        return ''
                filters.append(authorizedFilter)
            else:
                query = payload.pop('query')
                payload['query'] = {
                    'filtered': {
                        'query': query,
                        'filter': authorizedFilter}}
        else:
            payload['query'] = {
                'filtered': {'filter': authorizedFilter}}

        settings = IElasticSettings(getUtility(IPloneSiteRoot))
        try:
            response = urllib2.urlopen(
                random.choice(settings.get_search_urls()),
                json.dumps(payload))
        except:
            self.request.response.setStatus(500)
            return ''

        self.request.response.setHeader(
            'Content-Type',
            'application/json;charset=UTF-8')
        return response.read()
