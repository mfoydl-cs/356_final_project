$(document).ready(function(){
    console.log(window.location.href)
    $("#register").bind("click", function(e){
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
                    //window.location.replace("/unverified")
                    console.log(response)
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
    $("#login").bind("click", function(e){
        var username= $("#lusername").val(); 
        var password=$("#lpassword").val();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "username":username,
                "password":password
            }),
            dataType: "json",
            url: "/login",
            success: function(response){
                if(response.status=="OK"){
                    window.location.replace("/")
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
    $("#verify").bind("click", function(e){
        var key= $("#key").val(); 
        var email= $("#vemail").val();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "email":email,
                "key":key
            }),
            dataType: "json",
            url: "/verify",
            success: function(response){
                if(response.status=="OK"){
                    //window.location.replace("/");
                    console.log(response)
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