// A convenient way of generating transform strings for SVG elements

var _ = new function() {

    var translate = function(x, y) {
        x = x || 0;
        y = y || 0;
        this.transform_string += "translate(" + x + " " + y + ") ";
        return this;
    }

    var rotate = function(a, x, y) {
        a = a || 0;
        x = x || 0;
        y = y || 0;
        this.transform_string += "rotate(" + a + " " + x + " " + y + ") ";
        return this;
    }

    var scale = function(x, y) {
        x = x || 1;
        y = y || x;
        this.transform_string += "scale(" + x + " " + y + ") ";
        return this;
    }

    var skewX = function(x) {
        x = x || 0;
        this.transform_string += "skewX(" + x + ") ";
        return this;
    }

    var skewY = function(y) {
        y = y || 0;
        this.transform_string += "skewY(" + y + ") ";
        return this;
    }

    var svgTransform = function() {
        this.transform_string = "";
        this.translate = translate;
        this.rotate = rotate;
        this.scale = scale;
        this.skewX = skewX;
        this.skewY = skewY;
    }

    svgTransform.prototype.toString = function() { 
        return this.transform_string; 
    }

    this.translate = function(x, y) {
        return (new svgTransform()).translate(x, y);
    }

    this.rotate = function(a, x, y) {
        return (new svgTransform()).rotate(a, x, y);
    }

    this.scale = function(x, y) {
        return (new svgTransform()).scale(x, y);
    }

    this.skewX = function(x) {
        return (new svgTransform()).skewX(x);
    }

    this.skewY = function(y) {
        return (new svgTransform()).skewY(y);
    }

}