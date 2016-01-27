// Loading the periodic table JSON data

var ElemTable = function(selector, width, height) {

    this.table = d3.select(selector);
    // Does it exist?
    if (this.table[0][0] == null) {
        return;
    }
    this.table.classed('table', true);

    function arrayRange(n) {
        ans = new Array(n);
        for (i = 0; i < n; ++i)
            ans[i] = i;
        return ans;
    }

    this.width = width;
    this.height = height;

    // First clear
    this.table.selectAll('*').remove();
    // Insert rows and columns as required
    this.table.selectAll('.row')
        .data(arrayRange(this.height))
        .enter()
        .append('div')
        .attr('id', function(i) {return "tr" + i;})
        .classed('row', true)
        .selectAll('.cell')
        .data(arrayRange(this.width))
        .enter()
        .append('div')
        .attr('id', function(i) {return "tc" + i;})
        .classed('cell', true);


    this.getElem = function(x, y) {
        return this.table.select('#tr' + y).select('#tc' + x);
    }

    this.fillData = function(data, getCoords, makeElem) {

        for (var i = 0; i < data.length; ++i) {
            var xy = getCoords(data[i]);
            if (xy == null)
                continue;
            var elem = this.getElem(xy[0], xy[1]);
            makeElem(elem, data[i]);
        }

    }

}

// Main Mendelev table
var MendvTable = function(periodic_data, ibox) {

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


    this.getCoordsMendv = function(d) {
        if (d.subTable != "Main")
            return null;
        return [d.colI, d.rowI];
    }

    this.getCoordsLantAct = function(d) {
        if (d.subTable != "LantAct")
            return null;
        return [d.colI, d.rowI];
    }

    this.makeElemMendv = function(e, d) {
        var main_div = e.style('background-color', group_col[d.groupBlock])
                        .append('div')
                        .classed('elem_mendv', true);
        main_div.append('div')
                .classed('elem_symbol', true)
                .append("span")
                .html(d.symbol);
        main_div.append('div')
                .classed('elem_name', true)
                .append("span")
                .html(d.name);        
        main_div.append('div')
                .classed('elem_number', true)
                .append("span")
                .html(d.atomicNumber);
        main_div.append('div')
                .classed('elem_weight', true)
                .append("span")
                .html(parseFloat(d.atomicMass).toFixed(2));
        // Now bind the clicking event with a closure
        main_div.on("click", function(ibox, d) {
            return function() {
                ibox.showElement(d);
            };
        }(ibox, d));
    }

    this.periodic = periodic_data

    this.eT = new ElemTable(".periodic_table", 18, 7);
    this.eT.fillData(this.periodic, this.getCoordsMendv, this.makeElemMendv);            
    this.laT = new ElemTable(".lantact_table", 13, 2);
    this.laT.fillData(this.periodic, this.getCoordsLantAct, this.makeElemMendv);

    ibox.showElement(this.periodic[0]); // Initialize with hydrogen
}