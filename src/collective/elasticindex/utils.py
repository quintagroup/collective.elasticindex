
import pyes
import urlparse

from collective.elasticindex.interfaces import IElasticSettings


MAPPINGS = {
    'title': {'type': 'string', 'store': 'yes', 'index': 'analyzed'},
    'url': {'type': 'string', 'store': 'yes', 'index': 'analyzed'},
    'content': {'type': 'string',  'store': 'yes', 'index': 'analyzed'}}


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
    connection.indices.put_mapping(
        'document', {'properties':MAPPINGS}, [settings.index_name])

