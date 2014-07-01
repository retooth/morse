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

  $("input[type=\"checkbox\"]").each(function(){
    if ($(this).is(":checked")){
      $(this).parents(".filter-option").addClass("filter-option-selected");
    }else{
      $(this).parents(".filter-option").removeClass("filter-option-selected");
    }
  });

  $("input[type=\"checkbox\"]").click(function(){
    if ($(this).is(":checked")){
      $(this).parents(".filter-option").addClass("filter-option-selected");
    }else{
      $(this).parents(".filter-option").removeClass("filter-option-selected");
    }
  });

  $("#filter-dropdown").click(function(){
    if ($(this).hasClass("closed-dropdown")){
      $(this).removeClass("closed-dropdown");
      $(this).addClass("open-dropdown");
      $("#filter-menu").slideDown(400);
    }else{
      $(this).removeClass("open-dropdown");
      $(this).addClass("closed-dropdown");
      $("#filter-menu").slideUp(400);
    }
  });

  $("#tooltip").children().hide();
  $("#tooltip").children("#tooltip-default").fadeIn(200);
  rebindToolTipEvents();

});

function rebindToolTipEvents (){
  console.log("bound tooltips to " + $("[tooltip]").length + " elements");
  $("[tooltip]").off("mouseenter");
  $("[tooltip]").on("mouseenter", function(){
    console.log("#tooltip-" + $(this).attr("tooltip"));
    $("#tooltip").children().hide();
    $("#tooltip").children("#tooltip-" + $(this).attr("tooltip")).fadeIn(200);
  });

  $("[tooltip]").off("mouseleave");
  $("[tooltip]").on("mouseleave", function(){
    $("#tooltip").children().hide();
    $("#tooltip").children("#tooltip-default").fadeIn(200);
  });
}
