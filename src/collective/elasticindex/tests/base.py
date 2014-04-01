
try:
    from Zope2.App.zcml import load_config
except ImportError:
    from Products.Five.zcml import load_config
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.elasticindex
    load_config('configure.zcml', collective.elasticindex)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.elasticindex')


setup_product()
ptc.setupPloneSite(products=['collective.elasticindex'])


class ElasticIndexTestCase(ptc.PloneTestCase):
    pass
