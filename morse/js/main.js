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

  reinitCheckboxes();
  rebindCheckboxEvents();

  $.ajaxSetup({
    contentType: "application/json",
    traditional: true,
    type: "POST"
  });

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


    var active = $(document.activeElement);

    if (!active.is("input") && !active.is("[contenteditable]")) {
      showInputField();
    }else{
      return true;
    }

  });

  /* This is a workaround for a bug, that adds a another blockquote,
     if the user is inside a blockquote and presses enter */
  $("#new-post").on("keypress", blockquoteWorkaround);

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
  $("#show-user-menu").click(function (){
    $("#user-menu").slideToggle(600);
    $("#menu-active-background").slideToggle(0);
  });

  $("#show-moderator-menu").click(function (){
    $("#moderator-menu").slideToggle(600);
    $("#menu-active-background").slideToggle(0);
  });

  $("#show-admin-menu").click(function (){
    $("#admin-menu").slideToggle(600);
    $("#menu-active-background").slideToggle(0);
  });

  $("#menu-active-background").click(function (){
    $("#user-menu").slideUp(600);
    $("#moderator-menu").slideUp(600);
    $("#admin-menu").slideUp(600);
    $("#menu-active-background").slideUp(0);
  });

  rebindDropDownMenuEvents();

});

function rebindDropDownMenuEvents(){

  $(".closed-dropdown").off("click");
  $(".closed-dropdown").on("click", function(){
    var menuID = $(this).attr("dropdown-menu-id");
    var that = $(this);
    $("#" + menuID).slideDown(500, function(){
      that.removeClass("closed-dropdown");
      that.addClass("open-dropdown");
      rebindDropDownMenuEvents();
    });
  });

  $(".open-dropdown").off("click");
  $(".open-dropdown").on("click", function(){
    var menuID = $(this).attr("dropdown-menu-id");
    var that = $(this);
    $("#" + menuID).slideUp(500, function(){
      that.removeClass("open-dropdown");
      that.addClass("closed-dropdown");
      rebindDropDownMenuEvents();
    });
  });
}
function switchButton (button){
  button.fadeOut(0);
  var switchID = button.attr("switched-button");
  $("#" + switchID).fadeIn(0);
}

function reinitCheckboxes (){
  $("input[type=\"checkbox\"]").each(function(){
    if ($(this).is(":checked")){
      $(this).parents(".option").addClass("option-selected");
    }else{
      $(this).parents(".option").removeClass("option-selected");
    }
  });
}

function rebindCheckboxEvents (){
  $("input[type=\"checkbox\"]").off("click");
  $("input[type=\"checkbox\"]").on("click", function(){
    if ($(this).is(":checked")){
      $(this).parents(".option").addClass("option-selected");
    }else{
      $(this).parents(".option").removeClass("option-selected");
    }
  });
}
