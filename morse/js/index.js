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

  $("#top-action").mouseenter(function(){

    /* block if divs are still in motion */
    var currentTop = parseInt($("#index-header").css("top"));
    if (currentTop > 0) { return true; }

    var height = $("#top-action a").height();
    var timer = setTimeout(function(){
      $("#index-header").animate( { top : height + "px" }, {duration: 500 });
      $("#index").animate( { top : height + "px" }, {duration: 500, complete: fadeInTopActionInfo });
    }, 400);
    $(this).data("toolRevealDelay", timer);

  });  

  function fadeInTopActionInfo (){
    $("#top-action a").fadeIn(200);
  }

  $("#top-action").mouseleave(function(){

    /* clear timer, that was triggered on mousenter */
    var timer = $(this).data("toolRevealDelay");
    clearTimeout(timer);

    fadeOutTopActionInfo();
    $("#index-header").animate( { top : "0" }, {duration: 500});
    $("#index").animate( { top : "0" }, {duration: 500});

  });  

  function fadeOutTopActionInfo (){
    $("#top-action a").fadeOut(200);
  }

  if ($("#snap-tooltip-top").length > 0){
    $("#index-header").swipeSnap( { target: "top", snapInfo: $("#snap-tooltip-top"), 
                                   companions: [$("index")], 
                                   callback: gotoLogOut });
  }

  function gotoLogOut (){
    window.location = "/account/logout";
  }

});
