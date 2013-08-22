
from zope.formlib import form
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ISearchPortlet(IPortletDataProvider):
    """Search portlet.
    """


class SearchPortlet(base.Assignment):
    implements(ISearchPortlet)


class SearchPortletRenderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')


class SearchPortletAddForm(base.AddForm):
    """Creation form for search portlet.
    """
    form_fields = form.Fields()

    def create(self, data):
        return SearchPortlet()


class SearchPortletEditForm(base.EditForm):
    """Edit form for search portlet.
    """
    form_fields = form.Fields()
