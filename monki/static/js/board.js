"use strict";

var Board = (function($) {
  var $form = $('#id_form'),
      $textarea = $('#id_message'),
      $parent =  $('#id_parent');

  var init = function() {
    $form.on('submit', removeConfirmUnload);
    $textarea.on('keydown', submitPost);

    $('.quote-post').on('click', insertQuote);
    $('.ref').on('click', highlightPost);
    $('[data-hide]').on('click', updateHiddenPosts);

    $(window).on('beforeunload', confirmUnload);

    checkHighlight();
    quotePreview();
    highlightNewPosts();
    expandableImage();
    hidePosts();
  };

  var insertQuote = function(e) {
    var $this = $(this),
        postId = $this.data('post-id'),
        parentId = $this.data('parent-id'),
        currentValue,
        newValue;

    $parent.val(parentId);
    $('#reply-to').text('(Reply to: ' + parentId + ')');
    // TODO: add a link to back for 'new thread' button

    currentValue = $textarea.val();

    newValue = '>>' + postId + '\n'

    if (currentValue) {
      newValue = currentValue + '\n\n' + '>>' + postId + '\n';
    }

    $textarea.val(newValue);
    $textarea.focus();

    e.preventDefault();
  };

  var submitPost = function(e) {
    if (e.ctrlKey && e.keyCode == 13) {
      $form.submit();
    }
  };

  var confirmUnload = function() {
    if ($textarea.val()) {
      return 'Are you sure? your post will be lost';
    }
  };

  var removeConfirmUnload = function() {
    $(window).off('beforeunload');
  };

  var highlightPost = function(e) {
    var postId = $(this).data('post-id'),
        post = $('#post-' + postId + '.reply');

    $('.highlight').removeClass('highlight');

    if (post.length) {
      post.addClass('highlight');
      window.location.hash = 'post-' + postId;
      e.preventDefault();
    }
  };

  var checkHighlight = function() {
    var match,
        location = document.location.toString();

    if (match = /#post-(\d+)/.exec(location)) {
      $('#post-' + match[1] + '.reply').addClass('highlight');
    }
  };

  var quotePreview = function() {
    $('.ref').tooltipster({
      content: 'Loading...',
      contentAsHTML: true,
      animationDuration: 0,
      interactive: true,
      trigger: 'hover',
      theme: 'tooltipster-fuhrerchan',


      functionBefore: function(instance, helper) {
        var $origin = $(helper.origin),
            postId = $origin.data('post-id'),
            $post = $('#post-' + postId);

        if ($post.length) {
          instance.content($post.clone().removeAttr('id').removeClass('highlight').addClass('reply'));
          return true;
        }

        if (!$origin.data('loaded')) {
          $.get('/post/' + postId + '/', function(data) {
            instance.content(data);
            $origin.data('loaded', true)
          });
        }

        return true;
      },

    });
  };

  var expandableImage = function() {
    $('.expandable').expandable();
  };

  var highlightNewPosts = function() {
    var lastVisit = localStorage.getItem('lastVisit'),
        now = new Date().toISOString();

    if (!lastVisit) {
      lastVisit = {}
    }
    else {
      lastVisit = JSON.parse(lastVisit);
    }

    var obj = lastVisit
    obj[window.app.board] = now

    $.get('/api/boards/', function(data) {
      $.each(data, function(_, board) {
        var el = $('a[data-dir="' + board.directory + '"]');

        if ((board.last_post > obj[board.directory]) || (obj[board.directory] == undefined)) {
          el.addClass('highlight');
        }
      });
    });

    lastVisit = JSON.stringify(obj);
    localStorage.setItem('lastVisit', lastVisit);
  };

  var updateHiddenPosts = function(e) {
    var $this = $(this),
        postId = $this.data('hide'),
        $post = $('#post-' + postId),
        hiddenPosts = localStorage.getItem('hiddenPosts');

    if (!hiddenPosts) {
      hiddenPosts = []
    }
    else {
      hiddenPosts = JSON.parse(hiddenPosts);
    }

    if ($post.hasClass('hide')) {
      $this.html('Hide');
      $post.removeClass('hide');
    }
    else {
      $this.html('Un-hide');
      $post.addClass('hide');
    }

    var index = hiddenPosts.indexOf(postId);

    if (index > -1) {
      hiddenPosts.splice(index, 1);
    }
    else {
      hiddenPosts.push(postId);
    }

    hiddenPosts = JSON.stringify(hiddenPosts);
    localStorage.setItem('hiddenPosts', hiddenPosts);

    e.preventDefault();
  };

  var hidePosts = function() {
    var hiddenPosts = localStorage.getItem('hiddenPosts');

    if (hiddenPosts) {
      hiddenPosts = JSON.parse(hiddenPosts);

      hiddenPosts.map(function(i) {
        var $post = $('#post-' + i),
            $hide = $('[data-hide="' + i +'"]');

        $post.addClass('hide');
        $hide.html('Un-hide');
      });
    }
  };

  return {
    init: init,
  };
}(jQuery));

$(document).ready(Board.init());
