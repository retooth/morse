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

  changeToGroupMenu(1);

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
          if (users.length > 0){
            menu.find(".emptylist").fadeOut(0);
            for (var i = 0; i < users.length; i++){
              var id = users[i][0];
              var name = users[i][1];
              console.log(users[i]);
              var newli = $("<li user-id=\"" + id + "\">" + name + "</li>");
              newli.appendTo(menulist);
            }
	  }else{
            menu.find(".emptylist").fadeIn(200);
            console.log(menu.find(".emptylist"));
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

});
