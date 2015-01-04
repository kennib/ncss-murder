function deleteMurder(game_id, murder_id, cb) {
	var req = new XMLHttpRequest();
	req.onload = function() {
		cb();
	};
	req.open("DELETE", "/murder?game="+game_id+"&murder="+murder_id, true);
	req.send();
};
