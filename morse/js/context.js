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

function createPostReference (owner, postID){
  var refString = owner.attr("references");
  var refArray = refString.split(" ");
  refArray.push(postID);
  refArray = $.unique(refArray);
  refString = refArray.join(" ");
  owner.attr("references", refString);
}

function getPostReferences (owner){
  var refString = owner.attr("references");
  var refArray_strings = refString.split(" ");
  var refArray = []
  $.each(refArray, function(index, element){
    var ID = parseInt(element);
    refArray.push(ID);
  });
  return refArray;
}

function fetchContext (postID, callback){
  $.ajax({
    url: "/post/" + postID  + "/full-context.json",
    error: handleAjaxErrorBy( alertGlobal ),
    type: 'GET',
    success: callback,
  });
}
