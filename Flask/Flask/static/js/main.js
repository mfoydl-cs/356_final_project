
$(document).ready(function() {
    $("#tweet_text").keyup(function(){
        $("#count").text("Chars Left: " + (200 -$(this).val().length));
    });
    $("#tweet_text").ready(function(){
        $("#count").text("Chars Left: " + (200 -$(this).val().length));
    });


    $('.button-like').bind('click', function(e) {
            $(e.target).toggleClass("liked");
    });
    $('.heart').bind('click', function(e) {
        $(e.target.parentElement).toggleClass("liked");
    });

    $('.button-repost').bind('click', function(e){
        $(e.target).toggleClass("repost");
        $(e.target.parentElement).toggleClass("repost");
        $(e.target.childElement).toggleClass("repost");
    });
    $("#post").bind("click",function(e){
        console.log("posting...");
        var content= $("#post_text").val(); 
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "content":content
            }),
            dataType: "json",
            url: "/additem",
            success: function(response){
                if(response.status=="OK"){
                    window.location.replace("/")
                    console.log("Added");
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
    $("#logout").bind("click",function(e){
        console.log("posting...");
        var content= $("#post_text").val(); 
        $.ajax({
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            url: "/logout",
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
    $(".post").bind("click",function(e){
        
        var id =$(this).find("._id").html();
        console.log(id);
        $.ajax({
            type: "GET",
            contentType: "application/json",
            dataType: "json",
            url: "/item/"+id,
            success: function(response){
                if(response.status=="OK"){
                    console.log(response);
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
    $('#search').bind('click',function(e){
        console.log("SEARCH");
        var q = $("#searchbar").val();
        console.log(q);
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "q":q
            }),
            dataType: "json",
            url: "/search",
            success: function(response){
                if(response.status=="OK"){
                    //window.location.replace("/")
                    console.log(response);
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
    $("#profile").bind("click",function(e){
	$.ajax({
	    type: "POST",
	    contentType: "application/json",
	    data: JSON.stringify({
	      "username":"m",
	      "follow":true
	    }),
	    dataType: "json",
            url: "/follow",
            success: function(response){
                if(response.status=="OK"){
                    //window.location.replace("/")
                    console.log(response);
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
