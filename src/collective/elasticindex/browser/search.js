
(function($) {
    // Hang on in there. We have jQuery, 1.4.

    $(document).ready(function() {
        $('.es-search-form').each(function() {
            var $page = $(this),
                $result = $page.find('.es-search-results'),
                search_urls = $page.data('server-urls'),
                index_name = $page.data('index-name');

            function query(url, term) {
                // Form up any query here
                var query = {
                    query: {
                        term: { content: term }
                    }
                };
                $.ajax({
                    url: url,
                    type: 'POST',
                    crossDomain: true,
                    dataType: 'json',
                    success: function(data) {
                        var entry, i;

                        $result.empty();
                        for (i=0; i < data.hits.total; i++) {
                            entry = data.hits.hits[i];
                            $result.append(
                                '<li><a href="' + entry._source.url + '">' +
                                    entry._source.title + '</a></li>');
                        };
                    },
                    data: JSON.stringify(query),
                    async: false
                });
            };

            var get_url = function() {
                var index = Math.floor(Math.random() * search_urls.length);
                return [search_urls[index], '/', index_name, '/_search'].join('');
            };

            $page.find('input').each(function() {
                var $input = $(this),
                    previous = null,
                    timeout = null;

                var search = function() {
                    if (timeout != null) {
                        clearTimeout(timeout);
                    };
                    timeout = setTimeout(function () {
                        var term = $input.attr('value');

                        if (term != previous) {
                            query(get_url(), term);
                            previous = term;
                        };
                        timeout = null;
                    }, 500);
                };

                $input.bind('change', search);
                $input.bind('keypress', search);
                if ($input.attr('value')) {
                    search();
                };
            });

        });
    });

})(jQuery);
