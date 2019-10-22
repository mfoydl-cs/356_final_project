$(document).ready(function(){
    console.log(window.location.href)
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
            url: "/adduser",
            success: function(response){
                if(response.status=="OK"){
                    window.location.replace("/unverified")
                }
                else{
                    console.log(response);
                }
            },
            error: function(e){
                console.log("Error: "+e);
            }
        });
    });
});