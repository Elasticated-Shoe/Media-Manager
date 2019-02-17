function fetchBlock(row) {
    $.get("?Action=fetchMeta&Row=" + row, function(data) {
        console.log(data);
    });
}

function TEMP_fetchAll() {
    $.get("?Action=fetchMeta", function(data) {
        console.log(data);
    });
}

function renderTemplate(data, template) {
    var template = $('#' + template).html();
    var rendered = Mustache.render(template, {name: "Luke"});
    $('#target').html(rendered);
}

var render = (function() {
    var init = function() {
        console.log("init")
    }
    return {
        init: init
    };
})();

function defer(method) {
    if (window.jQuery) {
        method();
    } else {
        setTimeout(function() { defer(method) }, 10);
    }
}

// script load is async, wait for jquery
defer(function() {
    $(document).ready(function(){
        $(document).foundation() // initialize foundation framework
        render.init();
        /*
        Mustache.parse(template);   // speed up use of mustache.js templates
        var allFilmData = TEMP_fetchAll();
        renderTemplate(allFilmData)*/
    });
});
