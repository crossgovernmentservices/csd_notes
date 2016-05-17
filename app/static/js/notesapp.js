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

  $(function() {
    $('.editOnClick').each(editOnClick);

    $('.expandToFitContent').each(expandToFitContent);

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
