function windowInit() {
    if ($("body").prop('scrollHeight') > $("body").height()) {
        $("#scroll_to_top").show()
    } else {
        $("#scroll_to_top").hide()
    }
};
$(document).ready(function() {
    windowInit();
    $("#scroll_to_top").click(function() {
        $("html").animate({
            scrollTop: 0
        }, 500)
    });
    $('[data-toggle="tooltip"]').tooltip();

    $(".show_pass_js").click(function(){
        var selected_input = $(this).closest(".input-group").find("input");
        
        if (selected_input.attr("type") == 'password') {
            $(this).find("i").removeClass("fa-eye");
            $(this).find("i").addClass("fa-eye-slash");
            selected_input.attr("type", "text");
        }
        else{
            $(this).find("i").removeClass("fa-eye-slash");
            $(this).find("i").addClass("fa-eye");
            selected_input.attr("type", "password");
        }
    });

    $(".copy_append_js").each(function (i, e) {
        $(this).click(function (e) {
            e.preventDefault();

            if($(this).data("target") == 'self'){
                var $temp = $("<input>");
                $("body").append($temp);
                $temp.val($(this).html()).select();
                document.execCommand("copy");
                $temp.remove();
            }
            else{
                $($(this).data("target")).select();
                document.execCommand("copy");
                $($(this).data("target")).blur()
            }

            var copy_toast = VanillaToasts.create({
                title: 'Successfully copied!',
                text: 'Successfully copied!',
                type: 'success', // success, info, warning, error   / optional parameter
                timeout: 1000 // hide after 5000ms, // optional parameter
            });
        });
    });
});
$(window).resize(function() {
    windowInit()
});
$('#theme').click(function() {
    if ($('#theme-icon').hasClass('fas')) {
        axios('/api/themes/set/dark', {
            method: 'PUT'
        }).then(done).catch(error)
    } else {
        axios('/api/themes/set/light', {
            method: 'PUT'
        }).then(done).catch(error)
    }
});

function done(res) {
    if (res.data.error) {
        throw res.data.error
    }
    $(this).toggleClass('far').toggleClass('fas');
    window.location.reload()
};

function error(error) {
    VanillaToasts.create({
        type: 'error',
        title: 'Error!',
        text: error,
        timeout: 3000
    })
};