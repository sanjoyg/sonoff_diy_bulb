current_port=8081
$(function(){
  $(".power").click(function() {
    //$("body").toggleClass("active");
    //$("#on_body").attr("fill","#FF0000");
    //console.log("got here....")
    //console.log(color_from_rgb(255, 0, 0))
    //call_twin()
  });  
});

$(document).ready(function() {
    console.log(window.location.href);
    current_port=window.location.href.split("/")[2].split(":")[1];
    setInterval(call_twin,10000);
});

function conv_to_hex(num) {
    console.log(num);
    return num.toString(16).padStart(2,0)
}

function make_rgb(rgb_dict) {
    console.log(rgb_dict);
    r_str=conv_to_hex(rgb_dict.r)
    g_str=conv_to_hex(rgb_dict.g)
    b_str=conv_to_hex(rgb_dict.b)
    return "#".concat(r_str).concat(g_str).concat(b_str)
}

function set_state(data) {

    console.log("We are at : " + current_port)
    console.log("http://0.0.0.0:" + current_port + "/zeroconf/info", true);
    if (!data.hasOwnProperty("data")) 
        return;

    data_dict = data.data;

    if (data_dict.hasOwnProperty("switch"))  {
        var is_on = data_dict.switch;
        if (is_on == "on")
            $("body").attr("class","active");
        else 
            $("body").attr("class","");
    }
    
    if (data_dict.hasOwnProperty("ltype"))  {
        var ltype = data_dict.ltype;
        console.log("LTYPE IS : " + ltype);
        if (ltype == "white") {
            $("#mode").text("White")
            $("#on_body").attr("fill","#FFDB55");
        }

        if (ltype == "color")  {
            var color_str = make_rgb(data_dict.color);
            console.log("Color Str: ",color_str);
            $("#mode").text("RGB")
            $("#on_body").attr("fill",color_str);
        }
    }


    if (data_dict.hasOwnProperty("white"))  {
        if (data_dict.white.hasOwnProperty("br")) 
            $("#br").text("BR: " + data_dict.white.br  + "%")
        if (data_dict.white.hasOwnProperty("ct")) 
            $("#ct").text("CT: " + data_dict.white.ct  + "%")
    }

    if (data_dict.hasOwnProperty("color"))  {
        if (data_dict.color.hasOwnProperty("br")) 
            $("#br").text("BR: " + data_dict.color.br  + "%")

        var r,g,b;
        r=g=b="  ";

        if (data_dict.color.hasOwnProperty("r")) 
            r=data_dict.color.r
        if (data_dict.color.hasOwnProperty("g")) 
            g=data_dict.color.g
        if (data_dict.color.hasOwnProperty("b")) 
            b=data_dict.color.b
        $("#rgb").text(r+","+g+","+b)
    }
}

function call_twin() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            console.log("Twin called and returned...");
            var ret=JSON.parse(this.responseText);
            console.log(ret);
            set_state(ret);
         }
    };
    url_to_post="http://0.0.0.0:" + current_port + "/zeroconf/info"
    //xhttp.open("POST", "http://0.0.0.0:8081/zeroconf/info", true);
    //xhttp.open("POST", url_to_post, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send('{"deviceid" : "test" }')
}
