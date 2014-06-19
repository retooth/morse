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

  $("#newtopictitle").keydown(function(keyevent){
    if (keyevent.which === KEY_RETURN){
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

    if(element.nodeName === "BLOCKQUOTE" && keyevent.keyCode === KEY_RETURN && !keyevent.shiftKey) {
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
      url: "/account/updateinfo",
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
      url: "/account/update",
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
    $("#groupnav li").removeClass("selected");
    $("#groupnav li[group-id=\"" + groupID + "\"]").addClass("selected");
    $(".groupmenu").fadeOut(0);
    $(".groupmenu[group-id=" + groupID + "]").fadeIn(400);
  }

  rebindGroupNavEvents();

  function rebindGroupNavEvents (){
    $("#groupnav li").off("click");
    $("#groupnav li").on("click", function(){
      /* tab control */
      var groupID = $(this).attr("group-id");
      changeToGroupMenu(groupID);
    });
  }

  rebindUserMenuEvents();

  function rebindUserMenuEvents (){
    $(".groupmenu .newuser input").off("keyup");
    $(".groupmenu .newuser input").on("keyup", function(keyevent){

      var li = $(this).parents(".newuser");
      var menu = li.find(".newusermenu");
      var menulist = menu.find("ul");

      /* drop down behavior */
      if (keyevent.which === KEY_RETURN){
        var selected = menu.find(".selected");
        if (selected.length === 0){
          return true;
        }
        var userID = selected.attr("user-id");
        var group = $(this).parents(".groupmenu");
        var groupID = group.attr("group-id");
        console.log(groupID);
        addUserToGroup(userID, groupID);
        return true;
      }

      if (keyevent.which === KEY_DOWN){
        var selected = menu.find(".selected");
        if (selected.length === 0){
          var first = menulist.children().first().addClass("selected");
          first.addClass("selected");
          $(this).val( first.html() );
          return true;
        }
        selected.removeClass("selected");
        var next = selected.next();
        if (next.length === 0){
          var original = $(this).attr("original-value");
          $(this).val(original);
          return true;
        }
        next.addClass("selected");
        $(this).val( next.html() );
        return true;
      }

      if (keyevent.which === KEY_UP){
        var selected = menu.find(".selected");
        if (selected.length === 0){
          var last = menulist.children("li").last()
          last.addClass("selected");
          $(this).val( last.html() );
          return true;
        }
        selected.removeClass("selected");
        var prev = selected.prev();
        if (prev.length === 0){
          var original = $(this).attr("original-value");
          $(this).val(original);
          return true;
        }
        prev.addClass("selected");
        $(this).val( prev.html() );
        return true;
      }

      var pattern = $(this).val();
      $(this).attr("original-value", pattern);

      var position = li.position();
      menu.css("top", position.top + li.outerHeight());
      menu.css("left", position.left);

      $.ajax({
        url: "/userlist.json?pattern=" + pattern,
        type: "GET",
        success: function(response){
          var users = response.users;
          menulist.html("");
          for (var i = 0; i < users.length; i++){
            var id = users[i][0];
            var name = users[i][1];
            console.log(users[i]);
            var newli = $("<li user-id=\"" + id + "\">" + name + "</li>");
            newli.appendTo(menulist);
          }
          menu.fadeIn(200);
        },
        error: handleAjaxErrorBy(alertGlobal),
      });

    });
    $(".newusermenu ul").off("click");
    $(".newusermenu ul").on("click", "li", function(){
      var userID = $(this).attr("user-id");
      var groupID = $(this).parents(".groupmenu").attr("group-id");
      addUserToGroup(userID, groupID);
    });
  }

  function addUserToGroup (userID, groupID){
    var ul = $(".groupmenu[group-id=\"" + groupID + "\"] ul");
    var username = ul.find(".newusermenu li[user-id=\"" + userID + "\"]").html();
    var data = new Object({ userID : userID, groupID : groupID });
    $.ajax({
      url: "/groups/adduser",
      data: $.toJSON(data),
      success: function(response){

        var newli = $("<li></li>");
        newli.html(username);
        newli.attr("user-id", userID);    

        // we can be sure, that there is always at least one
        // .deletefromgroup. By cloning we can change the close
        // button in the template without the need to change it here
        var closebutton = $(".deletefromgroup").first().clone();
        closebutton.appendTo(newli);

        $(".newuser input").val("");
        $(".newusermenu").fadeOut(200);

        newUserLi = ul.find(".newuser");
        newli.insertBefore(newUserLi);

        // rebind click events
        $(".deletefromgroup").off("click");
        $(".deletefromgroup").on("click", deleteFromGroup);

      },
      error: handleAjaxErrorBy(alertGlobal),
    });
  }

  $(".deletefromgroup").on("click", deleteFromGroup);

  ADMIN_GROUP_ID = "1";

  function deleteFromGroup(){

    var listItem = $(this).parents("li");
    var groupMenu = $(this).parents(".groupmenu");
    var userID = listItem.attr("user-id");
    var groupID = groupMenu.attr("group-id");

    if ( userID === $("#useravatar").attr("user-id") &&
         groupID === ADMIN_GROUP_ID ){
      alertGlobal("lockoutprevented");
    }else{
      var data = new Object({ userID : userID, groupID : groupID });
      $.ajax({
        url: "/groups/removeuser",
        data: $.toJSON(data),
        success: function(response){
          listItem.remove();
          $(".newuser input").val("");
          $(".newusermenu").fadeOut(200);
        },
        error: handleAjaxErrorBy(alertGlobal),
      });
    }

  }  

  rebindColorPickerEvents();

  function rebindColorPickerEvents (){
    $(".colorpicker").off("click");
    $(".colorpicker").on("click", function(){

      var groupMenu = $(this).parents(".groupmenu");
      var groupID = groupMenu.attr("group-id");

      var oldLabel = groupMenu.find(".picked");
      var oldLabelID = oldLabel.attr("label-id");
      var newLabel = $(this);
      var newLabelID = newLabel.attr("label-id");

      var groupTab = $("#groupnav li[group-id=\"" + groupID + "\"]");

      var data = new Object({ groupID: groupID, labelID: newLabelID })

      $.ajax({
        url: "/groups/changelabel",
        data: $.toJSON(data),
        error: handleAjaxErrorBy( alertGlobal ),
        success: function(){
          groupTab.removeClass("label" + oldLabelID);
          groupTab.addClass("label" + newLabelID);
          newLabel.addClass("picked");
          oldLabel.removeClass("picked");
        },
      });

    });
  }

  rebindGroupFlagEvents();

  function rebindGroupFlagEvents (){
    $(".groupflag").off("change");
    $(".groupflag").on("change", function(){
      var flagMenu = $(this).parents(".groupflags");
      var groupMenu = $(this).parents(".groupmenu");
      var groupID = groupMenu.attr("group-id");
      var changed = $(this);

      var mayEdit  = flagMenu.find(".mayedit").is(":checked");
      var mayClose = flagMenu.find(".mayclose").is(":checked");
      var mayStick = flagMenu.find(".maystick").is(":checked");

      var data = new Object({ groupID: groupID, mayEdit : mayEdit, mayClose : mayClose, mayStick : mayStick });
      console.log("changed");
      $.ajax({
        url: "/groups/updateflags",
        data: $.toJSON(data),
        error: [handleAjaxErrorBy(alertGlobal), function(){
          /* reset the flag */
          changed.prop("checked", !changed.prop("checked"));
        }],
      });
    });
  }

  $("#newgroup").click(function(){
    /* in case the user doesn't click on input directly*/
    $("#newgroupname").focus();
  });

  $("#newgroupname").keypress(function(keyevent){
    if (keyevent.which === KEY_RETURN){
     
      var name = $(this).val()
      var data = new Object({ name: name });
      var json = $.toJSON(data);

      $.ajax({
        url: "/groups/create",
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

    // we can be sure, that there is always at least one
    // .newuser li. By cloning we can change the close
    // button in the template without the need to change it here
    var newUserLi = $(".newuser").first().clone();
    newGroup.find(".groupuserlist").append(newUserLi);

    /* insert delete button*/
    var deleteButton = $("<button/>");
    deleteButton.addClass("deletegroup");
    var deleteImage = $("<img/>");
    deleteImage.attr("src", "/static/trash.png");
    deleteImage.appendTo(deleteButton);
    var toolDiv = newGroup.find(".grouptools");
    deleteButton.appendTo(toolDiv);

    newGroup.insertBefore(".groupmenu[group-id=\"1\"]");
    rebindColorPickerEvents();
    rebindGroupFlagEvents();
    rebindDeleteGroupEvents();
    rebindUserMenuEvents();

    changeToGroupMenu(groupID);
    $("#newgroupname").val("");
    $(".newuser input:visible").focus();

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
          url: "/groups/delete",
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

  /* moderation (group management) ------------ */

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

  /* error handling --------------------------- */

  function handleAjaxErrorBy (callback){

    function handle (response){

      var processable = Array();
      processable.push(403);
      processable.push(412);

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

