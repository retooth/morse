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

  checkForUndiscoveredTopics();

  function checkForUndiscoveredTopics (){ 
    $(".board-item").each(function(){
      var boardItem = $(this);
      if (boardItem.attr("board-followed") === "True"){
        var boardID = boardItem.attr("board-id");
        $.ajax({
          url: "/board/" + boardID + "/undiscovered.json",
          error: handleAjaxErrorBy( alertGlobal ),
          type: "GET", 
          success: function(response){
            updateSideCounter(boardItem, response.undiscoveredCount); 
          },
        });
      }
    });   
 
    setTimeout(checkForUndiscoveredTopics, 5000);
  }

  function updateSideCounter (boardItem, count){
    var counter = boardItem.children(".item-side-counter");
    if (parseInt(counter.html()) === count){
      return true;
    }
    counter.html(count);
    counter.fadeIn(500);
  }

});
