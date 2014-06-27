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

  $("#filter-menu button").mousedown(function(){
    if ($(this).hasClass("latched")) {
      $(this).removeClass("latched");
      $(this).addClass("unlatching");
    }else{
      $(this).addClass("latching");
    }
  });

  $("#filter-menu button").mouseup(function(){
    if ($(this).hasClass("latching")) {
      $(this).removeClass("latching");
      $(this).addClass("latched");
    }else if ($(this).hasClass("unlatching")){
      $(this).removeClass("unlatching");
    }
  });

  $("#filter-menu button").mouseleave(function(){
    $(".filter-menu-tooltip").fadeOut(0);
  });

  $("#filter-option-favorited").mouseenter(function(){
    $("#filter-option-tooltip-favorited").fadeIn(0);
  });
  
  $("#filter-option-unread").mouseenter(function(){
    $("#filter-option-tooltip-unread").fadeIn(0);
  });

  $("#filter-option-followed").mouseenter(function(){
    $("#filter-option-tooltip-followed").fadeIn(0);
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

  console.log("included filter");

});
