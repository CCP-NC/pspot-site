function initPseudopotentialGraph(el) {
    $.when(
        $.getJSON("pspot_data.json", function(data) {
            pspot_files = data;
            console.log("Pseudopotential file list loaded");      
        }),
        $.getJSON("data/periodic_table/data_tabulated.json", function(data) {
            periodic_table = {}
            for (var i = 0; i < data.length; ++i) {
                periodic_table[data[i].symbol] = data[i];
            }
            console.log("Periodic table data loaded");                 
        })
    ).then(function() {

        // Grab the parameters from the URL
        urlpars = urlParams();

        var app = new Vue({
            el: el,
            data: {
                pspot: pspot_files[urlpars.el],
                element: periodic_table[urlpars.el],
                library: urlpars.lib,
                active_plot: 'econv',
            },
            methods: {
                elecStructure: function() {
                    var elstruct = this.pspot[this.library].electronic_structure;

                    var elstr = ''
                    for (var i = 0; i < elstruct.length; ++i) {
                        elstr += elstruct[i].orbital;
                        elstr += '<sub>' + elstruct[i].occupancy.toString() + '</sub>';
                    }

                    return elstr;
                }, 

                getProjLegendCol: function(i) {
                    var pdef = this.pspot[this.library].pseudopotential_definition;

                    var l = pdef[i].l;
                    var lc = 0;

                    for (var j = 0; j <= i; ++j) {
                        if (pdef[j].l == l) {                           
                            lc += 1;
                        }
                    }

                    return lc;
                }
            }
        });
    });
}