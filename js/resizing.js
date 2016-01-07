function resize_all() {

    function fit2width(el, frac) {
        // Fit a group of elements' font size to the maximum width of the text
        // (the element must contain a span)
        var max_w = 0;
        $(el).each(function(i, el) {
            el_w = $(el).find("span").width();
            if (el_w > max_w) {
                max_w = el_w;
            }
        });
        $(el).css("font-size", parseFloat($(el).css("font-size"))*($(el).width()*frac)/max_w);
    }

    // Change sizes of font according to global page size
    var symbol_height_frac = 0.5;
    var elem_text_height_frac = 0.5;

    // Symbols and elements: get the average cell size
    var symbols = $(".elem_symbol");
    symbols.css("font-size", symbols.height()*symbol_height_frac + "pt");
    var names = $(".elem_name");
    //names.css("font-size", names.height()*elem_text_height_frac + "pt");
    fit2width(names, 1.0);
    var nums_weights = $(".elem_number").add(".elem_weight");
    fit2width(nums_weights, 1.0);
    // Now actually use only the smallest one...

}