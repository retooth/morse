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
    $("#group-navigation li").removeClass("selected");
    $("#group-navigation li[group-id=\"" + groupID + "\"]").addClass("selected");
    $(".group-properties-menu").fadeOut(0);
    $(".group-properties-menu[group-id=" + groupID + "]").fadeIn(400);
  }

  rebindGroupNavEvents();

  function rebindGroupNavEvents (){
    $("#group-navigation li").off("click");
    $("#group-navigation li").on("click", function(){
      /* tab control */
      var groupID = $(this).attr("group-id");
      changeToGroupMenu(groupID);
    });
  }

  rebindUserMenuEvents();

  function rebindUserMenuEvents (){
    $(".group-properties-menu .new-member input").off("keyup");
    $(".group-properties-menu .new-member input").on("keyup", function(keyevent){

      var li = $(this).parents(".new-member");
      var menu = li.find(".new-member-menu");
      var menulist = menu.find("ul");

      /* drop down behavior */
      if (keyevent.which === KEY_RETURN){
        var selected = menu.find(".selected");
        if (selected.length === 0){
          return true;
        }
        var userID = selected.attr("user-id");
        var group = $(this).parents(".group-properties-menu");
        var groupID = group.attr("group-id");
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
        url: "/search/users.json?pattern=" + pattern,
        type: "GET",
        success: function(response){
          var users = response.users;
          menulist.html("");
          if (users.length > 0){
            menu.find(".empty-list").fadeOut(0);
            for (var i = 0; i < users.length; i++){
              var id = users[i][0];
              var name = users[i][1];
              console.log(users[i]);
              var newli = $("<li user-id=\"" + id + "\">" + name + "</li>");
              newli.appendTo(menulist);
            }
          }else{
            menu.find(".empty-list").fadeIn(200);
            console.log(menu.find(".emptylist"));
          }
          menu.fadeIn(200);
        },
        error: handleAjaxErrorBy(alertGlobal),
      });

    });
    $(".new-member-menu ul").off("click");
    $(".new-member-menu ul").on("click", "li", function(){
      var userIDString = $(this).attr("user-id");
      var groupIDString = $(this).parents(".group-properties-menu").attr("group-id");
      var userID = parseInt(userIDString);
      var groupID = parseInt(groupIDString);
      addUserToGroup(userID, groupID);
    });
  }

  function addUserToGroup (userID, groupID){
    var ul = $(".group-properties-menu[group-id=\"" + groupID + "\"] .group-property-members ul");
    var username = ul.find(".new-member-menu li[user-id=\"" + userID + "\"]").html();
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
        var closebutton = $(".delete-from-group").first().clone();
        closebutton.appendTo(newli);

        $(".new-member input").val("");
        $(".new-member-menu").fadeOut(200);

        newUserLi = ul.find(".new-member");
        newli.insertBefore(newUserLi);

        // rebind click events
        $(".delete-from-group").off("click");
        $(".delete-from-group").on("click", deleteFromGroup);

      },
      error: handleAjaxErrorBy(alertGlobal),
    });
  }

  $(".delete-from-group").on("click", deleteFromGroup);

  ADMIN_GROUP_ID = "1";

  function deleteFromGroup(){

    var listItem = $(this).parents("li");
    var groupMenu = $(this).parents(".group-properties-menu");
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
          $(".new-member input").val("");
          $(".new-member-menu").fadeOut(200);
        },
        error: handleAjaxErrorBy(alertGlobal),
      });
    }

  }  

  rebindColorPickerEvents();

  function rebindColorPickerEvents (){
    $(".colorpicker").off("click");
    $(".colorpicker").on("click", function(){

      var groupMenu = $(this).parents(".group-properties-menu");
      var groupIDString = groupMenu.attr("group-id");
      var groupID = parseInt(groupIDString);

      var oldLabel = groupMenu.find(".picked");
      var oldLabelIDString = oldLabel.attr("label-id");
      var newLabel = $(this);
      var newLabelIDString = newLabel.attr("label-id");
      var newLabelID = parseInt(newLabelIDString);

      var groupPennon = $("#group-navigation li[group-id=\"" + groupID + "\"] .group-pennon");

      var data = new Object({ groupID: groupID, labelID: newLabelID })

      $.ajax({
        url: "/groups/changelabel",
        data: $.toJSON(data),
        error: handleAjaxErrorBy( alertGlobal ),
        success: function(){
          groupPennon.removeClass("label-" + oldLabelIDString);
          groupPennon.addClass("label-" + newLabelIDString);
          newLabel.addClass("picked");
          oldLabel.removeClass("picked");
        },
      });

    });
  }

  rebindGroupFlagEvents();

  function rebindGroupFlagEvents (){
    $(".group-right").off("change");
    $(".group-right").on("change", function(){

      var flagMenu = $(this).parents(".group-property-rights");
      var groupMenu = $(this).parents(".group-properties-menu").first();

      var groupIDString = groupMenu.attr("group-id");
      var groupID = parseInt(groupIDString);
      var changed = $(this);

      var mayEditAllPosts  = flagMenu.find(".may-edit-all-posts").is(":checked");
      var mayCloseTopics = flagMenu.find(".may-close-topics").is(":checked");
      var mayPinTopics = flagMenu.find(".may-pin-topics").is(":checked");

      var data = new Object({ groupID: groupID, mayEditAllPosts : mayEditAllPosts, 
                              mayCloseTopics : mayCloseTopics, mayPinTopics : mayPinTopics });
      $.ajax({
        url: "/groups/updaterights",
        data: $.toJSON(data),
        error: [handleAjaxErrorBy(alertGlobal), function(response){
          /* reset the flag */
          changed.prop("checked", !changed.prop("checked"));
        }],
      });
    });
  }

  $("#new-group").click(function(){
    /* in case the user doesn't click on input directly*/
    $("#new-group-name").focus();
  });

  $("#new-group-name").keypress(function(keyevent){
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

    var newPennon = $("<span>");
    newPennon.addClass("icon");
    newPennon.addClass("group-pennon");
    newPennon.addClass("label-0");
    
    var newGroupName = $("<span>");
    newGroupName.addClass("group-name");
    newGroupName.html(name);

    newPennon.appendTo(newLi); 
    newGroupName.appendTo(newLi); 

    newLi.insertBefore("#new-group");
    rebindGroupNavEvents();

    var newGroup = $(".group-properties-menu[group-id=1]").clone();
    newGroup.attr("group-id", groupID);
    newGroup.find(".current-group-name").html(name);

    /* make clean */
    newGroup.find("input").each(function(){
      $(this).prop("checked", false);
    });
    newGroup.find(".picked").removeClass("picked");
    newGroup.find(".colorpicker[label-id=0]").addClass("picked");
    newGroup.find(".group-property-members .user").remove();

    /* insert delete button*/
    var deleteButton = $("<button/>");
    deleteButton.addClass("delete-group");
    var deleteImage = $("<img/>");
    deleteImage.attr("src", "/static/trash.png");
    deleteImage.appendTo(deleteButton);
    var toolDiv = newGroup.find(".group-tools");
    deleteButton.appendTo(toolDiv);

    newGroup.insertBefore(".group-properties-menu[group-id=\"1\"]");
    rebindColorPickerEvents();
    rebindGroupFlagEvents();
    rebindDeleteGroupEvents();
    rebindUserMenuEvents();

    changeToGroupMenu(groupID);
    $("#new-group-name").val("");
    $(".new-member input:visible").focus();

  }

  rebindDeleteGroupEvents();

  function rebindDeleteGroupEvents (){
    $(".delete-group").off("click");
    $(".delete-group").on("click", function(){
      var groupMenu = $(this).parents(".group-properties-menu");
      showDialog("deletegroup", groupMenu);

      groupMenu.on("click", "[dialog-control=\"1\"]", function(){
        hideDialogs();

        var groupIDString = $(this).parents(".group-properties-menu").attr("group-id");
        var groupID = parseInt(groupIDString);
        var data = new Object({ groupID: groupID });
        var json = $.toJSON(data);

        $.ajax({
          url: "/groups/delete",
          data: json,
          error: handleAjaxErrorBy( alertGlobal ),
          success: function(){
            $("#group-navigation li[group-id=\"" + groupID + "\"]").fadeOut(800);
            $(".group-properties-menu").fadeOut(0);
            $(".group-properties-menu[group-id=\"1\"]").fadeIn(400);
            $(".group-properties-menu[group-id=\"" + groupID + "\"]").remove();
          },
        });
      });

      groupMenu.on("click", "[dialog-control=\"2\"]", function(){
        hideDialogs();
      });

    });
  }

});
