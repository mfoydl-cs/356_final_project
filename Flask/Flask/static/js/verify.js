$(document).ready(function(){
    console.log(window.location.href)
    $("#submit").bind("click", function(e){
        var key= $("#key").val(); 
        var email= $("#email").val();
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
                    window.location.replace("/");
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