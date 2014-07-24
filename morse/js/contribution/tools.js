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
 rebindPostToolEvents();
});

function formatSelectedTextBy (contentElement, tag){
  var active = $(document.activeElement);
  if (active.is(contentElement))
    {
      var wrap = document.createElement(tag);
      var selection = getSelection().getRangeAt(0);
      if (selection === "") {
        alertInput("pleaseselect");
      }else{
        selection.surroundContents(wrap);
      }
    }
}

function rebindPostToolEvents (){

  $(".format-bold").off("mousedown");
  $(".format-bold").on("mousedown", function (){
    var toolFooter = $(this).parents(".tool-footer");
    var contentElement = toolFooter.siblings("article");
    formatSelectedTextBy(contentElement, "strong");
  });


  $(".format-italic").off("mousedown");
  $(".format-italic").on("mousedown", function (){
    var toolFooter = $(this).parents(".tool-footer");
    var contentElement = toolFooter.siblings("article");
    formatSelectedTextBy(contentElement, "em");
  });


  $(".format-quote").off("mousedown");
  $(".format-quote").on("mousedown", function (){
    var toolFooter = $(this).parents(".tool-footer");
    var contentElement = toolFooter.siblings("article");
    formatSelectedTextBy(contentElement, "blockquote");
  });


  $(".format-link").off("mousedown");
  $(".format-link").on("mousedown", function (){
    var active = $(document.activeElement);
    if (active.is("article[contenteditable=\"True\"]")){
        var wrap = document.createElement("span");
        var selection = getSelection().getRangeAt(0);
        wrap.setAttribute("id", "dummylink");
        selection.surroundContents(wrap);

        $("#newhref").val("http://");

        $("#newhrefwrapper").slideDown(400);
        $("#closenewhref").fadeIn(200);
        $("#makelink").addClass("openrightborder");
        $("#new-post").removeAttr("contenteditable");
        $("#new-contribution").addClass("disabledbox");
    }
  });


  $(".format-link").off("mouseup");
  $(".format-link").on("mouseup", function (){
    $("#newhref").focus();
  });

  
  $("#newhref").off("keypress");
  $("#newhref").on("keypress", function (keyevent){
    if(keyevent.which === KEY_RETURN){ 
      $("#newhrefwrapper").slideUp(200);
      $("#closenewhref").fadeOut(200);
      $("#makelink").removeClass("openrightborder");
      
      $(this).parents("#new-contribution").find("article");
      $("#new-post").attr("contenteditable", "true");
      $("#new-contribution").removeClass("disabledbox");

      $("#new-post").focus();

      var link = $("#dummylink").html();
      var href = $("#newhref").val();
      link = (link === "" ? href : link);
      $("#dummylink").replaceWith("<a href=\"" + href +"\">" + link + "</a>");
    }
  });

  $("#closenewhref").off("click");
  $("#closenewhref").on("click", function(){
    $("#newhrefwrapper").slideUp(200);
    $(this).fadeOut(200);
    $("#makelink").removeClass("openrightborder");

    $("#new-post").attr("contenteditable", "true");
    $("#new-contribution").removeClass("disabledbox");

    $("#new-post").focus();
    // FIXME: there is a bug, that doesn't do these last two
    // lines (at least the outline of dummylink is visible)
    // after that link creating doesn't work any more, probably
    // because more than one #dummylink exists. this has something
    // to do with multi-line-selecting, but i couldn't reproduce it
    // probably.
    var old = $("#dummylink").html();
    $("#dummylink").replaceWith(old);
  });

}
