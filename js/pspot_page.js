// Handling the pspot.html page

var PspotPage = function(pspot_files) {

	up = urlParams();

	this.library = up.lib;
	this.element = up.el;

	// References to important select elements
	this.ptype = $('#plot_type_select');
	this.pdata = $('#plot_data_select');
	this.lchos = $('#lib_choose_select');

	// Now fill the latter with the correct values
	// Start with the current one
	this.lchos.empty();
	for (lib in pspot_files[this.element]) {
		this.lchos.append($('<option>').attr('value', lib).text(lib));
	}
	this.lchos.val(this.library);

	this.update_pspot = function() {

		this.library = this.lchos.val();

		// Assign title
		$('title').html("Pseudopotential: " + this.element + " - " + this.library);

		// Now start changing elements as required
		// Grab the required pseudopotential info from the Session Storage, parsing back JSON into an Object
		this.pspot = pspot_files[this.element][this.library];

		$('.info_name').html(this.pspot.library);
		$('.info_element').html(this.pspot.ELEMENT);
		$('#pspot_line').html(this.pspot.pspot_string);

		$('#info_ion_charge').html(this.pspot.IONIC_CHARGE);
		$('#info_xc').html(this.pspot.LEVEL_THEORY);
		$('#info_solver').html(this.pspot.SOLVER);

		// Build electronic structure string
		// What's the highest shell?
		var elstruct = this.pspot.ELECTRONIC_STRUCTURE;
		var max_n = parseInt(elstruct[elstruct.length-1].ORBITAL);
		var elstruct_str = "";
		for (var i = 0; i < elstruct.length; ++i) {
			var n = parseInt(elstruct[i].ORBITAL);
			if (n < max_n)
				continue;
			elstruct_str += elstruct[i].ORBITAL;
			// Occupancy
			if (Math.round(elstruct[i].OCCUPATION) == elstruct[i].OCCUPATION) {
				elstruct_str += '[' + elstruct[i].OCCUPATION.toFixed(0) + '],';
			}
			else {
				elstruct_str += '[' + elstruct[i].OCCUPATION.toFixed(2) + '],';
			}
		}
		elstruct_str = elstruct_str.slice(0, elstruct_str.length-1);

		$('#info_elstruct').html(elstruct_str);

		for (cut in this.pspot.CUTOFFS) {
			$('#cut_val_' + cut.toLowerCase()).html(this.pspot.CUTOFFS[cut]);
		}

		// Compile the Beta projectors table
		var btab = $('#beta_proj_table');
		btab.find('tr:not(.tr_header)').remove();
		for (proj in this.pspot.PROJECTORS) {
			var proj_info = this.pspot.PROJECTORS[proj];
			var row = $('<tr>');
			row.append($('<td>').html(proj));
			row.append($('<td>').html(proj_info.L));
			row.append($('<td>').html(proj_info.E));
			row.append($('<td>').html(proj_info.RC));
			row.append($('<td>').html(proj_info.SCHEME));
			row.append($('<td>').html(proj_info.NORM));
			btab.append(row);
		}

		// Now update the links
		dtypes = ['beta', 'econv', 'pwave'];
		for (var i = 0; i < 3; ++i) {
			$('#link_' + dtypes[i]).attr({'href': this.pspot.basepath + "_OTF." + dtypes[i] + ".dat",
								   		  'download': this.pspot.ELEMENT + "_" + this.pspot.library + "." + dtypes[i] + ".dat"});
			$('#link_grace_' + dtypes[i]).attr({'href': this.pspot.basepath + "_OTF." + dtypes[i],
								   		  	    'download': this.pspot.ELEMENT + "_" + this.pspot.library + "." + dtypes[i] + ".agr"});
		}

		$('#link_gnuplot').attr({'href': this.pspot.basepath + ".gp",
								 'download': this.pspot.ELEMENT + "_" + this.pspot.library + ".gp"});	

		// And finish by updating the plots accordingly
		this.update_plots();	
	}

	this.update_plots = function() {

		// For now this functionality is disabled
		//var t = this.ptype.val();

		var t = 'static'; 
		var d = this.pdata.val();

		// So, what are we to visualize?
		switch(t) {
			case 'static':
				// Hide the d3 svg bit
				$('svg.pspot_main_plot').css("display", "none");
				$('img.pspot_main_plot').css("display", "inline");

				$('img.pspot_main_plot').attr("src", this.pspot.basepath + "." + d + ".png");

				break;
			case 'interactive':
				// Hide the jpg one
				$('svg.pspot_main_plot').css("display", "inline");
				$('img.pspot_main_plot').css("display", "none");

				break;
		}
	}

	// jQuery's proxy function allows to control the scope in which the callback is executed
	this.ptype.on('change', $.proxy(function() {this.update_plots();}, this));
	this.pdata.on('change', $.proxy(function() {this.update_plots();}, this));
	this.lchos.on('change', $.proxy(function() {this.update_pspot();}, this));

	this.update_pspot();
}