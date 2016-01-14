// Handling the pspot.html page

var PspotPage = function() {

	up = urlParams();

	this.pspot = up.pspot;
	this.element = up.el;

	// Now start changing elements as required
	// Grab the required pseudopotential info from the Session Storage, parsing back JSON into an Object
	var pspot_info = JSON.parse(window.sessionStorage.getItem("pspot_files"))[this.element][this.pspot];	

	$('.info_name').html(pspot_info.name);
	$('.info_element').html(pspot_info.elem);
	$('#pspot_line').html(pspot_info.ppot_string);

	for (cut in pspot_info.cutoffs) {
		$('#cut_val_' + cut.toLowerCase()).html(pspot_info.cutoffs[cut]);
	}


	this.update_plots = function() {

		var t = this.ptype.val();
		var d = this.pdata.val();

		// So, what are we to visualize?
		switch(t) {
			case 'static':
				// Hide the d3 svg bit
				$('svg.pspot_main_plot').css("display", "none");
				$('img.pspot_main_plot').css("display", "inline");

				$('img.pspot_main_plot').attr("src", "graphs/" + this.pspot + "/" + d + ".jpg");

				break;
			case 'interactive':
				// Hide the jpg one
				$('svg.pspot_main_plot').css("display", "inline");
				$('img.pspot_main_plot').css("display", "none");

				break;
		}
	}

	// Tie the update_plots function to the relevant dropdown menus
	this.ptype = $('#plot_type_select');
	this.pdata = $('#plot_data_select');

	// jQuery's proxy function allows to control the scope in which the callback is executed
	this.ptype.on('change', $.proxy(function() {this.update_plots();}, this));
	this.pdata.on('change', $.proxy(function() {this.update_plots();}, this));

}