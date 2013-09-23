
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.form import ControlPanelForm
from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from collective.elasticindex.interfaces import IElasticSettings
from collective.elasticindex.changes import changes
from collective.elasticindex.utils import create_index, delete_index


_ = MessageFactory('collective.elasticindex')


class ElasticIndexSettings(ControlPanelForm):
    label = _("Elasticsearch configuration")
    description = _("Configure elasticsearch index.")
    form_name = _("Elasticsearch configuration")
    form_fields = form.Fields(IElasticSettings)

    @form.action('Create index', name='create_index')
    def create_index(self, action, data):
        send = IStatusMessage(self.request).add
        try:
            create_index(IElasticSettings(self.context))
        except:
            send("Error while creating the index.", type='error')
        else:
            send("Index created.")

    @form.action('Delete index', name='delete_index')
    def delete_index(self, action, data):
        send = IStatusMessage(self.request).add
        try:
            delete_index(IElasticSettings(self.context))
        except:
            send("Error while deleting the index.", type='error')
        else:
            send("Index deleted.")

    @form.action('Import site content', name='import_content')
    def import_site_content(self, action, data):
        send = IStatusMessage(self.request).add
        try:
            changes.verify_and_index_container(self.context)
        except:
            send("Error while indexing the index.", type='error')
        else:
            send("Index refreshed.")

    actions += form.Actions(*list(ControlPanelForm.actions))
