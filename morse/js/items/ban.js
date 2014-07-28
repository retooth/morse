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

function rebindBanItemEvents (){

  $(".ban-item").off("mouseenter");
  $(".ban-item").on("mouseenter", function(){
    var banItemTools = $(this).find(".ban-item-tools");
    var timer = setTimeout(function(){
      banItemTools.fadeIn(400);
    }, 1000);
    $(this).data("toolRevealDelay", timer);
    var reason = $(this).find(".ban-reason");
    var timeLeft = $(this).find(".ban-expiration-time-left");
    var timer = setTimeout(function(){
      reason.slideDown(400);
      timeLeft.fadeIn(400);
    }, 1000);
    $(this).data("dataRevealDelay", timer);
  });

  $(".ban-item").off("mouseleave");
  $(".ban-item").on("mouseleave", function(){
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);
    timer = $(this).data("dataRevealDelay");
    clearTimeout(timer);

    var banItemTools = $(this).find(".ban-item-tools");
    banItemTools.fadeOut(400);

    var reason = $(this).find(".ban-reason");
    var timeLeft = $(this).find(".ban-expiration-time-left");
    reason.slideUp(400);
    timeLeft.fadeOut(400);
  });
}
