//----------------------------------------------------------
//Gets the querystring value for the specified key
$.querystring = (function(key,url){
    url = url || window.location.search;
    key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]"); 
    var regex = new RegExp("[\\?&]"+key+"=([^&#]*)"); 
    var results = regex.exec( url );
    return (!results)?"":decodeURIComponent(results[1].replace(/\+/g, " "));
}).bind($);

//----------------------------------------------------------

var analyze = function(text,analyzer) {
    uri = '/analyze/' + analyzer + '?debug=true&text=' + encodeURI(text);
    var ajaxTime= (new Date()) - 0;
    var data = $("#data");
    var debug = $("#debug");        
    $.get(uri,function(res,status) {
        var totalTime = (new Date())-ajaxTime;
        if (status=="success") {
            data.text(res.data)
            for(var i=0;i<res.debug.length;i++) {
                $(`<tr>
                    <td>${res.debug[i].name}</td>
                    <td>${res.debug[i].time}</td>
                    <td>${res.debug[i].debug}</td>
                    </tr>`).appendTo(debug)
            }
            $(`<tr>
                <td>Round Trip:</td>
                <td><strong>${totalTime}</strong></td>
                <td><em>NOTE!  Round trip time includes debug overhead.  "(end)" time measures pure analysis time.</em></td>
                </tr>`).appendTo(debug)

        }
    });
}

//----------------------------------------------------------

$(document).ready(function(){

    var select = $("#analyzer");
    var textbox = $("#text");

    text = $.querystring("text")
    analyzer = $.querystring("analyzer")

    if(text && analyzer) {
        analyze(text,analyzer)
        textbox.val(text)
    }

    // ------------------------------------------------

    $.get('/analyzers',function(res,status) {
        console.log(status)
        if (status=="success") {
            for(var i=0;i<res.data.length;i++) {
                name = res.data[i]
                option = $("<option value=\""+name+"\">"+name+"</option>");
                select.append(option)
            }            
            if (analyzer) select.val(analyzer);
        }
    });

    // ------------------------------------------------

});