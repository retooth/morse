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


  /* bidirectional infinite scrolling */
  var slot = "/topic/" + $("#topic").attr("topic-id") + "/posts.json";
  var builder = "/topic/" + $("#topic").attr("topic-id") + "/certainposts";
  var scrolling = new InfiniteScrolling();
  scrolling.init(".postitem", slot, builder, [rebindToolTipEvents, rebindPostItemEvents, readVisiblePosts], 3000, 20, 5);

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
	scrolling.showFromStart();
      },
    });
  });

  rebindPostItemEvents();

  function rebindPostItemEvents (){
    $(".postitem").off("dblclick");
    $(".postitem").on("dblclick", function(){
      if ($("#topic").attr("topic-closed") === "True"){
        return true;
      }
      var inputWrapper = $("#inputwrapper");
      inputWrapper.remove();
      inputWrapper.insertAfter($(this));
      rebindPostButtonEvents();
      rebindPostToolEvents();
      inputWrapper.slideDown(400);
      $("#new-post-button").slideUp(0);
      $("#newposttext").focus();
    });
  }

  $("#new-post-button").click(function(){
      $("#new-post-button").slideUp(0);
      $("#inputwrapper").slideDown(400);
      $("#newposttext").focus();
  });

  $("#close-topic").click(function(){
    var topicID = $("#topic").attr("topic-id");
    var that = $(this);

    $.ajax({
      url: "/topic/" + topicID + "/close",
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        switchButton(that);
        $("#inputwrapper").fadeOut(0);
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
