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

/* make multiline text inputs autogrow */
$("#newtopictext").autogrow();
$("#newposttext").autogrow();

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

  var postfooters = $(".postfooter").filter( 
                      function(index){ 
                        return $(this).visible() 
                      });


  /* collect ids of visible posts */
  var ids = Array();
  $.each(postfooters, function (index, item) {
    if ($(item).parent().hasClass("fresh")){
      ids.push($(item).html());
    }
  });

  var posts = postfooters.parent();
  var ids_json = JSON.stringify(ids);
  
  /* only send, if posts were found */
  if (ids.length > 0){
    $.ajax({
      url: "/read",
      contentType: "application/json",
      type: "POST",
      data: ids_json,
      error: function () { alertGlobal("ajax"); },
      success: function (data) { posts.removeClass("fresh", 5000); },
      dataType: "json",
      traditional: true
    });
  }

}

$(document).keydown(function (keyevent){
 // TODO: this is a bit of a mess, clean up please
 $("#typinginfo").slideUp(0);
 $("#inputwrapper").slideDown(400);
 if ($(document.activeElement).attr("id") == "newtopictitle" && keyevent.which == 13){
  $("#newtopictext").focus();
  keyevent.preventDefault();
  if ($("#newtopictitle").val() == ""){
    $("#newtopictitle").val("No Topic");
  }
 }else if ($(document.activeElement).attr("id") != "newtopictext" &&
           $(document.activeElement).attr("id") != "newhref"){
  /*if (keyevent.which == 13){
    keyevent.preventDefault();
  }*/
  if ($("#newtopictitle").length == 0){
    $("#newposttext").focus();
  }else{
    $("#newtopictitle").focus();
  }
 }
});

$("#docreate").on("click", function(){
  /* TODO: check blankpost
     alertInput("blankpost");
  */
  var title = $("#newtopictitle").html();
  var text = $("#newtopictext").html();
  var board_id = $("#boardid").html();

  $.ajax({
    url: board_id + "/starttopic",
    type: "POST",
    data: { title: title, text: text },
    error: function () { alertInput("ajax"); },
    success: processNewTopicResponse,
    dataType: "json",
    traditional: true
  });
});


$("#dopost").on("click", function(){
  /* TODO: check blankpost
     alertInput("blankpost");
  */
  var text = $("#newposttext").html();
  var topic_id = $("#topicid").html();

  $.ajax({
    url: topic_id + "/post",
    type: "POST",
    data: { text: text },
    error: function () { alertInput("ajax"); },
    success: processNewPostResponse,
    dataType: "json",
    traditional: true
  });
});

function processNewTopicResponse (response){
  if (response.success == false){
    alertInput("forbidden");
  }else{
    window.location.href = "/topic/" + response.topicId
  }
}

function processNewPostResponse (response){
  if (response.success == false){
    alertInput("forbidden");
  }else{
    window.location.reload();
    // FIXME: how to scroll down AFTER reload??
    // TODO: maybe do an ajax implementation
  }
}

/* This is a workaround for a bug, that adds a another blockquote,
if the user is inside a blockquote and presses enter */
$("#newtopictext").on("keypress", blockquoteWorkaround);
$("#newposttext").on("keypress", blockquoteWorkaround);

function blockquoteWorkaround (keyevent) {
  var range = window.getSelection().getRangeAt();
  var element = range.commonAncestorContainer;
  element = ((element.nodeType===1)?element:element.parentNode); 
  if(element.nodeName == "BLOCKQUOTE" && keyevent.keyCode == 13 && !keyevent.shiftKey) {
    keyevent.preventDefault();
    document.execCommand('InsertParagraph');
    document.execCommand('Outdent');    
  }
}

/* formatting toolbox */

$("#makebold").mousedown(function (e){
  if ($(document.activeElement).attr("id") == "newtopictext" ||
      $(document.activeElement).attr("id") == "newposttext")
  {
    var wrap = document.createElement("strong");
    var selection = getSelection().getRangeAt(0);
    if (selection == "") {
      alertInput("pleaseselect");
    }else{
      selection.surroundContents(wrap);
    }
  }
});

$("#makeitalic").mousedown(function (e){
  if ($(document.activeElement).attr("id") == "newtopictext" ||
      $(document.activeElement).attr("id") == "newposttext")
  {
    var wrap = document.createElement("em");
    var selection = getSelection().getRangeAt(0);
    if (selection == "") {
      alertInput("pleaseselect");
    }else{
      selection.surroundContents(wrap);
    }
  }
});

$("#makequote").mousedown(function (e){
  if ($(document.activeElement).attr("id") == "newtopictext" ||
      $(document.activeElement).attr("id") == "newposttext")
  {
    var wrap = document.createElement("blockquote");
    var selection = getSelection().getRangeAt(0);
    if (selection == "") {
      alertInput("pleaseselect");
    }else{
      selection.surroundContents(wrap);
    }
  }
});

$("#makelink").on("mousedown", function (e){
  if ($(document.activeElement).attr("id") == "newtopictext" ||
      $(document.activeElement).attr("id") == "newposttext")
  {
    var wrap = document.createElement("span");
    var selection = getSelection().getRangeAt(0);
    wrap.setAttribute("id", "dummylink");
    $("#newhref").val("http://");
    $("#newhrefwrapper").slideDown(400);
    selection.surroundContents(wrap);
  }
});

$("#makelink").on("mouseup", function (){
  $("#newhref").focus();
  $("#newtopictitle").removeAttr('contenteditable');
  $("#newtopictext").removeAttr('contenteditable');
  $("#newposttext").removeAttr('contenteditable');
  $("#inputwrapper").addClass("disabledbox");
});

$("#newhref").keypress(function (keyevent){
  if(keyevent.which == 13){
    $("#inputwrapper").removeClass("disabledbox");
    $("#newtopictitle").attr('contenteditable', "true");
    $("#newtopictext").attr('contenteditable', "true");
    $("#newposttext").attr('contenteditable', "true");
    $("#newtopictext").focus();
    $("#newposttext").focus();
    $("#newhrefwrapper").slideUp(200);
    var link = $("#dummylink").html();
    var href = $("#newhref").val();
    if (link == ""){
      link = href;
    }
    $("#dummylink").replaceWith("<a href=\"" + href +"\">" + link + "</a>");
  }
});

/* board info banners */
$(".boardentry").on("mouseenter", function (){
  $(this).children(".lastpost").slideDown(400);
  $(this).children(".lasttopics").slideDown(400);
});

$(".boardentry").on("mouseleave", function (){
  $(this).children(".lastpost").slideUp(200);
  $(this).children(".lasttopics").slideUp(200);
});

/* user navbar */
$("#useravatar").click(function (){
  $("#usernav").slideToggle();
});

$("#guestavatar").click(function (){
  $("#guestnav").slideToggle();
});

/* follow switch */
$("#followswitch").click(function () {
  jsonTopicId = JSON.stringify($("#topicid").html());
  console.log(jsonTopicId);
  if ($(this).hasClass("follow")){
    $.ajax({
      url: "/follow",
      contentType: "application/json",
      type: "POST",
      data: jsonTopicId,
      error: function () { alertGlobal("ajax"); },
      success: function (data) { unfollow(); },
      dataType: "json",
      traditional: true
    });
 }else{
    $.ajax({
      url: "/unfollow",
      contentType: "application/json",
      type: "POST",
      data: jsonTopicId,
      error: function () { alertGlobal("ajax"); },
      success: function (data) { follow(); },
      dataType: "json",
      traditional: true
    });
 }

});

function unfollow (){
  switchFollow()
  $("#followswitch").addClass("unfollow", 500);
  $("#followswitch").removeClass("follow", 500);
}

function follow (){
  switchFollow()
  $("#followswitch").addClass("follow", 500);
  $("#followswitch").removeClass("unfollow", 500);
}

function switchFollow (){
  var oldhtml = $("#followswitch").html(); 
  var newhtml = $("#followswitch").attr("switched");
  $("#followswitch").html(newhtml);
  $("#followswitch").attr("switched", oldhtml);
}

/* goback tooltip */
$("#goback").mouseenter(function(e){
  $("#gobacktooltip").spellFadeIn(800,10);
});

$("#goback").mouseleave(function(e){
  $("#gobacktooltip").spellFadeOut(800,100);
});

$("#closenewhref").click(function(e){
  $("#inputwrapper").removeClass("disabledbox");
  $("#newtopictitle").attr('contenteditable', "true");
  $("#newtopictext").attr('contenteditable', "true");
  $("#newposttext").attr('contenteditable', "true");
  $("#newtopictext").focus();
  $("#newposttext").focus();
  $("#newhrefwrapper").slideUp(200);
  var old = $("#dummylink").html();
  $("#dummylink").replaceWith(old);
});

//FIXME: delay until remove
$(".deletewebsite").on("click", function(e){
  $(this).parent().slideUp(200).remove();
});

/* settings */
$("#anotherwebsite").click(function(e){

  var website = $(".websitewrapper").first().clone();
  website.css("display", "none");
  website.children("input").val("");
  website.children("input").attr("placeholder", "...");
  website.insertBefore($("#anotherwebsitebr"));
  website.slideDown(200);
  website.children("button").fadeIn(1200);

  /* rebind it (since new .deletewebsite 
     elements were added) */
  $(".deletewebsite").off("click");
  //FIXME: see above
  $(".deletewebsite").on("click", function(e){
    $(this).parent().slideUp(200).remove();
  });

});

$("#updateinfo").click(function(e){

  var bio = $("#bio").val();
  var websites = Array()
  $.each($(".websitewrapper input"), function (index, item){
    websites.push($(item).val());
  });

  var info = new Object({ bio : bio, websites : websites});

  $(this).addClass("buttonspinner");

  $.ajax({
    url: "settings/updateinfo",
    type: "POST",
    contentType: "application/json",
    data: $.toJSON(info),
    error: function (e) {
        $("#updateinfo").removeClass("buttonspinner");
        alertInfoSettings("ajax"); 
    },
    success: function(data){ $("#updateinfo").removeClass("buttonspinner"); },
    dataType: "json",
    traditional: true
  });

});

$(".accountdetail").keypress(function(e){

  // see http://stackoverflow.com/questions/11627531
  $("#chromebugmask").slideDown(800);
  $("#updateaccount").fadeIn(400);

});

$("#updateaccount").click(function(e){


  $("div[id^=\"accountsettingsalert_\"]").fadeOut(0);
  
  $("#newpassword").removeClass("redoutline");
  $("#newpasswordagain").removeClass("redoutline");
  $("#oldpassword").removeClass("redoutline");

  $(this).addClass("buttonspinner");
  var newpasswd = $("#newpassword").val();
  var newpasswdrepeat = $("#newpasswordagain").val();
  if (newpasswd != newpasswdrepeat){
    alertAccountSettings("passwordsdontmatch");
    $("#newpassword").addClass("redoutline");
    $("#newpasswordagain").addClass("redoutline");
    $(this).removeClass("buttonspinner");
    return false;
  }

  var oldpasswd = $("#oldpassword").val();
  var newemail = $("#newemail").val();
  var account = { newemail : newemail, newpassword : newpasswd, oldpassword : oldpasswd };

  $.ajax({
    url: "settings/updateaccount",
    type: "POST",
    contentType: "application/json",
    data: $.toJSON(account),
    error: function (e) { 
      $("#updateaccount").removeClass("buttonspinner"); 
      alertAccountSettings("ajax"); 
    },
    success: function(data){ 

      $("#updateaccount").removeClass("buttonspinner"); 

      if (data.success == false){
        $("#oldpassword").addClass("redoutline");
        alertAccountSettings("wrongpassword");
        return false;
      }

    },
    dataType: "json",
    traditional: true
  });

});

/* administration */
$("#boardsettings").submit(function(e){
  // prevent blank board title
  if ($("#newboardtitle").val() != ""){
    return;
  }
  $("#newboardtitle").addClass("redoutline");
  $("#newboardtitle").focus();
  alertBoardSettings("blanktitle");
  e.preventDefault();
});


$(".grouplist").sortable({ 
  connectWith : ".grouplist",
  placeholder : 'ddplaceholder',
  create : allLiToHiddenInput,
  receive : allLiToHiddenInput
});

function allLiToHiddenInput (){
  $("#lihiddeninput").html("");
  liToHiddenInput( $("#modelistignorant li"), "ignorant");
  liToHiddenInput( $("#modelistknowonly li"), "knowonly");
  liToHiddenInput( $("#modelistreadonly li"), "readonly");
  liToHiddenInput( $("#modelistposter li"), "poster");
}

function liToHiddenInput (lilist, prefix){
  $.each ( lilist, function (index, item){
    var group_id = $(item).attr("group-id");
    var hiddeninput = $("<input/>");
    hiddeninput.attr("type", "hidden");
    hiddeninput.attr("name", prefix + index);
    hiddeninput.val(group_id);
    hiddeninput.appendTo("#lihiddeninput");
  });
}

$("#showmodelist").click(function(e){
  $("#showmodelist").fadeOut(0);
  $("#hidemodelist").fadeIn(0);
  $("#modelist").slideDown(800);
});

$("#hidemodelist").click(function(e){
  $("#hidemodelist").fadeOut(0);
  $("#showmodelist").fadeIn(0);
  $("#modelist").slideUp(800);
});

$("#groupsidelist li").click(function(e){
  $(".groupmenu").fadeOut(0);
  var group_id = $(this).attr("group-id");
  $(".groupmenu[group-id=" + group_id + "]").fadeIn(400);
});

$(".userfirstletter").click(function(e){
  var letter = $(this).attr("letter")
  $(".usersidelist ul").fadeOut(0);
  $(".usersidelist ul[letter=" + letter + "]").fadeIn(400);
});

$(".groupuserlist").sortable();

$(".usersidelist li").draggable({ helper: "clone", connectToSortable: ".groupuserlist"});

$(".groupuserlist").on( "sortstop", function (e, ui){

  var new_user = ui.item
  new_user.addClass("user");
  var id = new_user.attr("user-id");

  // This blob finds <li>s with the same user-id attr (which indicates
  // that this user is already in this group). It is >1 and not >0,
  // because at sortstop the new element is already added to <ul>

  if ( $(this).children("li[user-id=\"" + id + "\"]").length > 1 ){
    alertGlobal("alreadyingroup");
    new_user.remove();
  }else{
    $(this).attr("tainted", true);

    // we can be sure, that there always be at least one
    // .deletefromgroup. By cloning we can change the close
    // button in the template without the need to change it here
    var closebutton = $(".deletefromgroup").first().clone()
    closebutton.appendTo(new_user);
    $(".deletefromgroup").off("click");
    $(".deletefromgroup").on("click", deleteFromGroup);
  }

});

$(".deletefromgroup").on("click", deleteFromGroup);

function deleteFromGroup(e){
  $(this).parents(".groupuserlist").attr("tainted", true);
  $(this).parents("li").remove();
}  

$("#updategroups").click(function(e){

  //FIXME: buttonspinner shows endless when no change happened
  $(this).addClass("buttonspinner");
  $.each($(".groupuserlist[tainted=\"true\"]"), function (index, grouplist){
    var users = $(grouplist).children("li");
    var user_ids = Array();
    $.each (users, function (index, user){
        var id = $(user).attr("user-id");
        user_ids.push(id);
    });
    var group_id = $(grouplist).attr("group-id");
    var ids_json = JSON.stringify(user_ids);
    console.log(group_id);
    console.log(ids_json);
    $.ajax({
      url: "updategroup/" + group_id,
      type: "POST",
      contentType: "application/json",
      data: ids_json,
      error: function (e) {
          $("#updategroups").removeClass("buttonspinner");
          alertGlobal("ajax"); 
      },
      success: function(data){ $("#updategroups").removeClass("buttonspinner"); },
      dataType: "json",
      traditional: true
    });
  });


});

});

/* i put the alert functions in here, so they are in the right scope
for the bottom script in base.html to call */

function alertInput (id){
  /* shows the appropriate error message beneath the toolbox */
  $("div[id^=\"inputalert_\"]").fadeOut(0);
  $("#inputalert_"+id).fadeIn(800);
  $("#inputalert_"+id).fadeOut(4000);
}

function alertGlobal (id){
  /* shows the appropriate error banner below the header */
  $("div[id^=\"alert_\"]").fadeOut(0);
  $("#alert_"+id).slideDown(800);
  $("#alert_"+id).delay(10000).slideUp(800);
}

function alertAccountSettings (id){
  /* shows the appropriate error banner in the account settings section */
  $("div[id^=\"accountsettingsalert_\"]").fadeOut(0);
  $("#accountsettingsalert_"+id).slideDown(800);
  $("#accountsettingsalert_"+id).delay(2000).slideUp(800);
}

function alertInfoSettings (id){
  /* shows the appropriate error banner in the info settings section */
  $("div[id^=\"infosettingsalert_\"]").fadeOut(0);
  $("#infosettingsalert_"+id).slideDown(800);
  $("#infosettingsalert_"+id).delay(2000).slideUp(800);
}

function alertBoardSettings (id){
  /* shows the appropriate error message beneath the submit button */
  $("div[id^=\"boardsettingsalert_\"]").fadeOut(0);
  $("#boardsettingsalert_"+id).fadeIn(800);
  $("#boardsettingsalert_"+id).fadeOut(4000);
}
