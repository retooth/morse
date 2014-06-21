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

});
