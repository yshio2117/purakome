$( function() {
    var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    $('body').html($('body').html().replace(exp, "<a href='$1' target='_blank rel='nofollow noopener'>$1</a>"));
} );