$(document).ready(function(){
    $("#create").bind("click", function(e){
        var username= $("#username").val(); 
        var email= $("#email").val();
        var password=$("#password").val();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "username":username,
                "email":email,
                "password":password
            }),
            dataType: "json",
            success: function(response){
                url: window.location.hostname + "/unverified"
            },
            error: function(e){
                console.log("Error: "+e);
            }
        });
    });
});