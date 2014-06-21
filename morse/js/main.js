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

/* enum */
KEY_DOWN = 40;
KEY_UP = 38;
KEY_RETURN = 13;

$(document).on("ready", function () {

  /* make multiline text inputs autogrow */
  $("#newtopictext").autogrow();
  $("#newposttext").autogrow();

  $.ajaxSetup({
    contentType: "application/json",
    traditional: true,
    type: "POST"
  });

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


  $(document).keydown(function (keyevent){

    /* This is what happens, when you ''just start typing''
     * on the board or topic view
    * */

    // ignore keystrokes, that are not letters, numbers or signs
    if (!(keyevent.which >= 65 && keyevent.which <= 90) &&
        !(keyevent.which >= 48 && keyevent.which <= 57)){
        return true;
    }

    if ($("#topic").length === 0 &&
        $("#board").length === 0){
        return true;
    }

    if($("#topic").attr("topic-closed") === "True"){
      return true;
    }

    if($("#topic").attr("may-post") === "False"){
      return true;
    }

    if($("#board").attr("may-post") === "False"){
      return true;
    }


    var activeID = $(document.activeElement).attr("id");
    var atNewPost = $("#newposttext").length > 0;
    var atNewTopic = $("#newtopictitle").length > 0;

    if (activeID !== "newtopictitle" &&
        activeID !== "newtopictext" &&
        activeID !== "newposttext" &&
        activeID !== "newhref"){

      $("#typinginfo").slideUp(0);
      $("#inputwrapper").slideDown(400);

      if (atNewPost){
        $("#newposttext").focus();
      }else if (atNewTopic){
        $("#newtopictitle").focus();
      }

    }else{
      return true;
    }

  });

  /* This is a workaround for a bug, that adds a another blockquote,
     if the user is inside a blockquote and presses enter */
  $("#newtopictext").on("keypress", blockquoteWorkaround);
  $("#newposttext").on("keypress", blockquoteWorkaround);


  function blockquoteWorkaround (keyevent) {

    var range = window.getSelection().getRangeAt();
    var element = range.commonAncestorContainer;

    element = (element.nodeType===1) ? element : element.parentNode; 

    if(element.nodeName === "BLOCKQUOTE" && keyevent.keyCode === KEY_RETURN && !keyevent.shiftKey) {
      keyevent.preventDefault();
      document.execCommand("InsertParagraph");
      document.execCommand("Outdent");    
    }

  }

  /* board info banners (TODO: replace with something good) */
  $(".boarditem").on("mouseenter", function (){
  });

  $(".boarditem").on("mouseleave", function (){
  });


  /* user navbar */
  $("#useravatar").click(function (){
    $("#usernav").slideToggle();
  });

  $("#guestavatar").click(function (){
    $("#guestnav").slideToggle();
  });

  /* goback tooltip */
  $("#goback").mouseenter(function(){
    $("#gobacktooltip").spellFadeIn(800,10);
  });

  $("#goback").mouseleave(function(){
    $("#gobacktooltip").spellFadeOut(800,100);
  });

});

