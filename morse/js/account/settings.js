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

  $("#bio").keypress(function(){
    $("#updateinfo").fadeIn(400);
  });

  function rebindWebsiteEvents(){

    $(".deletewebsite").off("click");
    //FIXME: delay until remove
    $(".deletewebsite").on("click", function(){
      $(this).parent().slideUp(200).remove();
      beautifyWebsiteList();
    });

    $(".websitewrapper input").off("keypress");
    $(".websitewrapper input").on("keypress", function(){
      $("#updateinfo").fadeIn(400);
    });

  }

  $("#anotherwebsite").click(function(){

    var website = $(".websitewrapper").first().clone();
    website.css("display", "none");
    website.children("input").val("");
    website.children("input").attr("placeholder", "...");
    website.insertBefore($("#anotherwebsitebr"));

    beautifyWebsiteList();

    website.slideDown(200);
    website.children("button").fadeIn(1200);

    /* rebind it (since new .deletewebsite elements were added) */
    rebindWebsiteEvents();
  });

  function beautifyWebsiteList(){

    /* makes website input list look like 
     * a block with round edges */
 
    var lastindex = $(".websitewrapper").length - 1;
    unbeautifyWebsiteList();

    if (lastindex !== 0){
      $(".websitewrapper").each(function (index){
        if (index === 0){
          $(this).addClass("first");
        }
        if (index > 0 && index < lastindex){
          $(this).addClass("middle");
        }
        if (index === lastindex){
          $(this).addClass("last");
        }
      });
    }

  }

  function unbeautifyWebsiteList(){
    $(".websitewrapper").removeClass("first");
    $(".websitewrapper").removeClass("middle");
    $(".websitewrapper").removeClass("last");
  }

  $("#updateinfo").click(function(){

    var bio = $("#bio").val();
    var websites = Array();
    $(".websitewrapper input").each(function (){
      websites.push($(this).val());
    });

    var info = new Object({ bio : bio, websites : websites});

    $(this).addClass("buttonspinner");

    $.ajax({
      url: "/account/update-info",
      data: $.toJSON(info),
      error: handleAjaxErrorBy( alertInfoSettings ),
      complete: function(){ $("#updateinfo").removeClass("buttonspinner"); },
    });

  });


  /* settings (account) --------------------------- */

  $(".accountdetail").keypress(function(){
    // see http://stackoverflow.com/questions/11627531
    $("#chromebugmask").slideDown(800);
    $("#updateaccount").fadeIn(400);
  });

  $("#updateaccount").click(function(){

    $("#newpassword").removeClass("invalid-input");
    $("#newpasswordagain").removeClass("invalid-input");
    $("#oldpassword").removeClass("invalid-input");

    $(this).addClass("buttonspinner");

    var newPassword = $("#newpassword").val();
    var newPasswordAgain = $("#newpasswordagain").val();

    if (newPassword !== newPasswordAgain){
      alertAccountSettings("passwordsdontmatch");
      $("#newpassword").addClass("invalid-input");
      $("#newpasswordagain").addClass("invalid-input");
      $(this).removeClass("buttonspinner");
      return false;
    }

    var oldPassword = $("#oldpassword").val();
    var newEmail = $("#newemail").val();
    /* TODO: convention for json identifiers in pipe main.js <- ajax -> views.py */
    var account = { newemail : newEmail, newpassword : newPassword, oldpassword : oldPassword };

    $.ajax({
      url: "/account/update",
      data: $.toJSON(account),
      error: handleAjaxErrorBy( alertAccountSettings ),
      complete: function(){ 
        $("#updateaccount").removeClass("buttonspinner"); 
      },
    });

  });

});
