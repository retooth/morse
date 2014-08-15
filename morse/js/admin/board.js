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

  $("#board-settings").submit(function(e){
    // prevent blank board title
    if ($("#new-board-title").val() !== ""){
      return;
    }
    $("#new-board-title").addClass("invalid-input");
    $("#new-board-title").focus();
    alertBoardSettings("blanktitle");
    e.preventDefault();
  });

  $(".mode ul").sortable({ 
    connectWith : ".mode ul",
    placeholder : "drag-and-drop-placeholder",
    create : allLiToHiddenInput,
    receive : allLiToHiddenInput
  });

  function allLiToHiddenInput (){
    $("#li-hidden-input").html("");
    liToHiddenInput( $("#ignorant-mode li"), "ignorant");
    liToHiddenInput( $("#readonly-mode li"), "readonly");
    liToHiddenInput( $("#poster-mode li"), "poster");
  }

  function liToHiddenInput (lilist, prefix){
    lilist.each(function (index){
      var group_id = $(this).attr("group-id");
      var hiddeninput = $("<input/>");
      hiddeninput.attr("type", "hidden");
      hiddeninput.attr("name", prefix + index);
      hiddeninput.val(group_id);
      hiddeninput.appendTo("#li-hidden-input");
    });
  }

  var ADMIN_GROUP_ID = "1";

  $("#ignorant-mode").on("sortreceive", function (e, ui){
    if(ui.item.attr("group-id") === ADMIN_GROUP_ID){
      ui.item.remove();
      ui.item.appendTo(ui.sender);
      alertGlobal("lockoutprevented");
    }
  });

});
