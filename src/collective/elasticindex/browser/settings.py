
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18nmessageid import MessageFactory
from z3c.form import form, field, button
from plone.autoform.form import AutoExtensibleForm

from collective.elasticindex.interfaces import IElasticSettings
from collective.elasticindex.changes import changes
from collective.elasticindex.utils import create_index, delete_index


_ = MessageFactory('collective.elasticindex')
_plone = MessageFactory('plone')


class ElasticIndexSettings(AutoExtensibleForm, form.EditForm):
    label = _("Elasticsearch configuration")
    description = _("Configure elasticsearch index.")
    form_name = _("Elasticsearch configuration")
    control_panel_view = "plone_control_panel"
    schema = IElasticSettings

    @button.buttonAndHandler(u'Create index', name='create_index')
    def create_index(self, action):
        send = IStatusMessage(self.request).add
        try:
            create_index(IElasticSettings(self.context))
        except:
            send("Error while creating the index.", type='error')
        else:
            send("Index created.")

    @button.buttonAndHandler(u'Delete index', name='delete_index')
    def delete_index(self, action):
        send = IStatusMessage(self.request).add
        try:
            delete_index(IElasticSettings(self.context))
        except:
            send("Error while deleting the index.", type='error')
        else:
            send("Index deleted.")

    @button.buttonAndHandler(u'Import site content', name='import_content')
    def import_site_content(self, action):
        send = IStatusMessage(self.request).add
        try:
            changes.verify_and_index_container(self.context)
        except:
            send("Error while indexing the index.", type='error')
        else:
            send("Index refreshed.")

    @button.buttonAndHandler(_plone(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_plone(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(),
            self.control_panel_view))

