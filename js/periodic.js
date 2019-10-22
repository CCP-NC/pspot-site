function initPeriodicTable(el) {
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
                    var group_col = {
                        'actinoid': ['#77ffbb', '#55ee99'],
                        'alkali metal': ['#ddaa88', '#774422'],
                        'alkaline earth metal':  ['#ddaa00', '#774400'],
                        'halogen': ['#aaffcc', '#00ff44'],
                        'lanthanoid': ['#66ffaa', '#33cc77'],
                        'metal': ['#aaaadd', '#6666aa'],
                        'metalloid': ['#ffaadd', '#cc88bb'],
                        'noble gas': ['#eeeeff', '#ccccff'],
                        'nonmetal': ['#dd88ff', '#bb33cc'],
                        'transition metal': ['#ddddff', '#9999dd']};

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
    });
}