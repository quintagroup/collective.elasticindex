
(function($) {
    // Hang on in there. We have jQuery, 1.4.

    $(document).ready(function() {
        $('.esSearchForm').each(function() {
            var $form = $(this),
                $count = $form.find('span.searchResultsCount'),
                $empty = $form.find('div.emptySearchResults'),
                $result = $form.find('dl.searchResults'),
                search_urls = $form.data('server-urls'),
                index_name = $form.data('index-name');

            var query = function(url, term) {
                // Form up any query here
                var query = {
                    query: {
                        multi_match : {
                            query  : term,
                            fields : [
                                "author^2",
                                "title^2",
                                "subject^2",
                                "description",
                                "content"
                            ]
                        }
                    },
                    highlight: {
                        fields: {
                            title: {number_of_fragments: 0},
                            description: {fragment_size: 150, number_of_fragments: 3}
                        }
                    },
                    fields: ['url', 'title', 'description']
                };
                $.ajax({
                    url: url,
                    type: 'POST',
                    crossDomain: true,
                    dataType: 'json',
                    success: function(data) {
                        var entry, i, len;
                        var title, description, url;

                        $count.text(data.hits.total);
                        $result.empty();
                        if (!data.hits.total) {
                            $empty.show();
                            $result.hide();
                        } else {
                            $empty.hide();
                            $result.show();
                            for (i=0; i < data.hits.total; i++) {
                                entry = data.hits.hits[i];
                                title = (entry.highlight && entry.highlight.title) || entry.fields.title;
                                description = (entry.highlight && entry.highlight.description) || entry.fields.description;
                                url = entry.fields.url;
                                $result.append(
                                    '<dt class="contenttype-document"><a href="'
                                        + url + '">' + title + '</a></dt><dd>' + description + '</dd>'
                                );
                            };
                        };
                    },
                    data: JSON.stringify(query)
                });
            };

            var get_url = function() {
                var index = Math.floor(Math.random() * search_urls.length);
                return [search_urls[index], '/', index_name, '/_search'].join('');
            };

            var $field = $form.find('input[type=text]'),
                $button = $form.find('input[type=submit]'),
                previous = null,
                timeout = null;

            var schedule_search = function() {
                if (timeout !== null) {
                    clearTimeout(timeout);
                };
                timeout = setTimeout(function () {
                    var term = $field.attr('value');

                    if (term != previous) {
                        query(get_url(), term);
                        previous = term;
                    };
                    timeout = null;
                }, 500);
            };

            $button.bind('click', function(event) {
                schedule_search();
                event.preventDefault();
            });
            $field.bind('change', schedule_search);
            $field.bind('keypress', schedule_search);
            if ($field.attr('value')) {
                schedule_search();
            };

        });
    });

})(jQuery);
