
import pyes
import urlparse
from zope.interface import Interface
from zope.component import getAdapters
from collective.elasticindex.interfaces import IElasticMapping
from copy import deepcopy

ANALYZED_STRING_MAPPING = {
    'index': 'analyzed',
    'type': 'string',
    'store': 'yes'
}

STORED_STRING_MAPPING = {
    'index': 'not_analyzed',
    'type': 'string',
    'store': 'yes',
}

STRING_MAPPING = {
    'index': 'not_analyzed',
    'type': 'string',
    'store': 'no',
}

DATE_MAPPING = {
    'index': 'not_analyzed',
    'type': 'date',
    'store': 'no'
}

INT_MAPPING = {
    'index': 'not_analyzed',
    'type': 'integer',
    'store': 'no'
}

DOCUMENT_MAPPING = {
    '_index': {
        'enabled': True
    },
    # Stored
    'title': ANALYZED_STRING_MAPPING,
    'subject': ANALYZED_STRING_MAPPING,
    'description': ANALYZED_STRING_MAPPING,
    'content': ANALYZED_STRING_MAPPING,
    'author': ANALYZED_STRING_MAPPING,
    'contributors': ANALYZED_STRING_MAPPING,

    # Not analyzed
    '_id' : STORED_STRING_MAPPING,
    'url': STORED_STRING_MAPPING,
    'metaType': STORED_STRING_MAPPING,

    # Not stored
    'created': DATE_MAPPING,
    'modified': DATE_MAPPING,
    'publishedYear': INT_MAPPING,
    'sortableTitle': STRING_MAPPING,
    'authorizedUsers': STRING_MAPPING,
}

def parse_url(url):
    info = urlparse.urlparse(url)
    if ':' in info.netloc:
        url, port = info.netloc.split(':', 1)
    else:
        port = 80
        if info.scheme == 'https':
            port = 443
        url = info.netloc
    return 'http', url, int(port)


def connect(urls):
    try:
        return pyes.ES(map(parse_url, urls))
    except:
        raise ValueError('Cannot connect to servers')


def create_index(settings):
    connection = connect(settings.server_urls)
    connection.indices.create_index_if_missing(settings.index_name)
    document_mapping = deepcopy(DOCUMENT_MAPPING)

    for name, adapter in getAdapters((Interface,), IElasticMapping):
        document_mapping[name] = adapter
        
    connection.indices.put_mapping(
        'document', {'properties' : document_mapping}, [settings.index_name])


def delete_index(settings):
    connection = connect(settings.server_urls)
    connection.indices.delete_index_if_exists(settings.index_name)
