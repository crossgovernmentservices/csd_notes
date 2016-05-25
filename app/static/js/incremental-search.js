$(function () {
  $('.incremental-search').each(enableIncrementalSearch);

  function enableIncrementalSearch() {
    var $searchBox = $(this);
    var searchUrl = $searchBox.data('search-url');

    var $resultList = $('<ol class="incremental-search-results"/>');
    $resultList.insertAfter($searchBox);
    $resultList.on('selectResult', function (event) {
      $resultList.hide();
      $searchBox.trigger(event);
    });

    $searchBox.on('keypress', delayedSearch);

    var delayTimer = null;
    var delay = 200;

    function delayedSearch() {
      if (delayTimer) {
        clearTimeout(delayTimer);
      }

      delayTimer = setTimeout(search, delay);
    }

    function search() {
      var term = $searchBox.val();
      $.getJSON(searchUrl, {"q": term}, showResults(term));
    }

    function showResults(term) {
      return function (data) {
        $resultList.empty();

        if (data.results.length > 0) {
          $resultList.show();
          $resultList.append(data.results.map(option(highlight(term))));

        } else {
          $resultList.hide();
        }
      };
    }
  }

  function option(format) {
    return function (result) {
      var widget = $('<li>' + format(result.name) + '</li>');
      widget.on('click', function (event) {
        event.stopPropagation();
        widget.trigger($.Event('selectResult', {'searchResult': result}));
      });
      return widget;
    };
  }

  function highlight(term) {
    return function (s) {
      return s.replace(new RegExp(term, 'i'), '<b>$&</b>');
    };
  }

});
