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

function rebindPostItemEvents (){
  
  $(".post-item").off("mouseenter");
  $(".post-item").on("mouseenter", function(){
    $(this).addClass("post-item-selected");
    var postTools = $(this).find(".post-tools");
    var timer = setTimeout(function(){
      postTools.fadeIn(400);
    }, 1000);
    $(this).data("toolRevealDelay", timer);
  });

  $(".post-item").off("mouseleave");
  $(".post-item").on("mouseleave", function(){
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);
    var postTools = $(this).find(".post-tools");
    if (postTools.is(":visible")){
      postTools.fadeOut(400);
    }
    $(this).removeClass("post-item-selected");
  });

  $(".post-item").off("mouseleave");
  $(".post-item").on("mouseleave", function(){
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);
    var postTools = $(this).find(".post-tools");
    if (postTools.is(":visible")){
      postTools.fadeOut(400);
    }
    $(this).removeClass("post-item-selected");
  });

  /* mobile support */
  $(".post-item").off("tapone");
  $(".post-item").on("tapone", function(){
    $(".post-item").removeClass("post-item-selected");
    $(this).addClass("post-item-selected");
    $(".post-tools").fadeOut(200);
    var postTools = $(this).find(".post-tools");
    postTools.fadeIn(200);
  });

  $(".post").off("mouseup");
  $(".post").on("mouseup", function(){
      var postID = $(this).parents(".post-item").attr("post-id");
      var otherPosts = $(".post-item:not([post-id=" + postID + "])")
      otherPosts.find(".post-action-quote").fadeOut(0);

      var selection = getSelection().getRangeAt(0);
      var postTools = $(this).parents(".post-item").find(".post-tools");
      var quoteAction = postTools.find(".post-action-quote");
      /* FIXME: if i click on the selection itself, it gets
      visually unselected, but the endOffset and startOffset
      remain the same */
      var selectionEmpty = selection.endOffset - selection.startOffset === 0;
      if (selectionEmpty) {
        quoteAction.fadeOut(400);
      }else{
        quoteAction.fadeIn(400);
      }
  });

  $(document).off("mouseup");
  $(document).on("mouseup",function (){
    var selection = getSelection().getRangeAt(0);
    console.log(selection);
    /* check, in which element text was selected */
    var container = $(selection.commonAncestorContainer);
    /* there is a small problem concerning single-line
    vs multi-line selections. on a multi-line selection the
    commonAncestorContainer is the .post element, while on
    a single-line selection it is text and the .post element
    is its parent element. we catch both cases in here */
    var parent = container.parents(".post");
    var selectionNotInPostText = parent.length === 0 && !container.hasClass("post");
    var selectionEmpty = selection.endOffset - selection.startOffset === 0;
    if (selectionEmpty || selectionNotInPostText) {
      $(".post-action-quote").fadeOut(400);
    }
    return true;
  });

  $(".post-action-reply").off("click");
  $(".post-action-reply").on("click", function() {
    var postItem = $(this).parents(".post-item");
    putNewContributionFieldAfter(postItem);
    showNewContributionField();
    createPostReference($("#new-contribution"), postItem.attr("post-id"));
  });

  function resetAllEditDialogs (){
    $(".post").attr("contenteditable", "False");
    $(".post[original-content]").each(function(){
      var originalContent = $(this).attr("original-content")
      $(this).html(originalContent);
    });
    $(".post-item .tool-footer").slideUp(200);
    $("#editable-topic-title").slideUp(200);
  }

  $(".post-action-edit").off("click");
  $(".post-action-edit").on("click", function() {

    resetAllEditDialogs();

    var postItem = $(this).parents(".post-item");
    var post = postItem.find(".post")

    /* save original content (in case user changes
    his mind) */
    var content = post.html()
    post.attr("original-content", content);

    /* show edit dialog */
    post.attr("contenteditable", "True");
    postItem.find(".tool-footer").slideDown(400);
    if (postItem.attr("first-post") === "True"){
      $("#editable-topic-title").slideDown(400);
      $("#editable-topic-title").focus();
    }else{
      post.focus();
    }

  });

  $(".submit-edited-post").off("click");
  $(".submit-edited-post").on("click", function(){

    var postItem = $(this).parents(".post-item");
    var postID = postItem.attr("post-id");
    var post = postItem.find(".post");

    /* change post content */
    if (postItem.attr("first-post") === "True"){
        var topicID = $("#topic").attr("topic-id");
        var title = $("#editable-topic-title").html()
        var data = new Object( { newTitle : title  } );
        var json = $.toJSON(data);

        $.ajax({
          url: "/topic/" + topicID + "/change-title",
          data: json,
          error: handleAjaxErrorBy( alertGlobal ),
          success: topicTitleChanged 
        });
    }

    /* change post content */
    var content = post.html()
    var data = new Object( { editedContent : content  } );
    var json = $.toJSON(data);

    $.ajax({
      url: "/post/" + postID + "/edit",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: postChanged 
    });

  });

  function topicTitleChanged(){
    var newTitle = $("#editable-topic-title").html()
    $("#topic-title").html(newTitle)
    $("#editable-topic-title").slideUp(200);
  }

  function postChanged () {
    $(".post-item .tool-footer").slideUp(200); 
    $(".post").attr("contenteditable", "False"); 
    $(".post").removeAttr("original-content"); 
  }

}
