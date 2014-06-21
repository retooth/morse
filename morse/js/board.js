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

  $("button.closethread").click(function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/closethread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.closedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.addClass("topicclosed");
        item.find(".closethread").fadeOut(0);
        item.find(".openthread").fadeIn(200);
      },
    });
  });

  $("button.openthread").click(function(){
    var topicID = $(this).parents(".topicitem").attr("topic-id");
    var data = new Object({ topicID: topicID });
    var json = $.toJSON(data);

    $.ajax({
      url: "/openthread",
      data: json,
      error: handleAjaxErrorBy( alertGlobal ),
      success: function(response){
        topicID = response.openedID;
        var item = $(".topicitem[topic-id=\"" + topicID + "\"]");
        item.removeClass("topicclosed");
        item.find(".openthread").fadeOut(0);
        item.find(".closethread").fadeIn(200);
      },
    });
  });

});
