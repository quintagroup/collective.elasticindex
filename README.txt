=======================
collective.elasticindex
=======================

This extension index `Plone`_ content into `ElasticSearch`_. This doesn't
replace the Plone catalog with ElasticSearch, nor interact with the
Plone catalog at all, it merely index content inside ElasticSearch when
it is modified or published.

In addition to this, it provides a simple search page called
``search.html`` that queries ElasticSearch using Javascript (so Plone
is not involved in searching) and propose the same features than the
default Plone search page. A search portlet let you redirect people to
this new search page as well.

This extension have been built for Plone 4, but might work with Plone
3.

Usage
-----

After adding this extension to your buildout (including the zcml), you
can install the extension in Plone. A configuration screen is
available inside site setup. It will let you configure the URLs of the
ElasticSearch servers to use in order to index, and search. To proceed:

- Fill in the ElasticSearch settings,

- Click on *Save*,

- Click on *Create Index* in order to create the ElasticSearch index,

- Click on *Import site content* in order to index already existing
  content in ElasticSearch.

You can use the same ElasticSearch server (and probably index) for
multiple Plone sites, creating a federated search that way.

Security disclaimer
-------------------

By default is no authentication or access validation while searching
or indexing content. The original purpose of this search is to be
public.

If you have private content that you don't want to be searchable or
viewable by unauthorized people, please be sure to check the checkbox
*index only published content* in the configuration screen.

In addition to this ElasticSearch is not secured by default, meaning
there is no authentication to provide in order to index or look-up
content. Be sure to hide it behind a firewall and use a proxy or
Apache in order to restrict the requests made to it: you only need to
allow access via POST to the sub-URL ``_search`` after the index name
configured in the configuration screen. For instance, if the index
name is ``plone``, you shall allow only requests to
``http://your-public-es-url/plone/_search``. After you configured your
proxy, be sure to configure its public URL, like
``http://your-public-es-url`` in the configuration screen so the
search page knows how to contact it.

However if you want to allow users to search though restricted and not
yet published content, you can check *index security* and uncheck
*index only published content* in the configuration screen. After
reindexing your content, if you check *proxy search requests though
Plone and apply security filter*, search will work on restricted and
not yet published content, but will be slower as the queries will be
proxied though Plone.

.. _Plone: http://plone.org/
.. _ElasticSearch: http://www.elasticsearch.org/
