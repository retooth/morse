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

  $("#new-topic-title").keydown(function(keyevent){
    if (keyevent.which === KEY_RETURN){
      $("#new-post").focus();
      keyevent.preventDefault();
    }
    sanitizeTopicTitle();
  });

  $("#new-topic-title").keyup(sanitizeTopicTitle);
  $("#new-topic-title").blur(sanitizeTopicTitle);

  function sanitizeTopicTitle (){
    var title = $("#new-topic-title");
    title.find("br").remove();
  }

  $("#create-new-topic").on("click", function(){
    var title = $("#new-topic-title").html();
    
    if (title.length < 3){
      alertInput("title-too-short");
      return false;
    }

    var text = $("#new-post").html();
    if (text.length < 20){
      alertInput("text-too-short");
      return false;
    }

    var boardID = $("#board").attr("board-id");

    var data = new Object({ title: title, text: text });
    var json = $.toJSON(data);

    $.ajax({
      url: boardID + "/start-topic",
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
