(function($, window) {

  function expandToFitContent() {
    var $textarea = $(this);
    var vPadding = (
      parseInt($textarea.css('padding-top')) +
      parseInt($textarea.css('padding-bottom')));

    function fitContent() {
      $textarea.height($textarea.prop('scrollHeight') - vPadding);
    }

    $textarea.css({'overflow-y': 'hidden'});
    $textarea.on('input focus', fitContent);

    fitContent();
  }

  function editOnClick() {
    var $el = $(this);

    function deactivate(event) {
      event.stopPropagation();
      $('.editOnClick.active.edit-mode').removeClass('active edit-mode');
    }

    function activate(event) {
      deactivate(event);
      $el.addClass('active edit-mode');
    }

    function edit(event) {
      activate(event);
      $el.find('textarea').focus();
    }

    $el.find('textarea').on('keydown', activate);
    $el.find('input[name="tags"]').on('click', function (event) {
      event.stopPropagation();
    });
    $el.find('.close-btn').on('click', deactivate);
    $el.find('.cancel').on('click', deactivate);
    $el.on('click', edit);
  }

  function editableSearchTerm() {
    var $el = $(this);
    var $input = $('<input class="hidden editable search-term">').insertAfter($el);

    function edit() {
      $el.addClass('hidden');
      $input.removeClass('hidden');
      $input.val($.trim($el.text()));
      $input.focus().select();
    }

    function search() {
      document.location.search = '?q=' + $(this).val();
    }

    function cancel() {
      $el.removeClass('hidden');
      $input.addClass('hidden');
      $el.text($(this).val());
    }

    $el.on('click', edit);
    $input.on('change', search);
    $input.on('blur', cancel);
  }

  function tagInput() {
    var $el = $(this);
    var $tags = $el.parents('section').siblings('.tag-list').find('.note-tag').clone();
    var $taglist = $('<ul>');
    var $input = $el.find('input[type=text]');
    var $searchBox = $input.clone();
    $searchBox.removeAttr('name');
    $searchBox.on('click', function (event) { event.stopPropagation(); });
    $input.removeClass('incremental-search');
    $input.hide();
    $input.val('');
    var $searchItem = $('<li class="search">');
    $searchItem.append($searchBox);
    $taglist.append($searchItem);
    $el.append($taglist);

    function makeTag(tagName) {
      var $tag = $('<li class="note-tag"/>');
      var $link = $('<a href="/notes/tag/' + tagName + '">' + tagName + '</a>');
      $tag.append($link);
      addRemoveBtn($tag);
      return $tag;
    }

    function addRemoveBtn($tag) {
      var $removeBtn = $('<a class="removeTag">×</a>');
      $tag.append($removeBtn);
      $removeBtn.on('click', removeTag);
      return $tag;
    }

    function appendTag($tag) {
      $tag.insertBefore($searchItem);
      var tagName = $tag.text().slice(0, -1);
      var tags = $input.val();
      tags += (tags.length ? ',' : '') + tagName;
      $input.val(tags);
    }

    function removeTag(event) {
      event.preventDefault();
      var $tag = $(event.target).parent();
      var tagName = $tag.text().slice(0, -1);
      var tags = $input.val().split(',');
      tags.splice(tags.indexOf(tagName), 1);
      if (tags.length) {
        tags = tags.join(',');
      } else {
        tags = '';
      }
      $input.val(tags);
      $tag.remove();
    }

    $el.on('selectResult', function (event) {
      event.stopPropagation();
      appendTag(makeTag(event.searchResult.name));
      $searchBox.val('');
    });

    $tags.each(function () {
      var $tag = $(this);
      addRemoveBtn($tag);

      function selectTag(event) {
        event.preventDefault();
        console.log('select tag', $tag.find('a').first().text());
      }

      $tag.find('a').first().on('click', selectTag);
      appendTag($tag);
    });
  }

  $(function() {
    $('.editOnClick').each(editOnClick);

    $('.expandToFitContent').each(expandToFitContent);

    $('.tag-input').each(tagInput);

    $('.add-note-form').find('textarea').focus();

    $('body').on('click', function () {
      $('.undo-link').hide().next('.note-date').removeClass('hidden');
    });

    $('.undo-link').on('click', function (event) {
      event.stopPropagation();
    });

    $('.editable.search-term').each(editableSearchTerm);
  });

}).call(this, jQuery, window);
