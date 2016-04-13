$(document).ready(function() {
    console.log("Dashboard loaded!");
    $btn = $("#create");
    $id = $("#id");
    $lat = $("#lat");
    $lon = $("#lon");
    $ele = $("#ele");
    $trace = $("#trace");
    $track = $("#track");
    btn_listner();
});

function btn_listner() {
    $btn.click(function() {
        console.log("Button clicked!");
        console.log($id.val());
        console.log($lat.val());
        console.log($lon.val());
        console.log($trace.val());
        console.log($track.val());
        query = "?id="+$id.val()+"&lat="+$lat.val()+"&lon="+$lon.val()+"&ele="
                +$ele.val()+"&trace="+$trace.val()+"&track="+$track.val();
        $.get(window.location.href + query, function(response) {
            console.log(response);
            if (response != "Error") {
                window.location.href = window.location.href + response + "/";
            }
        });
    });
};
