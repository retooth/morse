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
  rebindBanItemEvents();

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
});
