$(document).ready(function(){
    $("#login").bind("click", function(e){
        var username= $("#username").val(); 
        var password=$("#password").val();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "username":username,
                "password":password
            }),
            dataType: "json",
            success: function(response){
                url: window.location.hostname + "/home"
            },
            error: function(e){
                console.log("Error: "+e);
            }
        });
    });
});