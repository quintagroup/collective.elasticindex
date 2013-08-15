
from plone.app.controlpanel.form import ControlPanelForm
from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from collective.elasticindex.interfaces import IElasticSettings
from collective.elasticindex.changes import changes
from collective.elasticindex.utils import create_index


_ = MessageFactory('collective.elasticindex')


class ElasticIndexSettings(ControlPanelForm):
    label = _("Elasticsearch configuration")
    description = _("Configure elasticsearch index.")
    form_name = _("Elasticsearch configuration")
    form_fields = form.Fields(IElasticSettings)

    @form.action('Create index', name='create_index')
    def create_index(self, action, data):
        create_index(IElasticSettings(self.context))


    @form.action('Import site content', name='import_content')
    def import_site_content(self, action, data):
        changes.verify_and_index_container(self.context)

    actions += form.Actions(*list(ControlPanelForm.actions))

