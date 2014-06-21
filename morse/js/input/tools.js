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

function formatSelectedTextBy (tag){
  var activeID = $(document.activeElement).attr("id");
  if (activeID === "newtopictext" ||
      activeID === "newposttext")
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

$(document).on("ready", function () {


  $("#makebold").mousedown(function (){
    formatSelectedTextBy("strong");
  });


  $("#makeitalic").mousedown(function (){
    formatSelectedTextBy("em");
  });


  $("#makequote").mousedown(function (){
    formatSelectedTextBy("blockquote");
  });


  $("#makelink").on("mousedown", function (){
    var activeID = $(document.activeElement).attr("id");
    if (activeID === "newtopictext" ||
        activeID === "newposttext")
      {
        var wrap = document.createElement("span");
        var selection = getSelection().getRangeAt(0);
        wrap.setAttribute("id", "dummylink");
        selection.surroundContents(wrap);

        $("#newhref").val("http://");

        $("#newhrefwrapper").slideDown(400);
        $("#closenewhref").fadeIn(200);
        $("#makelink").addClass("openrightborder");

        $("#newtopictitle").removeAttr("contenteditable");
        $("#newtopictext").removeAttr("contenteditable");
        $("#newposttext").removeAttr("contenteditable");
        $("#inputwrapper").addClass("disabledbox");
      }
  });


  $("#makelink").on("mouseup", function (){
    $("#newhref").focus();
  });


  $("#newhref").keypress(function (keyevent){
    if(keyevent.which === KEY_RETURN){ 
      $("#newhrefwrapper").slideUp(200);
      $("#closenewhref").fadeOut(200);
      $("#makelink").removeClass("openrightborder");

      $("#newtopictitle").attr("contenteditable", "true");
      $("#newtopictext").attr("contenteditable", "true");
      $("#newposttext").attr("contenteditable", "true");
      $("#inputwrapper").removeClass("disabledbox");

      $("#newtopictext").focus();
      $("#newposttext").focus();

      var link = $("#dummylink").html();
      var href = $("#newhref").val();
      link = (link === "" ? href : link);
      $("#dummylink").replaceWith("<a href=\"" + href +"\">" + link + "</a>");
    }
  });

  $("#closenewhref").click(function(){
    $("#newhrefwrapper").slideUp(200);
    $(this).fadeOut(200);
    $("#makelink").removeClass("openrightborder");

    $("#newtopictitle").attr("contenteditable", "true");
    $("#newtopictext").attr("contenteditable", "true");
    $("#newposttext").attr("contenteditable", "true");
    $("#inputwrapper").removeClass("disabledbox");

    $("#newtopictext").focus();
    $("#newposttext").focus();
    // FIXME: there is a bug, that doesn't do these last two
    // lines (at least the outline of dummylink is visible)
    // after that link creating doesn't work any more, probably
    // because more than one #dummylink exists. this has something
    // to do with multi-line-selecting, but i couldn't reproduce it
    // probably.
    var old = $("#dummylink").html();
    $("#dummylink").replaceWith(old);
  });

});
