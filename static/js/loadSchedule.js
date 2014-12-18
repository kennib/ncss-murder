function loadSchedule(game_id, cb) {
	var req = new XMLHttpRequest();
	req.onload = function() {
		var schedule = JSON.parse(this.responseText);
		cb(schedule);
	};
	req.open("get", "/static/data/schedule-2015.json", true);
	req.send();
};
