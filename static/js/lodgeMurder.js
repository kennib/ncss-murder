window.addEventListener('load', function() {

  var sel_victim = document.getElementById('sel_victim');
  var sel_murderer = document.getElementById('sel_murderer');

  /**
   * @param {!HTMLSelectElement} select to select on
   * @param {number} self ID of self
   * @param {number} direction to search, +ve or -ve
   */
  function selectNearest(select, self, direction) {
    if (!direction) {
      throw new Error('must specify +ve or -ve direction');
    }
    direction = direction > 0 ? 1 : -1;

    var all = {};
    var max = 0;
    for (var i = 0, opt; opt = select.options[i]; ++i) {
      all[+opt.value] = true;
      max = Math.max(max, +opt.value);
    }

    var target = self;
    for (;;) {
      target += direction;
      if (all[target]) {
        select.value = target;
        return true;
      }

      if (target <= 0 || target > max) {
        break;
      }
    }

    return false; // not valid
  }

  sel_victim.addEventListener('change', function() {
    if (sel_murderer.value) {
      return;  // ignore, something already chosen
    }
    selectNearest(sel_murderer, +sel_victim.value, -1)  // go back
  });

  sel_murderer.addEventListener('change', function() {
    if (sel_victim.value) {
      return;  // ignore, something already chosen
    }
    selectNearest(sel_victim, +sel_murderer.value, +1)  // go forward
  });

});