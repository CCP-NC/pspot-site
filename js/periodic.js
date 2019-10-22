function initPeriodicTable(el) {
    $.when(
        $.getJSON("pspot_data.json", function(data) {
            pspot_files = data;
            console.log("Pseudopotential file list loaded");                 
            console.log(pspot_files);
        }),
        $.getJSON("data/periodic_table/data_tabulated.json", function(data) {
            periodic_table = {}
            for (var i = 0; i < data.length; ++i) {
                periodic_table[data[i].symbol] = data[i];
            }
            console.log("Periodic table data loaded");                 
        })
    ).then(function() {
        var app = new Vue({
            el: el,
            data: {
                ptable: periodic_table,
                pspot: pspot_files,
                selected: 'H',
                show_table: false,
            },
            methods: {
                getGroupColor: function(el) {
                    // Default colors
                    var group_col = {'actinoid': '#55ee99',
                        'alkali metal': '#774422',
                        'alkaline earth metal': '#774400',
                        'halogen': '#00ff44',
                        'lanthanoid': '#33cc77',
                        'metal': '#6666aa',
                        'metalloid': '#cc88bb',
                        'noble gas': '#ddddff',
                        'nonmetal': '#bb33cc',
                        'transition metal': '#9999dd'};
                    return group_col[el.groupBlock];
                },
                getMass: function(el) {
                    return parseFloat(el.atomicMass).toFixed(1);
                },
                select: function(el) {
                    this.selected = el.symbol;
                },
                tableShow: function() {
                    if (this.pspot[this.selected]) {
                        this.show_table = true;
                    }
                },
                tableHide: function() {
                    this.show_table = false;
                }
            }
        });
        console.log(app);
    });
}