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

  function readVisiblePosts (){

    /* 
       readVisiblePosts() looks for posts in the current viewport and
       marks them as read via ajax. this include removing the
       css fresh class
       */

    var postfooters = $(".postfooter").filter(function(){ 
      return $(this).visible(); 
    });

    /* collect ids of visible posts */
    var postIDs = Array();
    postfooters.each(function (){
      var postItem = $(this).parent();
      if (postItem.hasClass("fresh")){
        var postID = postItem.attr("post-id");
        postIDs.push(postID);
      }
    });

    var posts = postfooters.parent();
    var data = new Object({postIDs: postIDs});
    var json = $.toJSON(data);

    /* only send, if posts were found */
    if (postIDs.length > 0){
      $.ajax({
        url: "/posts/read",
        data: json,
        error: handleAjaxErrorBy( alertGlobal ),
        success: function () { posts.removeClass("fresh"); },
      });
    }

  }

  /* follow switch */
  $("#follow-topic").click(function(){
    var topicID = $("#topic").attr("topic-id");
    var that = $(this);

    $.ajax({
      url: "/topic/" + topicID + "/follow",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
      },
    });
  });

  $("#unfollow-topic").click(function(){
    var topicID = $("#topic").attr("topic-id");
    var that = $(this);

    $.ajax({
      url: "/topic/" + topicID + "/unfollow",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
      },
    });
  });

  /* navigation */

  $("#top-action").mouseenter(function(){

    /* block if divs are still in motion */
    var currentTop = parseInt($("#topic-title").css("top"));
    if (currentTop > 0) { return true; }

    var height = $("#top-action a").height();

    
    var timer = setTimeout(function(){
      $("#topic").animate( { top : height + "px" }, {duration: 500 });
      $("#topic-title").animate( { top : height + "px" }, {duration: 500, complete: fadeInTopActionInfo });
    }, 1000);
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
    $("#topic").animate( { top : "0" }, {duration: 500});
    $("#topic-title").animate( { top : "0" }, {duration: 500});

  });  

  function fadeOutTopActionInfo (){
    $("#top-action a").fadeOut(200);
  }

  $("#topic-title").swipeSnap( { target: "top", snapInfo: $("#snap-tooltip-top"), companions: [$("#topic")], callback: gotoTopicList });

  function gotoTopicList (){
    var boardID = $("#topic").attr("board-id");
    window.location = "/board/" + boardID;
  }

  /*
  $("#topic").swipeSnap( { target: "left", snapInfo: $("#snap-previous-topic"), companions: [$("#topic-title")], callback: gotoPreviousTopic });
  $("#topic").swipeSnap( { target: "right", snapInfo: $("#snap-next-topic"), companions: [$("#topic-title")], callback: gotoNextTopic });

  function gotoPreviousTopic(){
    var prevTopicID = $("#topic").attr("previous-topic-id");
    window.location = "/topic/" + prevTopicID;
  }

  function gotoNextTopic(){
    var nextTopicID = $("#topic").attr("next-topic-id");
    window.location = "/topic/" + nextTopicID;
  }*/

  $("#previous-topic").mouseenter(function(){

    var timer = setTimeout(function(){
      $("#previous-topic a").fadeIn(400).css("display", "inline-block");
    }, 1000);
    $(this).data("toolRevealDelay", timer);

  });  

  $("#previous-topic").mouseleave(function(){

    /* clear timer, that was triggered on mousenter */
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);

    $("#previous-topic a").fadeOut(400);

  });  

  $("#next-topic").mouseenter(function(){

    var timer = setTimeout(function(){
      $("#next-topic a").fadeIn(400).css("display", "inline-block");
    }, 1000);
    $(this).data("toolRevealDelay", timer);

  });  

  $("#next-topic").mouseleave(function(){

    /* clear timer, that was triggered on mousenter */
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);

    $("#next-topic a").fadeOut(400);

  });  

  /* bidirectional infinite scrolling */
  var slot = "/topic/" + $("#topic").attr("topic-id") + "/posts.json";
  var builder = "/topic/" + $("#topic").attr("topic-id") + "/certainposts";
  var scrolling = new InfiniteScrolling();
  scrolling.init(".post-item", slot, builder, [rebindToolTipEvents, rebindPostItemEvents, rebindPostEditingEvents, 
                                              rebindPostToolEvents, readVisiblePosts, redrawPostHighlighting], 3000, 20, 5);

  hash = window.location.hash;
  if (hash){
    postID = hash.substr(5);
    scrolling.jumpTo(postID);
  }else{
    scrolling.showFromStart();
  }

  $(window).on('hashchange',function(){ 
    postID = window.location.hash.substr(5);
    scrolling.jumpTo(postID);
  });

  $(document).scroll(function(e){
    readVisiblePosts();
    scrolling.scroll();
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
      url: "/filter/posts",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(){
        prependNewContributionFieldTo($("#topic"));
	    scrolling.showFromStart();
      },
    });
  });

  rebindPostItemEvents();
  rebindPostEditingEvents();

  $("#new-post-button").click(function(){
    showNewContributionField();
  });

  $("#close-topic").click(function(){
    var topicID = $("#topic").attr("topic-id");
    var that = $(this);

    $.ajax({
      url: "/topic/" + topicID + "/close",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
        $("#new-contribution").fadeOut(0);
        $("#topic").attr("topic-closed", "True");
        $("#this-topic-is-closed").fadeIn(0);
        $("#new-post-button").fadeOut(0);
      },
    });
  });

  $("#reopen-topic").click(function(){
    var topicID = $("#topic").attr("topic-id");
    var that = $(this);

    $.ajax({
      url: "/topic/" + topicID + "/reopen",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
        $("#topic").attr("topic-closed", "False");
        $("#new-post-button").fadeIn(0);
        $("#this-topic-is-closed").fadeOut(0);
      },
    });
  });

});

function showNewContributionField (){
  $("#new-contribution").slideDown(400);
  $("#new-post-button").slideUp(400);
  $("#new-post").focus();
}

function highlightPosts (jsonResponse){
  var postList = jsonResponse.posts.join(" ");
  console.log(postList);
  $("#topic").attr("highlighted-posts", postList);
  $("#topic").attr("highlighting-active", "True");
  redrawPostHighlighting();
}

function redrawPostHighlighting (){

  var active = $("#topic").attr("highlighting-active");

  if (active === "True"){

      var highlighted = $("#topic").attr("highlighted-posts").split(" ");
      $(".post-item").each(function(){
        var currentPostID = $(this).attr("post-id");
        if (highlighted.indexOf(currentPostID) === -1){
          $(this).removeClass("post-item-highlighted");
          $(this).addClass("post-item-downlighted");
        }else{
          $(this).removeClass("post-item-downlighted");
          $(this).addClass("post-item-highlighted");
        }
      });

      rebindPostItemEvents();
      rebindPostEditingEvents();

  }else{

      $(".post-item").each(function(){
          $(this).removeClass("post-item-downlighted");
          $(this).removeClass("post-item-highlighted");
      });

  }

}
