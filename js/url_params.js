function urlParams() {
	// Get the URL parameters in object form

	params = {};

	param_string = window.location.search.substring(1); // Remove the question mark
	param_list = param_string.split('&');

	var param_re = /([^=]+)=([^=]+)/;
	for (var i = 0; i < param_list.length; ++i) {
		if (param_re.test(param_list[i])) {
			var m = param_re.exec(param_list[i]);
			params[m[1]] = m[2];
		}
	}

	return params;
}