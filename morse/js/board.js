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

$(document).on("ready", function () {

  function discoverVisibleTopics (){

    /* 
       discoverVisibleTopics() looks for topic items in the current 
       viewport and marks them as discovered via ajax. this include 
       removing the css fresh class
       */

    var topicItems = $(".topic-item").filter(function(){ 
      return $(this).visible(); 
    });

    /* collect ids of visible posts */
    var topicIDs = Array();
    topicItems.each(function () {
      topicID = $(this).attr("topic-id");
      topicIDs.push(topicID);
    });

    var data = new Object({topicIDs: topicIDs});
    var json = $.toJSON(data);

    /* only send, if topics were found */
    if (topicIDs.length > 0){
      $.ajax({
        url: "/topics/discover",
        data: json,
        error: handleAjaxErrorBy( alertGlobal ),
        success: function () { topicItems.removeClass("fresh"); },
      });
    }

  }
  function rebindTopicItemEvents () {

  $(".close-topic").off("click");
  $(".close-topic").on("click", function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");

    $.ajax({
      url: "/topic/" + topicID + "/close",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.closedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.addClass("topicclosed");
        item.find(".close-topic").fadeOut(0);
        item.find(".reopen-topic").fadeIn(200);
      },
    });
  });

  $(".reopen-topic").off("click");
  $(".reopen-topic").on("click", function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");

    $.ajax({
      url: "/topic/" + topicID + "/reopen",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.openedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.removeClass("topicclosed");
        item.find(".reopen-topic").fadeOut(0);
        item.find(".close-topic").fadeIn(200);
      },
    });
  });

  }

  /* follow switch */
  $("#follow-board").click(function(){
    var boardID = $("#board").attr("board-id");
    var that = $(this);

    $.ajax({
      url: "/board/" + boardID + "/follow",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
      },
    });
  });

  $("#unfollow-board").click(function(){
    var boardID = $("#board").attr("board-id");
    var that = $(this);

    $.ajax({
      url: "/board/" + boardID + "/unfollow",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
      },
    });
  });

  $(".order-option").click(function(){
    if ($(this).hasClass("option-selected")){
      var switched = $(this).attr("switched");
      var html = $(this).html();
      console.log(switched);
      $(this).attr("switched", html );
      $(this).html( switched );
    }
    $(".order-option").removeClass("option-selected");
    $(this).addClass("option-selected");
    $("#active-order").html( $(this).html() );
  });

  $("#new-topic-button").click(function(){
    showNewContributionField();
  });

  $("#top-action").mouseenter(function(){

    /* block if divs are still in motion */
    var currentTop = parseInt($("#board-title").css("top"));
    if (currentTop > 0) { return true; }

    var height = $("#top-action a").height();
    var timer = setTimeout(function(){
      $("#board").animate( { top : height + "px" }, {duration: 500 });
      $("#board-description").animate( { top : height + "px" }, {duration: 500 });
      $("#board-title").animate( { top : height + "px" }, {duration: 500, complete: fadeInTopActionInfo });
    }, 400);
    $(this).data("toolRevealDelay", timer);

  });  

  function fadeInTopActionInfo (){
    $("#top-action a").fadeIn(200);
  }

  $("#top-action").mouseleave(function(){

    /* clear timer, that was triggered on mousenter */
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);

    fadeOutTopActionInfo();
    $("#board-title").animate( { top : "0" }, {duration: 500});
    $("#board-description").animate( { top : "0" }, {duration: 500});
    $("#board").animate( { top : "0" }, {duration: 500});

  });  

  function fadeOutTopActionInfo (){
    $("#top-action a").fadeOut(200);
  }

  $("#board-title").swipeSnap( { target: "top", snapInfo: $("#snap-tooltip-top"), 
                                 companions: [$("#board"), $("#board-description")], 
                                 callback: gotoBoardIndex });

  function gotoBoardIndex (){
    window.location = "/";
  }

  /* bidirectional infinite scrolling */
  var slot = "/board/" + $("#board").attr("board-id") + "/topics.json";
  var builder = "/board/" + $("#board").attr("board-id") + "/certaintopics";
  var scrolling = new InfiniteScrolling();
  scrolling.init(".topic-item", slot, builder, [rebindToolTipEvents, rebindTopicItemEvents, 
                                               checkForUnreadPosts, discoverVisibleTopics], 3000, 20, 5);
  scrolling.showFromStart();
 
  $(window).scroll(scrolling.scroll, discoverVisibleTopics);

  $("#itemcontainer").on("emptycontainer", function(){
    $("#no-topics-yet").fadeIn(200);
  });

  $(".filter-option .checkbox").change(function(){
    var filterStatus = [];
    $(".filter-option .checkbox").each(function(){
      var id = $(this).attr("id");
      var active = $(this).is(":checked");
      filterStatus.push( [id, active] );
    });
    var data = new Object({filterStatus: filterStatus});
    var json = $.toJSON(data);
    $.ajax({
      url: "/filter/topics",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(){
        $("#no-topics-yet").fadeOut(0);
	    scrolling.showFromStart();
        updateTopicCache();
      },
    });
  });

  function updateTopicCache (){
    var boardID = $("#board").attr("board-id");
    $.ajax({
      url: "/board/" + boardID + "/update-topic-cache",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
    });
  }

  function checkForUnreadPosts (){ 
    $(".topic-item").each(function(){
      var topicItem = $(this);
      if (topicItem.attr("topic-followed") === "True"){
        var topicID = topicItem.attr("topic-id");
        $.ajax({
          url: "/topic/" + topicID + "/unread.json",
          error: handleAjaxErrorBy( alertGlobal ),
          type: "GET", 
          success: function(response){
            updateSideCounter(topicItem, response.unreadCount); 
          },
        });
      }
    });   
 
    setTimeout(checkForUnreadPosts, 5000);
  }

  function updateSideCounter (topicItem, count){
    var counter = topicItem.children(".item-side-counter");
    if (parseInt(counter.html()) === count){
      return true;
    }
    counter.html(count);
    counter.fadeIn(500);
  }

});

function showNewContributionField (){
  $("#new-topic-button").slideUp(400);
  $("#new-contribution").slideDown(400);
  $("#new-topic-title").focus();
}
