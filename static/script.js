var canvas = document.getElementById("paint");
var ctx = canvas.getContext("2d");
var width = canvas.width;
var height = canvas.height;
var curX, curY, prevX, prevY;
var hold = false;
var shape = Shape;
ctx.lineWidth = 2;
var test = "#eeFFFF"
var stroke_value = true;
var currentZone = 0
var selectedButton = null
ctx.strokeStyle = "#ee6363";


//drawing the shapes from the database
for (const [ShapesBank,ShapesBankData ] of Object.entries(Shapes)) {
    //console.log(`${ShapesBank}: ${ShapesBankData}`);
    for (const [ShapesZone,ShapesZoneData ] of Object.entries(ShapesBankData)) {
        //console.log(`${ShapesZone}: ${ShapesZoneData}`);
        if (!Object.keys(ShapesZoneData).length == 0){
            console.log(ShapesZoneData["shape"])
            console.log(ShapesZoneData["data"])
            var coordinates = JSON.parse(ShapesZoneData["data"]);
            var prevX = coordinates.x
            var prevY = coordinates.y
            var curX = coordinates.curX
            var curY = coordinates.curY
            if (ShapesZoneData["shape"] == "rect"){
                ctx.strokeRect(prevX, prevY, curX, curY);
                ctx.fillText(ShapesBank.concat(" ", ShapesZone), prevX+3, prevY-3);
            }else if (ShapesZoneData["shape"] == "circle"){
                ctx.beginPath();
                ctx.arc(Math.abs(curX + prevX)/2, Math.abs(curY + prevY)/2, Math.sqrt(Math.pow(curX - prevX, 2) + Math.pow(curY - prevY, 2))/2, 0, Math.PI * 2, true);
                ctx.closePath();
                ctx.stroke();
                ctx.fillText(ShapesBank.concat(" ", ShapesZone), prevX+3, prevY-3);
            }
        }
    }
}


function resetAllShapes(){
    if (confirm("This will delete all your zones!\nAre you sure?")) {
        $.post("/resetAllShapes");
        window.setTimeout(reloadPage, 10);
    }
}
function resetShape(){
    if (!selectedButton) {
        return
    }
    console.log(selectedButton);
    var bank = String(selectedButton.match(/Bank\d+/));
    var zone = String(selectedButton.match(/Zone\d+/));
    $.ajax({
      type: "POST",
      url: "/resetShape",
      data:  JSON.stringify({"bank": bank,
                            data: {
                            "zone": zone,
                            data: {}}}),
        contentType: "application/json; charset=utf-8"
      });
      window.setTimeout(reloadPage, 10);
}

$("#"+ shape).addClass('active');
function setShapeRect(id){
        shape = "rect";
        $("#"+ id).addClass('active');
        $("#circle").removeClass('active');
        $.post("/setShape","rect");
        if (!currentZone == 0){
            rectangle(currentZone);
        }
}
function setShapeCircle(id){
        shape = "circle";
        $("#"+ id).addClass('active');
        $("#rect").removeClass('active');
        $.post("/setShape","circle");
        if (!currentZone == 0){
            circle(currentZone);
        }
}
function draw(id){
    if (selectedButton) {
        $("#"+selectedButton).removeClass('active');
    }
    selectedButton = id;
    $("#"+ id).addClass('active');


    if (shape == "circle"){
        circle(id);
    }else{
        rectangle(id);
    }
}

function reloadPage(){
    location.reload();
}

function rectangle(id){
    currentZone = id
    var scaleX = width/canvas.getBoundingClientRect().width
    var scaleY = height/canvas.getBoundingClientRect().height

    canvas.onmousedown = function (e){
        var bounds = canvas.getBoundingClientRect();
        img = ctx.getImageData(0, 0, width, height);
        prevX= parseInt(e.clientX - bounds.left + (bounds.left - canvas.getBoundingClientRect().left))*scaleX;
        prevY= parseInt(e.clientY - bounds.top + (bounds.top - canvas.getBoundingClientRect().top))*scaleY;
        hold = true;
    };

    canvas.onmousemove = function (e){
        console.log(canvas.getBoundingClientRect().width)
        if (hold){
            ctx.putImageData(img, 0, 0);
            var bounds = canvas.getBoundingClientRect();
            curX = parseInt(e.clientX - bounds.left + (bounds.left - canvas.getBoundingClientRect().left))*scaleX - prevX;
            curY = parseInt(e.clientY - bounds.top + (bounds.top - canvas.getBoundingClientRect().top))*scaleY - prevY;
            ctx.strokeRect(prevX, prevY, curX, curY);
        }
    };

    canvas.onmouseup = function(e){
        hold = false;
        var bank = String(id.match(/Bank\d+/));
        var zone = String(id.match(/Zone\d+/));

        $.ajax({
          type: "POST",
          url: "/submitShape",
          data:  JSON.stringify({"bank": bank,
                                data: {
                                "zone": zone,
                                data: {"shape":"rect", "data":{"x":prevX,"y":prevY,"curX":curX,"curY":curY}}}}),
          contentType: "application/json; charset=utf-8"
        });
        window.setTimeout(reloadPage, 10);
        //location.reload();
    };

    canvas.onmouseout = function(e){
        //hold = false;
    };
}

// circle tool

function circle(id){
    currentZone = id
    var scaleX = width/canvas.getBoundingClientRect().width
    var scaleY = height/canvas.getBoundingClientRect().height
    canvas.onmousedown = function (e){
        var bounds = canvas.getBoundingClientRect();
        img = ctx.getImageData(0, 0, width, height);
        prevX= parseInt(e.clientX - bounds.left + (bounds.left - canvas.getBoundingClientRect().left))*scaleX;
        prevY= parseInt(e.clientY - bounds.top + (bounds.top - canvas.getBoundingClientRect().top))*scaleY;
        hold = true;
    };

    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            var bounds = canvas.getBoundingClientRect();
            curX = parseInt(e.clientX - bounds.left + (bounds.left - canvas.getBoundingClientRect().left))*scaleX;
            curY = parseInt(e.clientY - bounds.top + (bounds.top - canvas.getBoundingClientRect().top))*scaleY;
            ctx.beginPath();
            ctx.arc(Math.abs(curX + prevX)/2, Math.abs(curY + prevY)/2, Math.sqrt(Math.pow(curX - prevX, 2) + Math.pow(curY - prevY, 2))/2, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.stroke();
        }
    };

    canvas.onmouseup = function (e){
        hold = false;
        console.log(id);
        var bank = String(id.match(/Bank\d+/));
        var zone = String(id.match(/Zone\d+/));

        $.ajax({
          type: "POST",
          url: "/submitShape",
          data:  JSON.stringify({"bank": bank,
                                data: {
                                "zone": zone,
                                data: {"shape":"circle", "data":{"x":prevX,"y":prevY,"curX":curX,"curY":curY,"radius":curX-prevX}}}}),
          contentType: "application/json; charset=utf-8"
        });
        window.setTimeout(reloadPage, 10);
    };

    canvas.onmouseout = function (e){
        hold = false;
    };
}
