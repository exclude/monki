function getDragSize(e) {
  var rc = e.target.getBoundingClientRect(),
      left = Math.pow(e.clientX - rc.left, 2),
      top = Math.pow(e.clientY - rc.top, 2),
      size = Math.pow(left + top, .5);

  return size;
}

function getHeight() {
  return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
}


(function($) {
  function Expandable(previewImage) {
    this.$previewImage = previewImage;
  }

  Expandable.prototype = {

    init: function() {
      var instance = this;  // due javascript scope madness

      instance.addHelperClass();
      instance.makeResizable();
      instance.makeExpandable();
    },

    addHelperClass: function() {
      var instance = this;
      instance.$previewImage.addClass('thumbnail');
    },

    makeResizable: function() {
      var instance = this;

      instance.$previewImage.on('mousedown', instance.mouseDown);
      instance.$previewImage.on('mousemove', instance.mouseMove);
      instance.$previewImage.on('mouseup', instance.mouseUpAndOut);
      instance.$previewImage.on('mouseout', instance.mouseUpAndOut);
      instance.$previewImage.on('click', instance.mouseClick);
    },

    mouseDown: function(e) {
      var $this = $(this);

      if ($this.hasClass('fullsize')) {
        if (e.button == 0) {
          $this.data('innerWidth', $this.width());
          $this.data('d', getDragSize(e));
          $this.data('dr', false);

          e.preventDefault();
        }
      }
    },

    mouseMove: function(e) {
      var $this = $(this);

      if ($this.data('d')) {
        var newWidth = getDragSize(e) * ($this.data('innerWidth') / $this.data('d'));

        $this.css('width', newWidth);
        $this.css('maxWidth', newWidth);
        $this.css('height', 'auto')
        $this.css('zIndex', 1000);

        $this.data('dr', true);
      }
    },

    mouseUpAndOut: function(e) {
      var $this = $(this);

      $this.data('d', false);

      if ($this.data('dr')) {
        e.stopPropagation();
      }
    },

    mouseClick: function(e) {
      var $this = $(this);

      $this.data('d', false);

      if (($this.data('dr')) && ($this.hasClass('fullsize'))) {
        e.stopImmediatePropagation();
      }
    },

    makeExpandable: function() {
      var instance = this;

      instance.$previewImage.on('click', function(e) {
        if (instance.$previewImage.data('mode') == 'video') {
          instance.loadVideo();
        }
        else {
          instance.loadImage();
        }
      });
    },

    loadVideo: function(e) {
      var instance = this;

      if (instance.hasPlayer) {
        instance.$previewImage.hide();

        instance.$videoPlayer.show();
        instance.$videoPlayer[0].play()
      }
      else {
        var alt = instance.$previewImage.data('alt');

        instance.$videoPlayer = $([
          '<video autoplay loop controls>',
          '<source type="video/webm" src="' + alt + '">',
          '</video>'
        ].join('\n'));

        instance.$videoPlayer.on('click', function() {
          instance.$previewImage.show()

          instance.$videoPlayer.hide();
          instance.$videoPlayer[0].pause()
        });

        instance.$previewImage.hide();
        instance.$videoPlayer.insertBefore(instance.$previewImage);

        instance.hasPlayer = true;
      }
    },

    loadImage: function(e) {
      var $image = this.$previewImage;

      var alt = $image.data('alt'),
          src = $image.attr('src');

      $image.addClass('loading');

      $image.off('load');  // avoid event stack
      $image.on('load', function() {
        var $this = $(this);

        $this.removeClass('loading');
        $this.toggleClass('fullsize');
        $this.toggleClass('thumbnail');

        // remove limits, this is only important when page loads
        // to avoid element "blinking".
        $this.attr('width', '');
        $this.attr('height', '');
      });

      $image.css({'width': '', 'maxWidth': '', 'height': '', 'zIndex': ''});

      $image.attr('src', alt);
      $image.data('alt', src);
    },
  }

  $.fn.expandable = function() {
    this.each(function() {
      var $previewImage = $(this);

      var expandable = new Expandable($previewImage);
      expandable.init();
    });
  };

})(jQuery);
