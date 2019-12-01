
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
        var media= $("#mid").html() 
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "content":content,
                "media":[media]
            }),
            dataType: "json",
            url: "/additem",
            success: function(response){
                if(response.status=="OK"){
                    //window.location.replace("/")
                    console.log("Added");
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
                "following":follow,
                'rank':'time'
            }),
            dataType: "json",
            url: "/search",
            success: function(response){
                //showResults(response.items);
                console.log(response);
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
    $("#test").bind("click",function(e){
        console.log("liking...");
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "like":true
            }),
            dataType: "json",
            url: "/item/LZX2GpAEQt1575168736.0/like",
            success: function(response){
                console.log(response)
            },
            error: function(e){
                console.log("Error: "+e);
            }
        });
    });
    $("#mediaSubmit").click(function (event) {

        //stop submit the form, we will post it manually.
        event.preventDefault();

        // Get form
        var form = $('#mediaform')[0];

		// Create an FormData object 
        var data = new FormData(form);

		// If you want to add an extra field for the FormData
        //data.append("CustomField", "This is some extra data, testing");

		// disabled the submit button
        $("#mediaSubmit").prop("disabled", true);

        $.ajax({
            type: "POST",
            enctype: 'multipart/form-data',
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            url: "/addmedia",
            success: function (data) {

                //$("#result").text(data);
                console.log("SUCCESS : ", data);
                $("#mediaSubmit").prop("disabled", false);
                $("#mid").html(data.id)

            },
            error: function (e) {

                $("#result").text(e.responseText);
                console.log("ERROR : ", e);
                $("#mediaSubmit").prop("disabled", false);

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

