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
  bindBanItemMouseOverEvents();
  rebindBanToolEvents();
  rebindBanEditActions();

  $("#create-new-ip-ban").on("click", function(){
    $(this).slideUp(400);
    $("#new-ip-ban").slideDown(400);
  });

  $("#new-ip-ban-option-permanent").on("click", function(){
    if ($(this).is(":checked")){
      $("#new-ip-ban-duration").fadeOut(400);
    }else{
      $("#new-ip-ban-duration").fadeIn(400);
    }
  });


  $("#issue-new-ip-ban").on("click", function(){

    var ALL_BOARDS = 0;
    var affectedBoards = [];

    $("#new-ip-ban-affected-boards input:checkbox:checked").each(function(){
      var board_id = parseInt($(this).attr("board-id"))
      affectedBoards.push(board_id);
    }); 

    var permanent = $("#new-ip-ban-option-permanent").is(":checked");
    var IPRange = $("#new-ip-ban-ip-range").val();
    var reason = $("#new-ip-ban-reason").html();

    var data = new Object({ IPRange: IPRange, reason: reason, affectedBoards: affectedBoards });
    if (!permanent){
        var duration = parseInt($("#new-ip-ban-duration").val());
        data.duration = duration;
    }

    var json = $.toJSON(data);
    $.ajax({
      url: "/ip-bans/new",
      data: json,
      error: function (response){

        // hide previous invalid input markers
        $(".invalid-input").removeClass("invalid-input");

        var jsonString = response.responseText;
        errorMessage = $.parseJSON(jsonString);

        if (errorMessage.errorCode === 2){
          switch (errorMessage.rejectedAttribute){
            case "IPRange":
              $("#new-ip-ban-ip-range").addClass("invalid-input");
              break;
            case "duration":
              $("#new-ip-ban-duration").addClass("invalid-input");
              break;
            case "reason":
              $("#new-ip-ban-reason").addClass("invalid-input");
              break;
          }
        }

      },
      success: function () { window.location.reload();  }
    });
  });

});
