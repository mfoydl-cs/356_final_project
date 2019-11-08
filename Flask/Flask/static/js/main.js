
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
    $(".user").bind("click",function(e){
        console.log("user");
        var user =$(this).html();
        user = user.replace("@","");
        console.log(user);
        window.location.replace("/user/"+user+"/show");
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
    /*
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
    */
    $('#search').bind('click',function(e){
        console.log("SEARCH");
        var q = $("#searchbar").val();
        var user = $('#searchbar2').val();
        var follow = $("#following").prop('checked');
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "q":q,
                "username":user,
                "following":follow
            }),
            dataType: "json",
            url: "/search",
            success: function(response){
                showResults(response.items);
                //console.log(response);
                //window.location.replace("/search/"+response.items);
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
            dataType: "json",
            url: "/getuser",
            success: function(response){
                username= response.user;
                window.location.replace("/user/"+username+"/show");
                console.log(response);
            },
            error: function(e){
                console.log("Error: "+e);
            }
        });
    });
});

function showResults(r){
    var posts = "";
    for(var i=0; i<r.length;i++){
        posts+=createPost(r[i]);
    }
    $("#feed").html(posts);
}
function createPost(item){
    var html=   `<div class="post container">
                    <span hidden class="_id">${item['id']}</span>
                    <div class="post_head">
                        <span style="color:darkgray"></span>
                        <br>
                        <span style="font-weight: bold">@${item['username']}</span>
                    </div>
                    <div class="post_body">
                        <p>${item['content']}</p>
                    </div>
                    <div class="post_footer">
                        <div><button class="button button-post button-comment" ><div class="comment"></div></button></div>
                        <div><button class="button button-post button-repost"><span>&#x21ba;</span></button></div>
                        <div><button class="button button-post button-like"><span class="heart"></span></button></div>
                    </div>
                </div>`
    return html;
}

