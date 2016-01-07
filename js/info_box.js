InfoBox = function() {
    // Initializes the info box control

    this.ibox = $(".info_box");

    this.showElement = function(el) {

        // Assign the various contents
        this.ibox.css("border-color", "#"+el.cpkHexColor);
        this.ibox.find('.info_name').html(el.name);
        this.ibox.find('.info_symbol').html(el.symbol);
        this.ibox.find('.info_group').html(el.groupBlock);
        this.ibox.find('.info_elstate').html(el.electronicConfiguration);
        this.ibox.find('.info_bond').html(el.bondingType);

        // Now check if there are any pseudopotentials
        if (el.symbol in pspot_files) {

            var pspot_page_link = $("<a>").attr("href", "pspot.html?=" + pspot_files[el.symbol].default.file)
                                          .html(pspot_files[el.symbol].default.file);
            this.ibox.find('.info_pspot_default').html('').append(pspot_page_link);

            this.ibox.find('.info_nopspot').css("display", "none");
            this.ibox.find('.info_pspot').css("display", "block");
            this.ibox.find('.pspot_list_show').on('click', function() {ppList.compile(el.symbol); ppList.show();});
        }
        else {
            this.ibox.find('.info_nopspot').css("display", "block");
            this.ibox.find('.info_pspot').css("display", "none");
        }

    }

}