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

    if ($("#topic").length === 0 &&
        $("#board").length === 0){
        return true;
    }

    if($("#topic").attr("topic-closed") === "True"){
      return true;
    }

    $("#typinginfo").slideUp(0);
    $("#inputwrapper").slideDown(400);

    var activeID = $(document.activeElement).attr("id");
    var atNewPost = $("#newposttext").length > 0;
    var atNewTopic = $("#newtopictitle").length > 0;
    var pressedReturn = (keyevent.which === 13);

    if (activeID !== "newtopictitle" &&
        activeID !== "newtopictext" &&
        activeID !== "newposttext" &&
        activeID !== "newhref"){

      if (atNewPost){
        $("#newposttext").focus();
      }else if (atNewTopic){
        $("#newtopictitle").focus();
      }

    }else if (activeID === "newtopictitle" && pressedReturn){
      $("#newtopictext").focus();
      keyevent.preventDefault();
    }  

  });


  $("#docreate").on("click", function(){
    /* TODO: check blankpost
       alertInput("blankpost");
       */
    var title = $("#newtopictitle").html();
    var text = $("#newtopictext").html();
    var boardID = $("#board").attr("board-id");

    var data = new Object({ title: title, text: text });
    var json = $.toJSON(data);

    $.ajax({
      url: boardID + "/starttopic",
      data: json,
      error: handleAjaxErrorBy( alertInput ),
      success: processNewTopicResponse,
      dataType: "json",
    });
  });


  $("#dopost").on("click", function(){
    /* TODO: check blankpost
       alertInput("blankpost");
       */
    var text = $("#newposttext").html();
    var topic_id = $("#topic").attr("topic-id");

    var data = new Object({ text: text });
    var json = $.toJSON(data);

    $.ajax({
      url: topic_id + "/post",
      data: json,
      error: handleAjaxErrorBy( alertInput ),
      success: processNewPostResponse,
      dataType: "json",
    });
  });


  function processNewTopicResponse (response){
    window.location.href = "/topic/" + response.topicId;
  }


  function processNewPostResponse (){
    window.location.reload();
    // FIXME: how to scroll down AFTER reload??
    // TODO: maybe do an ajax implementation
  }


  /* This is a workaround for a bug, that adds a another blockquote,
     if the user is inside a blockquote and presses enter */
  $("#newtopictext").on("keypress", blockquoteWorkaround);
  $("#newposttext").on("keypress", blockquoteWorkaround);


  function blockquoteWorkaround (keyevent) {

    var range = window.getSelection().getRangeAt();
    var element = range.commonAncestorContainer;

    element = (element.nodeType===1) ? element : element.parentNode; 

    if(element.nodeName === "BLOCKQUOTE" && keyevent.keyCode === 13 && !keyevent.shiftKey) {
      keyevent.preventDefault();
      document.execCommand("InsertParagraph");
      document.execCommand("Outdent");    
    }

  }


  /* formatting toolbox */

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
    // if return is pressed
    if(keyevent.which === 13){ 
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


  /* board info banners (TODO: replace with something good) */
  $(".boardentry").on("mouseenter", function (){
  });

  $(".boardentry").on("mouseleave", function (){
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


  /* goback tooltip */
  $("#goback").mouseenter(function(){
    $("#gobacktooltip").spellFadeIn(800,10);
  });

  $("#goback").mouseleave(function(){
    $("#gobacktooltip").spellFadeOut(800,100);
  });


  /* settings (info) ------------------------------ */

  //FIXME: delay until remove
  $(".deletewebsite").on("click", function(){
    $(this).parent().slideUp(200).remove();
    beautifyWebsiteList();
  });

  $("#anotherwebsite").click(function(){

    var website = $(".websitewrapper").first().clone();
    website.css("display", "none");
    website.children("input").val("");
    website.children("input").attr("placeholder", "...");
    website.insertBefore($("#anotherwebsitebr"));

    beautifyWebsiteList();

    website.slideDown(200);
    website.children("button").fadeIn(1200);

    /* rebind it (since new .deletewebsite elements were added) */
    $(".deletewebsite").off("click");
    //FIXME: see above
    $(".deletewebsite").on("click", function(){
      $(this).parent().slideUp(200).remove();
      beautifyWebsiteList();
    });

  });

  function beautifyWebsiteList(){

    /* makes website input list look like 
     * a block with round edges */
 
    var lastindex = $(".websitewrapper").length - 1;
    unbeautifyWebsiteList();

    if (lastindex !== 0){
      $(".websitewrapper").each(function (index){
        if (index === 0){
          $(this).addClass("first");
        }
        if (index > 0 && index < lastindex){
          $(this).addClass("middle");
        }
        if (index === lastindex){
          $(this).addClass("last");
        }
      });
    }

  }

  function unbeautifyWebsiteList(){
    $(".websitewrapper").removeClass("first");
    $(".websitewrapper").removeClass("middle");
    $(".websitewrapper").removeClass("last");
  }

  $("#updateinfo").click(function(){

    var bio = $("#bio").val();
    var websites = Array();
    $(".websitewrapper input").each(function (){
      websites.push($(this).val());
    });

    var info = new Object({ bio : bio, websites : websites});

    $(this).addClass("buttonspinner");

    $.ajax({
      url: "settings/updateinfo",
      data: $.toJSON(info),
      error: handleAjaxErrorBy( alertInfoSettings ),
      complete: function(){ $("#updateinfo").removeClass("buttonspinner"); },
    });

  });


  /* settings (account) --------------------------- */

  $(".accountdetail").keypress(function(){
    // see http://stackoverflow.com/questions/11627531
    $("#chromebugmask").slideDown(800);
    $("#updateaccount").fadeIn(400);
  });

  $("#updateaccount").click(function(){

    $("#newpassword").removeClass("redoutline");
    $("#newpasswordagain").removeClass("redoutline");
    $("#oldpassword").removeClass("redoutline");

    $(this).addClass("buttonspinner");

    var newPassword = $("#newpassword").val();
    var newPasswordAgain = $("#newpasswordagain").val();

    if (newPassword !== newPasswordAgain){
      alertAccountSettings("passwordsdontmatch");
      $("#newpassword").addClass("redoutline");
      $("#newpasswordagain").addClass("redoutline");
      $(this).removeClass("buttonspinner");
      return false;
    }

    var oldPassword = $("#oldpassword").val();
    var newEmail = $("#newemail").val();
    /* TODO: convention for json identifiers in pipe main.js <- ajax -> views.py */
    var account = { newemail : newEmail, newpassword : newPassword, oldpassword : oldPassword };

    $.ajax({
      url: "settings/updateaccount",
      data: $.toJSON(account),
      error: handleAjaxErrorBy( alertAccountSettings ),
      complete: function(){ 
        $("#updateaccount").removeClass("buttonspinner"); 
      },
    });

  });


  /* administration (boards) ---------------------- */

  $("#boardsettings").submit(function(e){
    // prevent blank board title
    if ($("#newboardtitle").val() !== ""){
      return;
    }
    $("#newboardtitle").addClass("redoutline");
    $("#newboardtitle").focus();
    alertBoardSettings("blanktitle");
    e.preventDefault();
  });

  $(".grouplist").sortable({ 
    connectWith : ".grouplist",
    placeholder : "ddplaceholder",
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
    lilist.each(function (index){

      var group_id = $(this).attr("group-id");

      var hiddeninput = $("<input/>");
      hiddeninput.attr("type", "hidden");
      hiddeninput.attr("name", prefix + index);
      hiddeninput.val(group_id);
      hiddeninput.appendTo("#lihiddeninput");

    });
  }

  $("#showmodelist").click(function(){
    $("#showmodelist").fadeOut(0);
    $("#hidemodelist").fadeIn(0);
    $("#modelist").slideDown(800);
  });

  $("#hidemodelist").click(function(){
    $("#hidemodelist").fadeOut(0);
    $("#showmodelist").fadeIn(0);
    $("#modelist").slideUp(800);
  });

  $("#modelistignorant").on("sortreceive", function (e, ui){
    if(ui.item.attr("group-id") === ADMIN_GROUP_ID){
      ui.item.remove();
      ui.item.appendTo(ui.sender);
      alertGlobal("lockoutprevented");
    }
  });

  /* administration (group management) ------------ */

  function changeToGroupMenu (groupID){
    $(".groupmenu").fadeOut(0);
    console.log("found " + $(".groupmenu").length + " menus to fade out"); 
    console.log("changeto " + groupID); 
    $(".groupmenu[group-id=" + groupID + "]").fadeIn(400);
  }

  rebindGroupNavEvents();

  function rebindGroupNavEvents (){
    $("#groupnav li").off("click");
    $("#groupnav li").on("click", function(){
      /* tab control */
      var groupID = $(this).attr("group-id");
      $("#groupnav li").removeClass("selected");
      $(this).addClass("selected");
      changeToGroupMenu(groupID);
    });
  }

  $(".groupuserlist").sortable();

  $(".userlist li").draggable({ 
    appendTo: "body", 
    containment: "window", 
    helper: "clone", 
    connectToSortable: ".groupuserlist"
  });

  /* user scroll list */

  $("#scrolldown").mousedown(function(){
    var current = parseInt( $("#userlist #scroller").css("top").replace(/[^-\d\.]/g, "") );
    var scrollerheight = $("#userlist #scroller").outerHeight();
    var viewportheight = $("#userlist").height();
    if (current <= - scrollerheight + viewportheight){
      return false;
    }
    var newvalue = (current - 10) + "px";
    $("#userlist #scroller").css("top", newvalue);
  });

  $("#scrollup").mousedown(function(){
    var current = parseInt( $("#userlist #scroller").css("top").replace(/[^-\d\.]/g, "") );
    if (current === 0){
      return false;
    }
    var newvalue = (current + 10) + "px";
    $("#userlist #scroller").css("top", newvalue);
  });

  rebindGroupUserDragAndDropEvents();

  function rebindGroupUserDragAndDropEvents(){
    $(".groupuserlist").off("sortstop"); 
    $(".groupuserlist").on("sortstop", function (e, ui){

      var new_user = ui.item;
      new_user.addClass("user");
      var id = new_user.attr("user-id");

      // check for read-only groups (guest/register)
      if ( $(this).parent(".groupmenu").hasClass("readonly") ){
        alertGlobal("readonlygroup");
        new_user.remove();

      }else if ( $(this).children("li[user-id=\"" + id + "\"]").length > 1 ){
                 // This blob finds <li>s with the same user-id attr (which indicates
                 // that this user is already in this group). It is >1 and not >0,
                 // because at sortstop the new element is already added to <ul>

        alertGlobal("alreadyingroup");
        new_user.remove();

      }else{
        $(this).attr("tainted", true);

        // this section adds a close button to the
        // li element before it gets integrated into
        // the group view. it may seem pedestrian,
        // but simply adding the button to new_user
        // caused it to be added every time the user
        // reordered the list. if you know a more
        // elegant solution, please fork and code.

        var user_id = new_user.attr("user-id");
        var username = $(".user[user-id=" + user_id +"]").html();

        var newelement = $("<li></li>");
        newelement.html(username);
        newelement.attr("user-id", user_id);    

        // we can be sure, that there is always at least one
        // .deletefromgroup. By cloning we can change the close
        // button in the template without the need to change it here
        var closebutton = $(".deletefromgroup").first().clone();
        closebutton.appendTo(newelement);

        ui.item.replaceWith(newelement);

        // rebind click events
        $(".deletefromgroup").off("click");
        $(".deletefromgroup").on("click", deleteFromGroup);
      }

    });
  }

  $(".deletefromgroup").on("click", deleteFromGroup);

  ADMIN_GROUP_ID = "1";

  function deleteFromGroup(){

    var listItem = $(this).parents("li");
    var groupUserList = $(this).parents(".groupuserlist");

    if ( listItem.attr("user-id") === $("#useravatar").attr("user-id") &&
         groupUserList.attr("group-id") === ADMIN_GROUP_ID ){
      alertGlobal("lockoutprevented");
    }else{
      groupUserList.attr("tainted", true);
      listItem.remove();
    }

  }  

  $("#updategroups").click(function(){

    /* sends all tainted data of tainted groupmenus
     * via ajax to the server
     * */

    var taintedLists = $(".groupuserlist[tainted=\"true\"]"); 
    var taintedSettings = $(".header[tainted=\"true\"]"); 

    if ( taintedLists.length === 0 && taintedSettings.length === 0){
      return False;
    }

    $(this).addClass("buttonspinner");

    taintedLists.each(function (){

      var users = $(this).children("li");

      var userIDs = Array();
      users.each(function (){
        var id = $(this).attr("user-id");
        userIDs.push(id);
      });

      var groupID = $(this).parents(".groupmenu").attr("group-id");
      var json = JSON.stringify(userIDs);
      $.ajax({
        url: "updategroup/" + groupID,
        data: json,
        error: handleAjaxErrorBy(alertGlobal),
        complete: function(){ $("#updategroups").removeClass("buttonspinner"); },
      });

    });

    taintedSettings.each(function (){

      var label_id  = $(this).children(".picked").attr("label-id");
      var group_id  = $(this).parents(".groupmenu").attr("group-id");
      var may_edit  = $(this).find(".mayedit").is(":checked");
      var may_close = $(this).find(".mayclose").is(":checked");
      var may_stick = $(this).find(".maystick").is(":checked");

      var meta = new Object({ label_id : label_id, may_edit : may_edit, may_close : may_close, may_stick : may_stick });

      $.ajax({
        url: "updategroupmeta/" + group_id,
        data: $.toJSON(meta),
        error: handleAjaxErrorBy(alertGlobal),
        success: function(){ $("#updategroups").removeClass("buttonspinner"); },
      });
    });

  });

  rebindColorPickerEvents();

  function rebindColorPickerEvents (){
    $(".colorpicker").off("click");
    $(".colorpicker").on("click", function(){

      var groupMenu = $(this).parents(".groupmenu");
      var groupID = groupMenu.attr("group-id");

      var pickedLabel = groupMenu.find(".picked");
      var oldLabelID = pickedLabel.attr("label-id");
      var newLabelID = $(this).attr("label-id");

      var groupTab = $("#groupnav li[group-id=\"" + groupID + "\"]");
      groupTab.removeClass("label" + oldLabelID);
      groupTab.addClass("label" + newLabelID);
      
      $(this).addClass("picked");
      pickedLabel.removeClass("picked");
      
      $(this).parents(".header").attr("tainted", true);

    });
  }

  rebindGroupFlagEvents();

  function rebindGroupFlagEvents (){
    $(".groupflag").off("change");
    $(".groupflag").on("change", function(){
      $(this).parents(".header").attr("tainted", true);
    });
  }

  $("#newgroup").click(function(){
    /* in case the user doesn't click on input directly*/
    $("#newgroupname").focus();
  });

  $("#newgroupname").keypress(function(keyevent){
    if (keyevent.which === 13){
     
      var name = $(this).val()
      var data = new Object({ name: name });
      var json = $.toJSON(data);

      $.ajax({
        url: "creategroup",
        data: json,
        error: handleAjaxErrorBy( alertGlobal ),
        success: loadNewGroup,
        dataType: "json",
      });

     }
  });

  function loadNewGroup (response){
    var groupID = response.newGroupID;
    var name = response.name;

    var newLi = $("<li>");
    newLi.attr("group-id", groupID);
    newLi.addClass("label0"); 
    newLi.html(name);
    newLi.insertBefore("#newgroup");
    console.log("das neue li hat die group-id " + newLi.attr("group-id"));
    rebindGroupNavEvents();

    var newGroup = $(".groupmenu[group-id=1]").clone();
    newGroup.attr("group-id", groupID);

    /* make clean */
    newGroup.find("input").each(function(){
      $(this).prop("checked", false);
    });
    newGroup.find(".picked").removeClass("picked");
    newGroup.find(".colorpicker[label-id=0]").addClass("picked");
    newGroup.find(".groupuserlist").html("");
    newGroup.find(".groupuserlist").sortable();

    /* insert delete button*/
    var deleteButton = $("<button/>");
    deleteButton.addClass("deletegroup");
    var deleteImage = $("<img/>");
    deleteImage.attr("src", "/static/trash.png");
    deleteImage.appendTo(deleteButton);
    var toolDiv = newGroup.find(".grouptools");
    deleteButton.appendTo(toolDiv);

    newGroup.insertAfter("#userlistwrapper");
    rebindColorPickerEvents();
    rebindGroupFlagEvents();
    rebindGroupUserDragAndDropEvents();
    rebindDeleteGroupEvents();

    changeToGroupMenu(groupID);
    $("#newgroupname").val("");

  }

  rebindDeleteGroupEvents();

  function rebindDeleteGroupEvents (){
    $(".deletegroup").off("click");
    $(".deletegroup").on("click", function(){
      var groupMenu = $(this).parents(".groupmenu");
      showDialog("deletegroup", groupMenu);

      groupMenu.on("click", "[dialog-control=\"1\"]", function(){
        hideDialogs();

        var groupID = $(this).parents(".groupmenu").attr("group-id");
        var data = new Object({ groupID: groupID });
        var json = $.toJSON(data);

        $.ajax({
          url: "deletegroup",
          data: json,
          error: handleAjaxErrorBy( alertGlobal ),
          success: function(){
            $("#groupnav li[group-id=\"" + groupID + "\"]").fadeOut(800);
            $(".groupmenu").fadeOut(0);
            $("#welcomegrouptip").fadeIn(400);
            $(".groupmenu[group-id=\"" + groupID + "\"]").remove();
          },
        });
      });

      groupMenu.on("click", "[dialog-control=\"2\"]", function(){
        hideDialogs();
      });

    });
  }

  $("button.closethread").click(function(){
    var topicID = $(this).parents(".topicentry").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/closethread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.closedID;
        var entry = $(".topicentry[topic-id=\"" + topicID + "\"]");
        entry.addClass("topicclosed");
        entry.find(".closethread").fadeOut(0);
        entry.find(".openthread").fadeIn(200);
      },
    });
  });

  $("button.openthread").click(function(){
    var topicID = $(this).parents(".topicentry").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/openthread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.openedID;
        var entry = $(".topicentry[topic-id=\"" + topicID + "\"]");
        entry.removeClass("topicclosed");
        entry.find(".openthread").fadeOut(0);
        entry.find(".closethread").fadeIn(200);
      },
    });
  });

  function handleAjaxErrorBy (callback){

    function handle (response){

      var processable = Array();
      processable.push(403);

      if(processable.indexOf( response.status ) >= 0){
        callback(response.responseText);
      }else{
        callback("ajax");
      }

    }

    return handle;
  }

});

/* i put the alert functions in here, so they are in the right scope
   for the bottom script in base.html to call */

function showDialog (id, parent){
  hideDialogs();

  var dialog = $("#dialog_"+id); 
  var newDialogWrapper = dialog.parents(".dialogwrapper").clone();
  newDialogWrapper.appendTo(parent);

  var closebutton = newDialogWrapper.find(".close");
  closebutton.click(function(){
    hideDialogs();
  });

  newDialogWrapper.fadeIn(200);
}

function hideDialogs(){
  $(".dialogwrapper").fadeOut(0);
}

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

  /* FIXME: develop clean highlighting system */
  if (id === "wrongpassword"){
    $("#oldpassword").addClass("redoutline");
  }

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

