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

    function activate() {
      $('.editOnClick.active.edit-mode').removeClass('active edit-mode');
      $el.addClass('active edit-mode');
    }

    function edit() {
      activate();
      $el.find('textarea').focus();
    }

    $el.find('textarea').on('keydown', activate);
    $el.on('click', edit);
  }

  $(function() {
    $('.editOnClick').each(editOnClick);

    $('.expandToFitContent').each(expandToFitContent);

    $('.add-note-form').find('textarea').focus();

    $('body').on('click', function () {
      $('.undo-link').hide().next('.note-date').removeClass('hidden');
    });
  });

}).call(this, jQuery, window);
