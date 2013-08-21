
(function($) {
    // Hang on in there. We have jQuery, 1.4.
    var BATCH_SIZE = 10;

    var ElasticSearch = function($form) {
        var search_urls = $form.data('server-urls'),
            index_name = $form.data('index-name');
        var empty_results = [],
            results = [];
        var previous_query = null,
            start_from = 0;

        var get_url = function() {
            var index = Math.floor(Math.random() * search_urls.length);
            return [search_urls[index], '/', index_name, '/_search'].join('');
        };

        var build_query = function(original) {
            var queries = [{
                    query_string : {
                        query: original.term,
                        default_operator: "AND",
                        fields: [
                            "author^2",
                            "title^3",
                            "subject^2",
                            "description",
                            "content"
                        ]
                    }
                }],
                query,
                sort = {};
            // Sorting options.
            if (original.sort == 'created' || original.sort == 'modified') {
                sort[original.sort] = 'desc';
            } else if (original.sort == 'title') {
                sort = "sortableTitle";
            } else {
                sort = "_score";
            };
            // Other criterias
            if (original.contributors) {
                queries.push({match: {contributors: original.contributors}});
            };
            if (original.created) {
                queries.push({range: {created: {from: original.created}}});
            };
            if (queries.length > 1) {
                query = {bool: {must: queries}};
            } else {
                query = queries[0];
            };
            return {
                size: BATCH_SIZE,
                sort: [sort],
                query: query,
                highlight: {
                        fields: {
                            title: {number_of_fragments: 0},
                            description: {fragment_size: 150, number_of_fragments: 3}
                        }
                    },
                fields: ['url', 'title', 'description']
            };
        };

        var do_search = function(query, from) {
            // Form up any query here
            query['from'] = from || 0;
            $.ajax({
                url: get_url(),
                type: 'POST',
                crossDomain: true,
                dataType: 'json',
                success: function(data) {
                    var notifies = data.hits.total ? results : empty_results;
                    for (var i=0, len=notifies.length; i < len; i++) {
                        notifies[i](data.hits, from || 0);
                    }
                },
                data: JSON.stringify(query)
            });
            return query;
        };

        return {
            subscribe: function(plugin) {
                if (plugin.onempty !== undefined) {
                    empty_results.push(plugin.onempty);
                };
                if (plugin.onresult !== undefined) {
                    results.push(plugin.onresult);
                };
            },
            scroll: function(index) {
                if (previous_query !== null) {
                    do_search(previous_query, index);
                };
            },
            search: function(term) {
                previous_query = do_search(build_query(term));
            }
        };
    };

    var CountDisplayPlugin = function($count) {
        return {
            onempty: function() {
                $count.text('0');
            },
            onresult: function(data) {
                $count.text(data.total);
            }
        };
    };

    var ResultDisplayPlugin = function($result, $empty) {
        return {
            onempty: function() {
                $result.hide();
                $empty.show();
            },
            onresult: function(data) {
                var entry, i, len;
                var title, description, url;

                $empty.hide();
                $result.empty();
                $result.show();
                for (i=0, len=data.hits.length; i < len; i++) {
                    entry = data.hits[i];
                    title = (entry.highlight && entry.highlight.title) || entry.fields.title;
                    description = (entry.highlight && entry.highlight.description) || entry.fields.description;
                    url = entry.fields.url;
                    $result.append(
                        '<dt class="contenttype-document"><a href="'
                            + url + '">' + title + '</a></dt><dd>' + description + '</dd>'
                    );
                };
            }
        };
    };

    var BatchDisplayPlugin = function($batch, update) {
        var PAGING    = 3,
            NO_LEAP   = 0,
            PRE_LEAP  = 1,
            POST_LEAP = 2,

            $prev = $('span.previous'),
            $next = $('span.next'),

            $prev_a = $('span.previous a'),
            $next_a = $('span.next a'),

            $prev_size = $('span.previous a span span'),
            $next_size = $('span.next a span span'),

            link_to = function (opt) {
                var $item;

                if (opt.current) {
                    $item = $('<span class="esGeneratedBatch current"> ' + opt.page + ' </span>');
                } else {
                    $item = $('<a class="esGeneratedBatch" href=""> ' + opt.page + ' </a>');

                    if (opt.leap) {
                        var $leap = $('<span>&hellip;</span>');
                        if (opt.leap == PRE_LEAP) {
                            $item.prepend($leap);
                        } else {
                            $item.append($leap);
                        }
                    };

                    $item.bind('click', function () {
                        update((opt.page - 1) * BATCH_SIZE);
                        return false;
                    });
                };
                return $item;
            };

        return {
            onempty: function() {
                $batch.hide();
            },
            onresult: function(data, current) {
                $batch.hide();

                if (data.total <= BATCH_SIZE) {
                    return;
                }

                $batch.children('.esGeneratedBatch').remove();

                var page_count = Math.ceil(data.total / BATCH_SIZE);
                var current_page = Math.ceil(current / BATCH_SIZE) + 1;
                var $current = link_to({page : current_page, current: true});

                $current.insertAfter($next);

                for (var i = PAGING; i >= 1; i--) {
                    if (current_page - i <= 1) {
                        continue;
                    }
                    link_to({page : current_page - i}).insertBefore($current);
                };

                for (var i = PAGING; i >= 1; i--) {
                    if (current_page + i >= page_count) {
                        continue;
                    }
                    link_to({page : current_page + i}).insertAfter($current);
                };

                if (current_page > 1) {
                    var first_leap = current_page - PAGING > 2 ? POST_LEAP : NO_LEAP;
                    $prev_size.text(BATCH_SIZE);
                    $prev_a.unbind();
                    $prev_a.bind('click', function () { update(current - BATCH_SIZE); return false });
                    $prev.show();
                    link_to({page: 1, leap: first_leap}).insertAfter($next);
                } else {
                    $prev.hide();
                };

                if (current_page < page_count) {
                    var last_leap = current_page + PAGING < (page_count - 2) ? PRE_LEAP : NO_LEAP;
                    var next_size = Math.min(data.total - (current_page * BATCH_SIZE), BATCH_SIZE);
                    $next_size.text(next_size);
                    $next_a.unbind();
                    $next_a.bind('click', function () { update(current + BATCH_SIZE); return false });
                    $next.show();
                    link_to({page: page_count, leap: last_leap}).appendTo($batch);
                } else {
                    $next.hide();
                };

                $batch.show();
            }
        };
    };

    $(document).ready(function() {
        $('.esSearchForm').each(function() {
            var $form = $(this),
                $options = $form.find('div.esSearchOptions'),
                search = ElasticSearch($form);

            var $query = $form.find('input.searchPage'),
                $author = $form.find('input#Contribs'),
                $subject = $form.find('input#Suject'),
                $since = $form.find('select#created'),
                $button = $form.find('input[type=submit]'),
                $sort = $form.find('select#sort_on'),
                options = false,
                previous = null,
                timeout = null;

            var scroll_search = function(index) {
                if (timeout !== null) {
                    clearTimeout(timeout);
                    timeout = null;
                };
                search.scroll(index);
            };

            var schedule_search = function(force) {
                if (timeout !== null) {
                    clearTimeout(timeout);
                };
                timeout = setTimeout(function () {
                    var query = {term: $query.val()};

                    if (options) {
                        query['contributors'] = $author.val();
                        query['subjects'] = $subject.val();
                        query['created'] = $since.val();
                        query['sort'] = $sort.val();
                    };

                    if (force || query.term != previous && !options) {
                        search.search(query);
                        previous = query.term;
                    };
                    timeout = null;
                }, 500);
            };

            search.subscribe(CountDisplayPlugin($form.find('span.searchResultsCount')));
            search.subscribe(ResultDisplayPlugin($form.find('dl.searchResults'), $form.find('div.emptySearchResults')));
            search.subscribe(BatchDisplayPlugin($form.find('div.listingBar'), scroll_search));

            $form.find('a.esSearchOptions').bind('click', function (event) {
                options = !options;
                $options.slideToggle();
                event.preventDefault();
            });
            $button.bind('click', function(event) {
                schedule_search(true);
                event.preventDefault();
            });
            $options.delegate('input,select', 'change', schedule_search);
            $query.bind('change', schedule_search);
            $query.bind('keypress', schedule_search);
            if ($query.val()) {
                schedule_search();
            };

        });
    });

})(jQuery);
