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

  /* mark posts on screen as read */
  readVisiblePosts();

  $(document).scroll(function (){
    readVisiblePosts();
  });


  function readVisiblePosts (){

    /* 
       readVisible() looks for posts in the current viewport and
       marks them as read via ajax. this include removing the
       css fresh class
       */

    var postfooters = $(".postfooter").filter(function(){ 
      return $(this).visible(); 
    });

    /* collect ids of visible posts */
    var ids = Array();
    postfooters.each(function () {
      if ($(this).parent().hasClass("fresh")){
        ids.push($(this).html());
      }
    });

    var posts = postfooters.parent();
    var json = JSON.stringify(ids);

    /* only send, if posts were found */
    if (ids.length > 0){
      $.ajax({
        url: "/read",
        data: json,
        error: handleAjaxErrorBy( alertGlobal ),
        success: function () { posts.removeClass("fresh"); },
      });
    }

  }

  /* follow switch */
  $("#followswitch").click(function () {

    var jsonTopicId = JSON.stringify($("#topic").attr("topic-id"));
    var notFollowed = $(this).hasClass("follow");
    $.ajax({
      url: notFollowed ? "/follow" : "/unfollow",
      data: jsonTopicId,
      error: handleAjaxErrorBy( alertGlobal ),
      success: notFollowed ? unfollow : follow,
    });

  });

  function unfollow (){
    switchFollow();
    $("#followswitch").addClass("unfollow", 500);
    $("#followswitch").removeClass("follow", 500);
  }

  function follow (){
    switchFollow();
    $("#followswitch").addClass("follow", 500);
    $("#followswitch").removeClass("unfollow", 500);
  }

  function switchFollow (){
    var oldhtml = $("#followswitch").html(); 
    var newhtml = $("#followswitch").attr("switched");
    $("#followswitch").html(newhtml);
    $("#followswitch").attr("switched", oldhtml);
  }

  /* bidirectional infinite scrolling */

  MAX_BLOCKS = 3;
  CONTAINER_LIMIT = 5;

  $(document).scroll(function(e){

    /* don't scroll, if posts are loading */
    var container = $("#postcontainer");
    if (container.attr("reloading") === "true"){
      e.preventDefault();
    }
    checkBottomLoader();
    checkTopLoader();

  });

  function checkBottomLoader(){
    /* check if postloader bottom is visible */
    if ($("#postloader-bottom").visible()){
      console.log("checking bottom");
      var last = $("#postcontainer").children(".postblock").last();
      var newOffset = parseInt(last.attr("offset")) + CONTAINER_LIMIT;
      fetchPosts(newOffset, "bottom", removeSemaphore);
      if (!$("#postloader-bottom").children("#info-rockbottom").is(":visible")){
        $("#postloader-bottom").children("#info-newposts").fadeIn(400);
      }
    };
  }

  function checkTopLoader(){
    /* check if postloader top is visible */
    if ($("#postloader-top").visible()){
      console.log("checking top");
      var first = $("#postcontainer").children(".postblock").first();
      var newOffset = parseInt(first.attr("offset")) - CONTAINER_LIMIT;
      console.log(newOffset);
      if (newOffset >= 0){
        fetchPosts(newOffset, "top", removeSemaphore);
        $("#postloader-top").children("#info-oldposts").fadeIn(400);
      }else{
        $("#postloader-top").children("#info-oldposts").fadeOut(0);
      }
    };
  }

  function createInitSpinner(){
    $("#postloader-top").children().fadeOut(0);
    $("#info-init").fadeIn(400); 
    $("#postcontainer").addClass("contentspinner");
  } 

  function removeInitSpinner (){
    $("#postcontainer").removeClass("contentspinner");
    $("#info-init").fadeOut(0);
  }

  createInitSpinner();
  fetchPosts(0, "bottom", [removeInitSpinner, removeSemaphore, checkTopLoader, checkForUnreadPosts]); 

  function rebindPostJumpers (){
    console.log($(".post-jumper"));
    $(".post-jumper").off("click");
    $(".post-jumper").on("click", function(){
      console.log("clicked post jumper");
      var postID = $(this).attr("jump-to");
      $("#postcontainer").html("");
      createInitSpinner();
      jumpToPost(postID, [removeInitSpinner, removeSemaphore, checkTopLoader, checkForUnreadPosts]); 
    });
  }

  function checkForUnreadPosts (){
      var topicID = $("#topic").attr("topic-id");
      $.ajax({
        url: "/topic/" + topicID + "/unread.json",
        type: "GET", 
        error: handleAjaxErrorBy(alertGlobal),
        success: function (unread) { 
	  if (unread.unreadCount > 0){
	    buildJumpToUnreadButton(unread.unreadCount, unread.firstUnreadID);
	  }else{
	    buildJumpToLastButton();
	  }
        },
      });
  }

  function buildJumpToLastButton() { };

  function buildJumpToUnreadButton (unreadCount, firstUnreadID){
      $.ajax({
        url: "/buttonbuilder/unread?unreadCount=" + unreadCount + "&firstUnreadID=" + firstUnreadID,
        type: "GET", 
        error: handleAjaxErrorBy(alertGlobal),
        success: function (html) {
	  if ($("#jump-to-unread").length > 0){
            $("#jump-to-unread").replaceWith(html);
	  }else{
	    $("#postloader-top").prepend(html); 
	  }
	  $("#postloader-top").children().fadeOut(0);
	  $("#jump-to-unread").fadeIn()
	  rebindPostJumpers();
        },
      });
  }

  function jumpToPost (postID, callback){
    var topicID = $("#topic").attr("topic-id");
    $.ajax({
      url: "/topic/" + topicID + "/jump?postID=" + postID,
      type: "GET", 
      error: handleAjaxErrorBy(alertGlobal),
      success: function (block) {
	appendPostBlock(block);
	$(window).scrollTop( $("[jumphere]").offset().top );
      },
      complete: callback
    });
  }

  function fetchPosts (offset, target, callback){
    var container = $("#postcontainer");

    /* only trigger ajax, if no loading process is active */
    if (container.attr("reloading") === "false"){

      /* set semaphore */
      container.attr("reloading", "true");

      /* fetch posts */
      var topicID = $("#topic").attr("topic-id");
      $.ajax({
        url: "/topic/" + topicID + "/postrange?&offset=" + offset,
        type: "GET", 
        error: function(response) {

          /* check if no more posts were available ... */
          if(response.responseText === "nomoreposts"){
            if (!$("#postloader-bottom").children("#info-rockbottom").is(":visible")){
              $("#postloader-bottom").children().fadeOut(0);
              $("#postloader-bottom").children("#info-rockbottom").fadeIn(400);
            }
          /* .. or something went wrong */
          }else{
            alertGlobal("ajax");
          }

        },
        success: function (block) { 

          if (target === "top"){
            prependPostBlock(block);
          }else{
     	    appendPostBlock(block);
          }

        },
        complete: callback
      });

    }

  }

  function prependPostBlock (block){
    $(block).prependTo($("#postcontainer"));
    var firstBlock = $(".postblock").first();
    var ghostHeight = firstBlock.height();
    var newScrollPos = $(window).scrollTop() + ghostHeight;
    $(window).scrollTop(newScrollPos);
    if ($(".postblock").length > MAX_BLOCKS){
      $(".postblock").last().remove();
      if ($("#postloader-bottom").children("#info-rockbottom").is(":visible")){
	$("#postloader-bottom").children().fadeOut(0);
	$("#postloader-bottom").children("#info-newposts").fadeIn(400);
      }
    }
  }

  function appendPostBlock (block){
    $(block).appendTo($("#postcontainer"));
    if ($(".postblock").length > MAX_BLOCKS){
      var firstBlock = $(".postblock").first();
      var ghostHeight = firstBlock.height();
      var newScrollPos = $(window).scrollTop() - ghostHeight;
      firstBlock.remove();
      $(window).scrollTop(newScrollPos);
    }
  }

  function removeSemaphore (){
    $("#postcontainer").attr("reloading", "false");
  }

});
