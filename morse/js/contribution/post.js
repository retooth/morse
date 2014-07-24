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
 rebindPostButtonEvents();
});

function rebindPostButtonEvents (){

  $("#create-new-post").off("click");
  $("#create-new-post").on("click", function(){
    var text = $("#new-post").html();
    if (text.length < 20){
      alertInput("text-too-short");
      return false;
    }

    var topicID = $("#topic").attr("topic-id");
    var references = getPostReferences($("#new-contribution"));

    var data = new Object({ text: text, referencedPostIDs: references });
    var json = $.toJSON(data);

    $.ajax({
      url: topicID + "/post",
      data: json,
      error: handleAjaxErrorBy( alertInput ),
      success: processNewPostResponse,
      dataType: "json",
    });
  });
}

function processNewPostResponse (){
  window.location.reload();
  // FIXME: how to scroll down AFTER reload??
  // TODO: maybe do an ajax implementation
}
