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

  $("#tooltip").children().hide();
  $("#tooltip").children("#tooltip-default").fadeIn(200);
  rebindToolTipEvents();

});

function rebindToolTipEvents (){
  $("[tooltip]").off("mouseenter");
  $("[tooltip]").on("mouseenter", function(){
    $("#tooltip").children().hide();
    $("#tooltip").children("#tooltip-" + $(this).attr("tooltip")).fadeIn(200);
  });

  $("[tooltip]").off("mouseleave");
  $("[tooltip]").on("mouseleave", function(){
    $("#tooltip").children().hide();
    $("#tooltip").children("#tooltip-default").fadeIn(200);
  });
}
