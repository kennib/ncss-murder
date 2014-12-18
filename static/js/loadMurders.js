function loadMurders(game_id, cb) {
	var req = new XMLHttpRequest();
	req.onload = function() {
		var murders = JSON.parse(this.responseText);
		cb(murders);
	};
	req.open("get", "/murder?game="+game_id, true);
	req.send();
};
