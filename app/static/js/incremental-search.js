$(function () {
  $('.incremental-search').each(enableIncrementalSearch);

  function enableIncrementalSearch() {
    var $searchBox = $(this);
    var searchUrl = $searchBox.data('search-url');

    var $field = $('<input type="hidden" name="id">');
    $field.insertAfter($searchBox);

    var $resultList = $('<ol class="incremental-search-results"/>');
    $resultList.insertAfter($searchBox);

    var delayTimer = null;
    var delay = 200;

    $searchBox.on('keypress', function () {

      if (delayTimer) {
        clearTimeout(delayTimer);
      }

      delayTimer = setTimeout(function () {
        var term = $searchBox.val();
        console.log(term);
        search(searchUrl, term, showResults($resultList, option(highlight(term))));
      }, delay);
    });

  }

  function search(url, term, callback) {
    $.getJSON(url, {"q": term}, callback);
  }

  function showResults(resultList, widget) {
    return function (data) {

      resultList.empty();

      for (var i in data.results) {
        resultList.append(widget(data.results[i]));
      }

    };
  }

  function option(format) {
    return function (result) {
      var widget = $('<li>' + format(result.name) + '</li>');
      //widget.on('click', function () { submit(result.name, result.value); });
      return widget;
    };
  }

  function highlight(term) {
    return function (s) {
      return s.replace(new RegExp(term, 'i'), '<b>$&</b>');
    };
  }

});
