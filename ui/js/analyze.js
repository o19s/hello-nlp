$(document).ready(function(){

    var form = $("#form");
    var submit = $("#submit");
    var select = $("#analyzers");
    var text = $("#text");
    var data = $("#data");
    var debug = $("#debug");

    $.get('/analyzers',function(res,status) {
        console.log(status)
        if (status=="success") {
            for(var i=0;i<res.data.length;i++) {
                name = res.data[i]
                option = $("<option value=\""+name+"\">"+name+"</option>");
                select.append(option)
            }
        }
    });

    // ------------------------------------------------

    var analyze = function(e) {
        e.preventDefault();
        e.stopPropagation();
        analyzer = select.val();
        text = text.val();
        uri = '/analyze/' + analyzer + '?debug=true&text=' + encodeURI(text);
        var ajaxTime= (new Date()) - 0;
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
                    <td>Total Trip:</td>
                    <td><strong>${totalTime}</strong></td>
                    <td></td>
                    </tr>`).appendTo(debug)

            }
        });
        return false;
    }

    //form.on('submit',analyze)
    submit.on('click',analyze)

    // ------------------------------------------------

});