from collections import namedtuple

from castle.cms.package import CASTLE_VERSION  # noqa:F401
from castle.cms.package import CASTLE_VERSION_STRING  # noqa:F401

SHIELD = namedtuple('SHIELD', 'NONE BACKEND ALL')('', 'backend', 'all')
MAX_PASTE_ITEMS = 40
ALL_SUBSCRIBERS = '--SUBSCRIBERS--'
ALL_USERS = '--USERS--'
DEFAULT_SITE_LAYOUT_REGISTRY_KEY = 'castle.cms.mosaic.default_site_layout'
CRAWLED_SITE_ES_DOC_TYPE = 'website'
CRAWLED_DATA_KEY = 'castle.cms.crawldata'
TRASH_LOG_KEY = 'castle.cms.empty-trash-log'
ANONYMOUS_USER = "Anonymous User"
