
from collective.elasticindex.changes import changes
from Products.CMFCore.utils import getToolByName


def content_added(content, event):
    factorytool = getToolByName(content, 'portal_factory')
    if factorytool in content.aq_chain:
        return
    if changes.should_index_content(content):
        changes.index_content(content)


def content_modified(content, event):
    factorytool = getToolByName(content, 'portal_factory')
    if factorytool in content.aq_chain:
        return
    if changes.should_index_content(content):
        changes.index_content(content)


def content_deleted(content, event):
    if event.newParent is None:
        if changes.should_index_content(content):
            changes.unindex_content(content)


def content_published(content, event):
    if not changes.only_published:
        return
    if (event.old_state.getId() == 'published' and
        event.new_state.getId() != 'published'):
        changes.unindex_content(content)
    elif (event.new_state.getId() == 'published' and
          event.old_state.getId() != 'published'):
        changes.index_content(content)

