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

  $("button.closethread").click(function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/closethread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.closedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.addClass("topicclosed");
        item.find(".closethread").fadeOut(0);
        item.find(".openthread").fadeIn(200);
      },
    });
  });

  $("button.openthread").click(function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/openthread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.openedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.removeClass("topicclosed");
        item.find(".openthread").fadeOut(0);
        item.find(".closethread").fadeIn(200);
      },
    });
  });

  /* follow switch */
  $("#followswitch").click(function () {

    var jsonTopicId = JSON.stringify($("#topic").attr("topic-id"));
    var notFollowed = $(this).hasClass("follow");
    if (notFollowed) {
      unfollow();
    }else{
      follow();
    }
    /*$.ajax({
      url: notFollowed ? "/follow" : "/unfollow",
      data: jsonTopicId,
      error: handleAjaxErrorBy( alertGlobal ),
      success: notFollowed ? unfollow : follow,
    });*/

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

  $("#order-dropdown").click(function(){
    if ($(this).hasClass("closed-dropdown")){
      $(this).removeClass("closed-dropdown");
      $(this).addClass("open-dropdown");
      $("#active-order").fadeOut(0);
      $("#order-menu").slideDown(400);
    }else{
      $(this).removeClass("open-dropdown");
      $(this).addClass("closed-dropdown");
      $("#active-order").fadeIn(200);
      $("#order-menu").slideUp(400);
    }
  });

  $(".order-option").click(function(){
    if ($(this).hasClass("order-option-selected")){
      var switched = $(this).attr("switched");
      var html = $(this).html();
      console.log(switched);
      $(this).attr("switched", html );
      $(this).html( switched );
    }
    $(".order-option").removeClass("order-option-selected");
    $(this).addClass("order-option-selected");
    $("#active-order").html( $(this).html() );
  });

  $("#new-topic-button").click(function(){
      $("#new-topic-button").slideUp(0);
      $("#inputwrapper").slideDown(400);
      $("#newtopictitle").focus();
  });

});
