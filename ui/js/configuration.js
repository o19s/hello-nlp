$(document).ready(function(){

    // ------------------------------------------------

    $.get('/environment',function(res,status) {
        environment = $("#environment");
        if (status=="success") {
            environment.text(JSON.stringify(res,null,2))

        }
    });

    $.get('/pipeline',function(res,status) {
        pipeline = $("#pipeline");
        if (status=="success") {
            pipeline.text(JSON.stringify(res,null,2))

        }
    });

    // ------------------------------------------------


});