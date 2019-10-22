
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
});