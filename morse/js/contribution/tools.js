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

  $(".format-tool[format-type=\"simple-wrap\"]").off("mousedown");
  $(".format-tool[format-type=\"simple-wrap\"]").on("mousedown", function (){
    var toolFooter = $(this).parents(".tool-footer");
    var contentElement = toolFooter.siblings("article");
    var tag = $(this).attr("tag");
    formatSelectedTextBy(contentElement, tag);
  });

  $(".format-tool[format-type=\"attr-input\"]").off("mousedown");
  $(".format-tool[format-type=\"attr-input\"]").on("mousedown", function (){
    var active = $(document.activeElement);
    if (active.is("article[contenteditable=\"True\"]")){

        var wrap = document.createElement("span");
        var selection = getSelection().getRangeAt(0);
        selection.surroundContents(wrap);
        $(wrap).addClass("pseudo-selected");

        active.removeAttr("contenteditable");
    }
  });

  $(".format-tool[format-type=\"attr-input\"]").off("mouseup");
  $(".format-tool[format-type=\"attr-input\"]").on("mouseup", function (){
    var toolFooter = $(this).parents(".tool-footer");
    var attrInput = toolFooter.children(".attr-input");
    attrInput.slideDown(400);
    attrInput.val("http://");
    attrInput.focus();
    var len = attrInput.val().length;
    attrInput[0].setSelectionRange(len, len);
    attrInput.attr("tag", $(this).attr("tag"));
    attrInput.attr("attr", $(this).attr("attr"));
    attrInput.attr("empty-selection-default", $(this).attr("empty-selection-default"));
  });
  
  $(".attr-input").off("keypress");
  $(".attr-input").on("keypress", function (keyevent){
    if(keyevent.which === KEY_RETURN){ 

      $(this).slideUp(400);
      
      var article = $(this).parents(".tool-footer").siblings("article");
      article.attr("contenteditable", "true");
      article.focus();

      var selectedElement = article.find(".pseudo-selected");
      var selectedContent = selectedElement.html()
      var tag = $(this).attr("tag");
      var attrName = $(this).attr("attr");
      var attrValue = $(this).val();
      
      if (selectedContent === ""){
        switch ($(this).attr("empty-selection-default")){
          case "inherit-from-attr":
            selectedContent = attrValue;
            break;
        }
      }
    

      var newElement = $("<" + tag + ">");
      newElement.attr(attrName, attrValue);
      newElement.html(selectedContent);

      selectedElement.replaceWith(newElement);
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
