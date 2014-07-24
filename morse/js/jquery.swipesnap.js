/*
    This file is part of Morse.

    Morse is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morse is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Morse.  If not, see <http://www.gnu.org/licenses/>.
*/

(function ( $ ) {

    $.fn.swipeSnap = function( options ) {

      this.css("position", "relative");

      var opt = $.extend( {}, $.fn.swipeSnap.defaults, options );
      $.each(opt.companions, function(index, item){
        item.css("position", "relative");
      });

      if (opt.target === "top"){

        if (this.css("top") === "auto"){
          this.css("top", "0px");
        }    

        $.each(opt.companions, function(index, item){
          if (item.css("top") === "auto"){
            item.css("top", "0px");
          }    
        });

        $.fn.swipeSnap.topActive = true;
        $.fn.swipeSnap.topOptions = opt;
        this.swipe( { swipeStatus: $.fn.swipeSnap.snapVertical } );

      }else
      if (opt.target === "bottom"){

        if (this.css("top") === "auto"){
          this.css("top", "0px");
        }    

        $.each(opt.companions, function(index, item){
          if (item.css("top") === "auto"){
            item.css("top", "0px");
          }    
        });

        $.fn.swipeSnap.bottomActive = true;
        $.fn.swipeSnap.bottomOptions = opt;
        this.swipe( { swipeStatus: $.fn.swipeSnap.snapVertical } );

      }else
      if (opt.target === "left"){

        if (this.css("left") === "auto"){
          this.css("left", "0px");
        }    

        $.each(opt.companions, function(index, item){
          if (item.css("left") === "auto"){
            item.css("left", "0px");
          }    
        });

        $.fn.swipeSnap.leftActive = true;
        $.fn.swipeSnap.leftOptions = opt;
        this.swipe( { swipeStatus: $.fn.swipeSnap.snapHorizontal, allowPageScroll: "vertical" } );

      }else
      if (opt.target === "right"){

        if (this.css("left") === "auto"){
          this.css("left", "0px");
        }    

        $.each(opt.companions, function(index, item){
          if (item.css("left") === "auto"){
            item.css("left", "0px");
          }    
        });

        $.fn.swipeSnap.rightActive = true;
        $.fn.swipeSnap.rightOptions = opt;
        this.swipe( { swipeStatus: $.fn.swipeSnap.snapHorizontal, allowPageScroll: "vertical" } );

      } 
    };

    $.fn.swipeSnap.topActive = false;
    $.fn.swipeSnap.bottomActive = false;
    $.fn.swipeSnap.leftActive = false;
    $.fn.swipeSnap.rightActive = false;
    
    $.fn.swipeSnap.defaults = { companions: [], callback: undefined, 
                                snapInfo: undefined, fadeDuration: 200,
                                snapBackDuration: 500 }


    $.fn.swipeSnap.snapVertical = function (event, phase, direction, 
                                            distance, duration, fingers) {
      var topOptions = undefined;
      var topSnapActionThreshold = undefined;
      var topSnapBottomBoundary = undefined;

      if ($.fn.swipeSnap.topActive){
        var topOptions = $.fn.swipeSnap.topOptions;
        var topSnapActionThreshold = topOptions.snapInfo.outerHeight();
        var topSnapBottomBoundary = topSnapActionThreshold * 2;
      }

      var bottomOptions = undefined;
      var bottomSnapActionThreshold = undefined;
      var bottomSnapTopBoundary = undefined;

      if ($.fn.swipeSnap.bottomActive){
        var bottomOptions = $.fn.swipeSnap.bottomOptions;
        var bottomSnapActionThreshold = - bottomOptions.snapInfo.outerHeight();
        var bottomSnapTopBoundary = bottomSnapActionThreshold * 2;
      }

      if (phase === "start"){

        var topValue = parseInt($(this).css("top"));
        $.fn.swipeSnap.oldTopValue = topValue;

      }else if (phase === "move"){

        var relative_distance = 0;
        if (direction === "up"){
          relative_distance = - distance;
        }else if (direction === "down"){
          relative_distance = distance;
        }

        var oldTopValue = $.fn.swipeSnap.oldTopValue;
        var newTopValue = oldTopValue + relative_distance;

        var topBoundary = $.fn.swipeSnap.bottomActive ? bottomSnapTopBoundary : oldTopValue;
        var bottomBoundary = $.fn.swipeSnap.topActive ? topSnapBottomBoundary : oldTopValue;

        if (newTopValue >= topBoundary && newTopValue < bottomBoundary){

          this.css("top", newTopValue + "px");

          if ($.fn.swipeSnap.topActive){          

            var companions = $.fn.swipeSnap.topOptions.companions;

            $.each(companions, function (index, item){
              item.css("top", newTopValue + "px");
            });

            var duration = topOptions.fadeDuration;
            if (newTopValue > topSnapActionThreshold && !topOptions.snapInfo.is(":visible")){
              topOptions.snapInfo.fadeIn(duration);
            }else 
            if (newTopValue < topSnapActionThreshold && topOptions.snapInfo.is(":visible")){
              topOptions.snapInfo.fadeOut(duration);
            }

          }

          if ($.fn.swipeSnap.bottomActive){

            var companions = $.fn.swipeSnap.bottomOptions.companions;

            $.each(companions, function (index, item){
              item.css("top", newTopValue + "px");
            });

            var duration = bottomOptions.fadeDuration;
            if (newTopValue < bottomSnapActionThreshold && !bottomOptions.snapInfo.is(":visible")){
              bottomOptions.snapInfo.fadeIn(duration);
            }else 
            if (newTopValue > topSnapActionThreshold && bottomOptions.snapInfo.is(":visible")){
              bottomOptions.snapInfo.fadeOut(duration);
            }

          }

        }

      }else if (phase === "end" || phase === "cancel"){

        var oldTopValue = $.fn.swipeSnap.oldTopValue;
        var currentTopValue = parseInt($(this).css("top"));

        if ($.fn.swipeSnap.topActive && currentTopValue > oldTopValue && 
            currentTopValue < topSnapBottomBoundary){

          var callback = undefined;

          if (topOptions.snapInfo.is(":visible")){
            callback = topOptions.callback;
          }

          topOptions.snapInfo.fadeOut(topOptions.fadeDuration);
          $.each(topOptions.companions, function (index, item){
            item.animate({ top: oldTopValue }, topOptions.snapBackDuration);
          });

          this.animate({ top: oldTopValue }, {duration: topOptions.snapBackDuration, 
                                              complete: callback});

        }else
        if ($.fn.swipeSnap.bottomActive && currentTopValue < oldTopValue && 
            currentTopValue > bottomSnapTopBoundary){

          var callback = undefined;

          if (bottomOptions.snapInfo.is(":visible")){
            callback = bottomOptions.callback;
          }

          bottomOptions.snapInfo.fadeOut(bottomOptions.fadeDuration);
          $.each(bottomOptions.companions, function (index, item){
            item.animate({ top: oldTopValue }, bottomOptions.snapBackDuration);
          });

          this.animate({ top: oldTopValue }, {duration: bottomOptions.snapBackDuration, 
                                              complete: callback});

        }

      }

    }
 
    $.fn.swipeSnap.snapHorizontal = function (event, phase, direction, 
                                              distance, duration, fingers) {
      var leftOptions = undefined;
      var leftSnapActionThreshold = undefined;
      var leftSnapRightBoundary = undefined;

      if ($.fn.swipeSnap.leftActive){
        var leftOptions = $.fn.swipeSnap.leftOptions;
        var leftSnapActionThreshold = leftOptions.snapInfo.outerWidth();
        var leftSnapRightBoundary = leftSnapActionThreshold * 2;
      }

      var rightOptions = undefined;
      var rightSnapActionThreshold = undefined;
      var rightSnapLeftBoundary = undefined;

      if ($.fn.swipeSnap.rightActive){
        var rightOptions = $.fn.swipeSnap.rightOptions;
        var rightSnapActionThreshold = - rightOptions.snapInfo.outerWidth();
        var rightSnapLeftBoundary = rightSnapActionThreshold * 2;
      }

      if (phase === "start"){

        var leftValue = parseInt($(this).css("left"));
        $.fn.swipeSnap.oldLeftValue = leftValue;

      }else if (phase === "move"){

        var relative_distance = 0;
        if (direction === "left"){
          relative_distance = - distance;
        }else if (direction === "right"){
          relative_distance = distance;
        }

        var oldLeftValue = $.fn.swipeSnap.oldLeftValue;
        var newLeftValue = oldLeftValue + relative_distance;

        var leftBoundary = $.fn.swipeSnap.rightActive ? rightSnapLeftBoundary : oldLeftValue;
        var rightBoundary = $.fn.swipeSnap.leftActive ? leftSnapRightBoundary : oldLeftValue;

        if (newLeftValue >= leftBoundary && newLeftValue < rightBoundary){

          this.css("left", newLeftValue + "px");

          if ($.fn.swipeSnap.leftActive){          

            var companions = $.fn.swipeSnap.leftOptions.companions;

            $.each(companions, function (index, item){
              item.css("left", newLeftValue + "px");
            });

            var duration = leftOptions.fadeDuration;
            if (newLeftValue > leftSnapActionThreshold && !leftOptions.snapInfo.is(":visible")){
              leftOptions.snapInfo.fadeIn(duration);
            }else 
            if (newLeftValue < leftSnapActionThreshold && leftOptions.snapInfo.is(":visible")){
              leftOptions.snapInfo.fadeOut(duration);
            }

          }

          if ($.fn.swipeSnap.rightActive){

            var companions = $.fn.swipeSnap.rightOptions.companions;

            $.each(companions, function (index, item){
              item.css("left", newLeftValue + "px");
            });

            var duration = rightOptions.fadeDuration;
            if (newLeftValue < rightSnapActionThreshold && !rightOptions.snapInfo.is(":visible")){
              rightOptions.snapInfo.fadeIn(duration);
            }else 
            if (newLeftValue > leftSnapActionThreshold && rightOptions.snapInfo.is(":visible")){
              rightOptions.snapInfo.fadeOut(duration);
            }

          }

        }

      }else if (phase === "end" || phase === "cancel"){

        var oldLeftValue = $.fn.swipeSnap.oldLeftValue;
        var currentLeftValue = parseInt($(this).css("left"));

        if ($.fn.swipeSnap.leftActive && currentLeftValue > oldLeftValue && 
            currentLeftValue < leftSnapRightBoundary){

          var callback = undefined;

          if (leftOptions.snapInfo.is(":visible")){
            callback = leftOptions.callback;
          }

          leftOptions.snapInfo.fadeOut(leftOptions.fadeDuration);
          $.each(leftOptions.companions, function (index, item){
            item.animate({ left: oldLeftValue }, leftOptions.snapBackDuration);
          });

          this.animate({ left: oldLeftValue }, {duration: leftOptions.snapBackDuration, 
                                              complete: callback});

        }else
        if ($.fn.swipeSnap.rightActive && currentLeftValue < oldLeftValue && 
            currentLeftValue > rightSnapLeftBoundary){

          var callback = undefined;

          if (rightOptions.snapInfo.is(":visible")){
            callback = rightOptions.callback;
          }

          rightOptions.snapInfo.fadeOut(rightOptions.fadeDuration);
          $.each(rightOptions.companions, function (index, item){
            item.animate({ left: oldLeftValue }, rightOptions.snapBackDuration);
          });

          this.animate({ left: oldLeftValue }, {duration: rightOptions.snapBackDuration, 
                                              complete: callback});

        }

      }

    }
}( jQuery ));

