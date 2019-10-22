function makeUrl(base_url, params) {
	// Build an URL with the given parameters (passed as JS object)
	var url = base_url;
	if (params != null) {
		url += '?';
		for (p in params) {
			url += p + '=' + params[p] + '&';
		}
		// Remove the last &
		url = url.slice(0, url.length-1);
	}
    return url;
}

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