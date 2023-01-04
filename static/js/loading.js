$('head').append(
            '<style type="text/css">#container2 { display: none; } #fade, #loader { display: block; }</style>'
);
jQuery.event.add(window,"load",function() { // 全ての読み込み完了後に呼ばれる関数
            var pageH = $("#container2").height();
            $("#fade").css("height", pageH).delay(900).fadeOut(800);
            $("#loader").delay(300).fadeOut(150);
            $("#container2").css("display", "block");
});