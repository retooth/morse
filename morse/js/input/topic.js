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

  $("#newtopictitle").keydown(function(keyevent){
    if (keyevent.which === KEY_RETURN){
      $("#newtopictext").focus();
      keyevent.preventDefault();
    }
  });

  $("#docreate").on("click", function(){
    /* TODO: check blankpost
       alertInput("blankpost");
       */
    var title = $("#newtopictitle").html();
    var text = $("#newtopictext").html();
    var boardID = $("#board").attr("board-id");

    var data = new Object({ title: title, text: text });
    var json = $.toJSON(data);

    $.ajax({
      url: boardID + "/starttopic",
      data: json,
      error: handleAjaxErrorBy( alertInput ),
      success: processNewTopicResponse,
      dataType: "json",
    });
  });

  function processNewTopicResponse (response){
    window.location.href = "/topic/" + response.topicId;
  }

});
