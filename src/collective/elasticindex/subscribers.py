
from collective.elasticindex.changes import changes
from Products.CMFCore.utils import getToolByName


def content_added(content, event):
    factorytool = getToolByName(content, 'portal_factory', None)
    if factorytool in content.aq_chain:
        return
    changes.index_content(content)


def content_modified(content, event):
    factorytool = getToolByName(content, 'portal_factory', None)
    if factorytool in content.aq_chain:
        return
    changes.index_content(content)


def content_deleted(content, event):
    if event.newParent is None:
        changes.unindex_content(content)


