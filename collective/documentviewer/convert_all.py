from collective.documentviewer.async import queueJob
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.settings import Settings
from collective.documentviewer.utils import allowedDocumentType
from logging import getLogger
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

logger = getLogger('collective.documentviewer')


def convert_all(only_unconverted=True):
    """Convert all files.
    Defaults to convert only files, which hasn't been converted yet.
    """
    site = getSite()

    qi = getToolByName(site, 'portal_quickinstaller', None)
    if not qi:
        return
    if not qi.isProductInstalled('collective.documentviewer'):
        return
    if getRequest().get('plone.app.contenttypes_migration_running', False):
        """Don't migrate while running a plone.app.contenttypes migration.
        """
        return

    cat = getToolByName(site, 'portal_catalog')
    res = cat(portal_type='File')
    length = len(res)

    for cnt, item in enumerate(res, 1):

        logger.info('processing %s/%s', cnt, length)

        obj = item.getObject()

        settings = Settings(obj)
        if not only_unconverted and settings.successfully_converted:
            return

        gsettings = GlobalSettings(site)

        if not allowedDocumentType(obj, gsettings.auto_layout_file_types):
            return

        auto_layout = gsettings.auto_select_layout
        if auto_layout and obj.getLayout() != 'documentviewer':
            obj.setLayout('documentviewer')

        if obj.getLayout() == 'documentviewer' and gsettings.auto_convert:
            queueJob(obj)