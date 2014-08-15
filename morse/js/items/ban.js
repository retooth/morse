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

function unbindBanItemMouseOverEvents(){
  $(".ban-item").off("mouseenter");
  $(".ban-item").off("mouseleave");
}

function bindBanItemMouseOverEvents (){

  $(".ban-item").on("mouseenter", function(){
    var banItemTools = $(this).find(".ban-item-tools");
    var timer = setTimeout(function(){
      banItemTools.fadeIn(400);
    }, 1000);
    $(this).data("toolRevealDelay", timer);
    var reason = $(this).find(".ban-reason");
    var timeLeft = $(this).find(".ban-expiration-time-left");
    var affectedBoards = $(this).find(".ban-affected-boards-display");
    var timer = setTimeout(function(){
      reason.slideDown(400);
      timeLeft.fadeIn(400);
      affectedBoards.slideDown(400);
    }, 1000);
    $(this).data("dataRevealDelay", timer);
  });

  $(".ban-item").on("mouseleave", function(){
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);
    timer = $(this).data("dataRevealDelay");
    clearTimeout(timer);

    var banItemTools = $(this).find(".ban-item-tools");
    banItemTools.fadeOut(400);

    var reason = $(this).find(".ban-reason");
    var timeLeft = $(this).find(".ban-expiration-time-left");
    var affectedBoards = $(this).find(".ban-affected-boards-display");
    reason.slideUp(400);
    timeLeft.fadeOut(400);
    affectedBoards.slideUp(400);
  });
}

function rebindBanToolEvents (){

  $(".ban-action-edit").off("click");
  $(".ban-action-edit").on("click", function () {
    var banItem = $(this).parents(".ban-item");
    banItem.find(".ban-header-display").slideUp(400);
    banItem.find(".ban-header-edit").slideDown(400);
    banItem.find(".ban-affected-boards-display").slideUp(400);
    banItem.find(".ban-affected-boards-edit").slideDown(400);
    banItem.find(".ban-edit-footer").slideDown(400);
    unbindBanItemMouseOverEvents();
  });

}

function rebindBanEditActions (){

  $(".ban-item .ban-edit-action-update").off("click");
  $(".ban-item .ban-edit-action-update").on("click", function () {
    var banItem = $(this).parents(".ban-item");
    var IPRange = banItem.find(".ban-ip-range").val();
    var duration = parseInt(banItem.find(".ban-duration").val())
    var reason = $(".ban-reason").html();
    
    var affectedBoards = [];

    banItem.find(".ban-affected-boards-edit input:checkbox:checked").each(function(){
      var board_id = parseInt($(this).attr("board-id"))
      affectedBoards.push(board_id);
    }); 

    var permanent = banItem.find(".ban-option-permanent").is(":checked");

    var data = new Object({ IPRange: IPRange, reason: reason, affectedBoards: affectedBoards });
    if (!permanent){
        var duration = parseInt(banItem.find(".ban-duration").val());
        data.duration = duration;
    }
    var json = $.toJSON(data);
    var banID = banItem.attr("ban-id")

    $.ajax({
      url: "/ip-bans/" + banID + "/update",
      data: json,
      error: function (response){

        // hide previous invalid input markers
        $(".invalid-input").removeClass("invalid-input");

        var jsonString = response.responseText;
        errorMessage = $.parseJSON(jsonString);

        if (errorMessage.errorCode === 2){
          switch (errorMessage.rejectedAttribute){
            case "IPRange":
              banItem.find(".ban-ip-range").addClass("invalid-input");
              break;
            case "duration":
              banItem.find(".ban-duration").addClass("invalid-input");
              break;
            case "reason":
              banItem.find(".ban-reason").addClass("invalid-input");
              break;
          }
        }

      },
      success: function () { window.location.reload();  }
    });

  });

  $(".ban-option-permanent").off("change");
  $(".ban-option-permanent").on("change", function(){
    var banItem = $(this).parents(".ban-item");
    if ($(this).is(":checked")){
      banItem.find(".ban-duration").fadeOut(400);
    }else{
      banItem.find(".ban-duration").fadeIn(400);
    }
  });

}
