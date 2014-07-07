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

/* bidirectional infinite scrolling */

var TARGET_INIT = 0;
var TARGET_BOTTOM = 1;
var TARGET_TOP = 2;

function InfiniteScrolling (type){

  var that = this;
  this.type = type;
  this.cache = new Object({ IDs: [] });

  this.init = function (itemSelector, slot, builder, reloadingCallbacks = [], refreshRate = 3000, 
			fillingPower = 20, itemsPerReload = 5){

    this.itemSelector = itemSelector;
    this.slot = slot;
    this.builder = builder;
    this.reloadingCallbacks = reloadingCallbacks;
    this.refreshRate = refreshRate;
    this.fillingPower = fillingPower;
    this.itemsPerReload = itemsPerReload;
    this.cache = new Object({ IDs : [] });

    $(document).scroll(function(e){

      if ($("#info-older-items").is(":visible")){
	var scrollPos = $(window).scrollTop();
	if (scrollPos < $("#info-older-items").offset().top){
	  $(window).scrollTop($("#info-older-items").offset().top);
	}
	e.preventDefault();
      }

    });

    this.createInitSpinner();

  }

  this.showFromStart = function(){
    this.resetContainer();
    this.refreshCache(this.initView);
  }

  this.scroll = function(){
    that.checkBottom();
    that.checkTop();
  }

  this.resetContainer = function(){
    that.createInitSpinner();
    $("#itemcontainer").html("");
  }

  this.refreshCache = function(callback){
    $.ajax({
      url: this.slot,
      type: "GET", 
      error: handleAjaxErrorBy(alertGlobal),
      success: callback,
    });
  }

  this.initView = function(freshCache){
    that.cache = freshCache;
    that.resetContainer();
    that.fetchItems(0, that.fillingPower, TARGET_INIT, [that.removeInitSpinner]);
    setTimeout(function(){
      that.refreshCache(that.triggerCacheChangeEvent);
    }, 
    that.refreshRate);
  }

  this.triggerCacheChangeEvent = function(freshCache){
    //XXX: FIXME: ignore order
    if( JSON.stringify(that.cache) !== JSON.stringify(freshCache) ){
      $("#itemcontainer").trigger("cachechanged", freshCache)
      setTimeout(function(){
	that.refreshCache(triggerCacheChangeEvent);
      }, 
      that.refreshRate);
    }
  }

  this.jumpCallback = function(freshCache, itemID){
    var index = freshCache.IDs.indexOf(itemID);
    if (index >= 0) {
      this.cache = freshCache;
      this.fetchItems(index, index + that.fillingPower, TARGET_INIT, [this.removeInitSpinner, 
        function (){
          var jumpHere = $(that.itemSelector + "[cache-index=\"" + index + "\"]").first();
          that.checkTop();
	  var jumpPos = jumpHere.offset().top;
          $(window).scrollTop(jumpPos);
        }
      ]);
      setTimeout(function(){
	that.refreshCache(that.triggerCacheChangeEvent);
      }, 
      that.refreshRate);
    }else{
      this.initView(freshCache);
    }
  }

  this.jumpTo = function(itemID){
    this.resetContainer();
    var itemID = parseInt(itemID);
    this.refreshCache(function(freshCache){ 
      that.jumpCallback(freshCache, itemID);
    });
  }

  this.createInitSpinner = function(){
    $("#itemloader-top").children().fadeOut(0);
    $("#info-init").fadeIn(400); 
    $("#itemcontainer").addClass("contentspinner");
  } 

  this.removeInitSpinner = function(){
    $("#itemcontainer").removeClass("contentspinner");
    $("#info-init").fadeOut(0);
  }

  this.checkBottom = function(){
    if ($("#itemloader-bottom").visible()){
      var last = $(this.itemSelector).last();
      var start = parseInt(last.attr("cache-index")) + 1;
      var stop = start + that.itemsPerReload;
      that.fetchItems(start, stop, TARGET_BOTTOM);
    };
  }

  this.checkTop = function(){
    if ($("#itemloader-top").visible()){
      var first = $(that.itemSelector).first();
      var firstCacheIndex = parseInt(first.attr("cache-index"));
      var start = firstCacheIndex - that.itemsPerReload;
      var stop = firstCacheIndex;
      that.fetchItems(start, stop, TARGET_TOP);
    };
  }

  this.clearLoadingMessages = function(){
    $("#info-older-items").fadeOut(0);
    $("#info-newer-items").fadeOut(0);
  }

  this.fetchItems = function(cache_start, cache_stop, target, callbacks = []){

    if (cache_start == this.cache.IDs.length){
      if (!$("#info-rockbottom").is(":visible")){
	$("#itemloader-bottom").children().fadeOut(0);
	$("#info-rockbottom").fadeIn(200);
      }
      return false;
    }

    if (cache_start < 0){
      cache_start = 0;
    }

    if (cache_stop > this.cache.IDs.length){
      cache_stop = this.cache.IDs.length;
    }

    if (!(cache_start - cache_stop)){
      return false;
    }

    var container = $("#itemcontainer");
    // XXX
    var defaultCallbacks = [this.removeSemaphore, this.clearLoadingMessages];
    var globalCallbacks = defaultCallbacks.concat(that.reloadingCallbacks);
    var callbacks = globalCallbacks.concat(callbacks);
    console.log(callbacks);

    /* only trigger ajax, if no loading process is active */
    if (container.attr("reloading") === "false"){


      /* set semaphore */
      this.addSemaphore();
      IDs = this.cache.IDs.slice(cache_start, cache_stop);
      var data = new Object({ IDs: IDs });
      var json = $.toJSON(data);

      if (target === TARGET_TOP){
	$("#info-older-items").fadeIn(200);
      }else if (target === TARGET_BOTTOM){
	$("#info-newer-items").fadeIn(200);
      }

      /* fetch items */
      $.ajax({
        url: this.builder,
        data: json,
        error: handleAjaxErrorBy(alertGlobal),
        success: function (response) { 

          var block = $($.parseHTML(response))
          if (target === TARGET_TOP){
            that.prependBlock(block, cache_start);
          }else{
     	    that.appendBlock(block, cache_start);
          }

        },
        complete: callbacks
      });

    }

  }

  this.injectCacheIndexAttributes = function(cache_start){

    var newItems = $(this.itemSelector + ":not([cache-index])");    
    var index = cache_start;
    $(newItems).each(function(){
      $(this).attr("cache-index", index);
      index++;
    });
/*
    var first = $(this.itemSelector + "[cache-index]").first();
    var last = $(this.itemSelector + "[cache-index]").last();
    if (first.length > 0 || last.length > 0){

      var previous = first.prevAll();

      if ( previous.length > 0 ){
        var firstIndex = parseInt(first.attr("cache-index"));
        var index = firstIndex - 1;
        previous.each(function(){
          $(this).attr("cache-index", index);
          index--;
        });
      }

      var next = last.nextAll();

      if ( next.length > 0 ){
        var lastIndex = parseInt(last.attr("cache-index"));
        var index = lastIndex + 1;
        next.each(function(){
          $(this).attr("cache-index", index);
          index++;
        });
      }

    }else{
      //$(this.itemSelector).first();
      var index = 0;
      $(this.itemSelector).each(function(){
        $(this).attr("cache-index", index);
        index++;
      });

    }*/
  }

  this.prependBlock = function (block, cache_start){

    $("#itemcontainer").prepend(block);
    
    var newItems = $(this.itemSelector + ":not([cache-index])");

    var ghostHeight = 0;
    newItems.each(function(){
      ghostHeight += $(this).outerHeight();
    });

    this.injectCacheIndexAttributes(cache_start);

    var newScrollPos = $(window).scrollTop() + ghostHeight;
    $(window).scrollTop(newScrollPos);

    if ($(this.itemSelector).length > this.fillingPower){
      var diff = this.fillingPower - $(this.itemSelector).length;
      $(this.itemSelector).slice(diff).remove();
      if ($("#info-rockbottom").is(":visible")){
        $("#info-rockbottom").fadeOut(0);
      }
    }

  }

  this.appendBlock = function (block, cache_start){

    $("#itemcontainer").append(block);

    this.injectCacheIndexAttributes(cache_start);

    if ($(this.itemSelector).length > this.fillingPower){
      var diff = $(this.itemSelector).length - this.fillingPower;
      var dispensableItems = $(this.itemSelector).slice(0, diff)
      var ghostHeight = 0;
      dispensableItems.each(function(){
        ghostHeight += $(this).outerHeight();
      });

      var newScrollPos = $(window).scrollTop() - ghostHeight;
      $(window).scrollTop(newScrollPos);

      dispensableItems.remove();
    }

  }

  this.addSemaphore = function(){
    $("#itemcontainer").attr("reloading", "true");
  }

  this.removeSemaphore = function(){
    $("#itemcontainer").attr("reloading", "false");
  }

}
