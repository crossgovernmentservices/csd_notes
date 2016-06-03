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

  function setEditMode(event) {
    event.preventDefault();
    event.stopPropagation();

    $('.edit-mode').removeClass('edit-mode');
    $(this).closest('.editable').addClass('edit-mode');
  }

  function enhanceTagForm() {
    var $section = $(this);
    var $base_form = $section.find('form');
    $base_form.find('button').remove();

    $section.find('.tag-entry-group').each(function () {
      var $tag = $(this);
      var $form = $('<form method="post">').attr('action', $base_form.attr('action'));
      $tag.wrap($form);
      $tag.find('input').each(function () {
        var $input = $(this);
        $input.attr('name', $input.attr('name').replace(/tag-\d+-(.*)/, 'tag-0-$1'));
      });
      $tag.append($('<button class="save-btn button">Save</button>'));
      $tag.append($('<button class="secondary-btn button">Delete</button>'));

      $tag.find('input[type=text]').on('input keypress', function () {
        var $input = $(this);
        if ($input.val() != $input.data('initial')) {
          $tag.addClass('changed');
        } else {
          $tag.removeClass('changed');
        }
      });
    });

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

    $('.edit-link').on('click', setEditMode);

    $('.tag-list-edit').each(enhanceTagForm);

    $('.editable.search-term').each(editableSearchTerm);
  });

}).call(this, jQuery, window);
