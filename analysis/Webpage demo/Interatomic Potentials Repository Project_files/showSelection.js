function showSelection(selectId, divId) {
  var i = document.getElementById(selectId).value;
  var j;
  for (j = 0; j < divId.length; j++) {
    var e = document.getElementById(divId[j]);
    if (i == j) {
      e.style.display = "block";
    } else {
      e.style.display = "none";
    };
  };
};