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
        success: function () { posts.removeClass("fresh", 5000); },
      });
    }

  }

  /* follow switch */
  $("#followswitch").click(function () {

    jsonTopicId = JSON.stringify($("#topic").attr("topic-id"));
    notFollowed = $(this).hasClass("follow");
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

  CONTAINER_LIMIT = 10;
  MAX_BLOCKS = 3;

  $(document).scroll(function(e){

    /* don't scroll, if posts are loading */
    container = $("#postcontainer");
    if (container.attr("reloading") === "true"){
      e.preventDefault();
    }

    /* check if postloader bottom is visible */
    if ($("#postloader-bottom").visible()){
      var last = container.children(".postblock").last();
      newOffset = parseInt(last.attr("offset")) + CONTAINER_LIMIT;
      fetchPosts(newOffset, "bottom", removeSemaphore);
      if (!$("#postloader-bottom").children("#info-rockbottom").is(":visible")){
        $("#postloader-bottom").children("#info-newposts").fadeIn(400);
      }
    };

    /* check if postloader top is visible */
    if ($("#postloader-top").visible()){
      var first = container.children(".postblock").first();
      newOffset = parseInt(first.attr("offset")) - CONTAINER_LIMIT;
      if (newOffset >= 0){
        fetchPosts(newOffset, "top", removeSemaphore);
        $("#postloader-top").children("#info-oldposts").fadeIn(400);
      }else{
        $("#postloader-top").children("#info-oldposts").fadeOut(0);
      }
    };
  });

 
  $("#info-init").fadeIn(400); 
  fetchPosts(0, "bottom", removeSpinner);

  function removeSpinner (){
    $("#postcontainer").removeClass("contentspinner");
    $("#info-init").fadeOut(0);
    removeSemaphore();
  }

  function fetchPosts (offset, target, callback){
    console.log("fetch");
    container = $("#postcontainer");

    /* only trigger ajax, if not loading process is active */
    if (container.attr("reloading") === "false"){

      /* set semaphore */
      container.attr("reloading", "true");

      /* fetch posts */
      topicID = $("#topic").attr("topic-id");
      $.ajax({
        url: "/posts?topicID=" + topicID + "&offset=" + offset + "&limit=" + CONTAINER_LIMIT,
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
            $(block).prependTo(container);
            if ($(".postblock").length > MAX_BLOCKS){
              var firstBlock = $(".postblock").first();
              var ghostHeight = firstBlock.height();
              var newScrollPos = $(window).scrollTop() + ghostHeight;
              $(".postblock").last().remove();
              if ($("#postloader-bottom").children("#info-rockbottom").is(":visible")){
                $("#postloader-bottom").children().fadeOut(0);
                $("#postloader-bottom").children("#info-newposts").fadeIn(400);
              }
              $(window).scrollTop(newScrollPos);
            }
          }else{
            $(block).appendTo(container);
            if ($(".postblock").length > MAX_BLOCKS){
              var firstBlock = $(".postblock").first();
              var ghostHeight = firstBlock.height();
              var newScrollPos = $(window).scrollTop() - ghostHeight;
              firstBlock.remove();
              $(window).scrollTop(newScrollPos);
            }
          }

        },
        complete: callback
      });

    }

  }

  function removeSemaphore (){
    $("#postcontainer").attr("reloading", "false");
  }

});
