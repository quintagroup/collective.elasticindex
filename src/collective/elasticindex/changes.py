
from Products.CMFCore.interfaces import IFolderish, IContentish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint
from zope.component import queryUtility
from zope.interface import implements
import threading
import transaction
import logging

from collective.elasticindex.interfaces import IElasticSettings
from collective.elasticindex.utils import connect

logger = logging.getLogger('collective.elasticindex')


def get_uid(content):
    """Return content identifier to use in ES.
    """
    if IPloneSiteRoot.providedBy(content):
        uid = 'root'
    else:
        uid = content.UID()
    return uid or None

def get_data(content):
    """Return data to index in ES.
    """
    uid = get_uid(content)
    if not uid:
        return None, None
    title = content.Title()
    try:
        text = content.SearchableText()
    except:
        text = title
    data = {'title': title,
            'description': content.Description(),
            'subject': ' '.join(content.Subject()),
            'url': content.absolute_url(),
            'author': ' '.join(content.listCreators()),
            'content': text}
    created = content.created()
    if created is not (None, 'None'):
        data['created'] = created.strftime('%Y-%m-%dT%H:%M:%S')
    modified = content.modified()
    if modified is not (None, 'None'):
        data['modified'] = modified.strftime('%Y-%m-%dT%H:%M:%S')
    return uid, data

def list_content(content):
    """Recursively list CMF content out of the given one.
    """

    def recurse(content):
        for child in content.contentValues():
            if IFolderish.providedBy(child):
                for grandchild in recurse(child):
                    yield grandchild
            yield child

    if IFolderish.providedBy(content):
        for child in recurse(content):
            yield child
        yield content
    elif IContentish.providedBy(content):
        yield content


class ElasticSavepoint(object):
    implements(ISavepointDataManager)

    def __init__(self, manager, index, unindex):
        self._index = index.copy()
        self._unindex = set(unindex)

    def restore(self):
        self.manager._index = self._index
        self.manager._unindex = self._unindex


class ElasticChanges(threading.local):
    implements(IDataManagerSavepoint)

    def __init__(self, manager):
        self.manager = manager
        self._clear()

    def _clear(self):
        self._index = dict()
        self._unindex = set()
        self._settings = None
        self._connection = None
        self._activated = False

    def _follow(self):
        if self._settings is None:
            portal = queryUtility(IPloneSiteRoot)
            if portal is None:
                return False
            self._settings = IElasticSettings(portal)
            self._activated = self._settings.activated
            if self._activated:
                transaction = self.manager.get()
                transaction.join(self)
        return self._activated

    def index_content(self, content, recursive=False):
        if not self._follow():
            return
        if recursive:
            items = list_content(content)
        else:
            items = [content]
        for item in items:
            uid, data = get_data(item)
            if data:
                if uid in self._unindex:
                    del self._unindex[uid]
                self._index[uid] = data

    def unindex_content(self, content):
        if not self._follow():
            return
        uid = get_uid(content)
        if uid in self._index:
            del self._index[uid]
        self._unindex.add(uid)

    def savepoint(self):
        return ElasticSavepoint(self, self._index, self._unindex)

    def commit(self, transaction):
        pass

    def sortKey(self):
        return 'Z' * 100

    def abort(self, transaction):
        self._clear()

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        if self._index or self._unindex and self._settings.server_urls:
            self._connection = connect(self._settings.server_urls)

    def tpc_finish(self, transaction):
        if self._connection is not None:
            for uid, data in self._index.iteritems():
                try:
                    self._connection.index(
                        data,
                        self._settings.index_name,
                        'document',
                        id=uid,
                        bulk=True)
                except:
                    logger.exception(
                        'Error while indexing document in Elasticsearch')
            for uid in self._unindex:
                try:
                    self._connection.delete(
                        self._settings.index_name,
                        'document',
                        uid,
                        bulk=True)
                except:
                    logger.exception(
                        'Error while indexing document in Elasticsearch')
            if self._index or self._unindex:
                try:
                    self._connection.flush_bulk(True)
                except:
                    logger.exception(
                        'Error while flushing changes to Elasticsearch')
        self._clear()

    def tpc_abort(self, transaction):
        self._clear()


changes = ElasticChanges(transaction.manager)
