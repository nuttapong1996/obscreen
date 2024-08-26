
jQuery(document).ready(function ($) {
    const contentData = JSON.parse($('#content-edit-location').val() || '{}');
    const screenRatio = 16/9;

    $('.screen-holder').css({
        'padding-top': ( 1/ ( screenRatio ) * 100) + '%'
    });

    $('.ratio-value').val(screenRatio);

    $('#screen').css({
        width: $('#screen').width(),
        height: $('#screen').height(),
        position: 'relative',
    }).parents('.screen-holder:eq(0)').css({
        width: 'auto',
        'padding-top': '0px'
    });

    const draw = function() {
        const $screen = $('#screen');
        const $text = $('<div class="text">');
        let insideText = $('#elem-text').val();

        if ($('#elem-scroll-enable').is(':checked')) {
            const $wrapper = $('<marquee>');
            $wrapper.attr({
                scrollamount: $('#elem-scroll-speed').val(),
                direction: $('[name=scrollDirection]:checked').val(),
                behavior: 'scroll',
                loop: -1
            });
            $wrapper.append(insideText);
            insideText = $wrapper;
        }

        $text.append(insideText);

        let justifyContent = 'center';
        switch($('[name=textAlign]:checked').val()) {
            case 'left': justifyContent = 'flex-start'; break;
            case 'right': justifyContent = 'flex-end'; break;
        }

        $text.css({
            padding: $('#elem-container-margin').val() + 'px',
            color: $('#elem-fg-color').val(),
            textAlign: $('[name=textAlign]:checked').val(),
            textDecoration: $('#elem-text-underline').is(':checked') ? 'underline' : 'normal',
            fontSize: $('#elem-font-size').val() + 'px',
            fontWeight: $('#elem-font-bold').is(':checked') ? 'bold' : 'normal',
            fontStyle: $('#elem-font-italic').is(':checked') ? 'italic' : 'normal',
            fontFamily: $('#elem-font-family').val() + ", 'Arial', 'sans-serif'",
            whiteSpace: $('#elem-single-line').is(':checked') ? 'nowrap' : 'normal',
            justifyContent: justifyContent
        });

        $screen.css({
             backgroundColor: $('#elem-bg-color').val(),
        });

        $screen.html($text);
    };

    $(document).on('input', '#elementForm input, #elementForm select', function () {
        draw();
    });

    draw();


    $(document).on('submit', 'form.form', function (e) {
        const location = getLocationPayload();
        $('#content-edit-location').val(JSON.stringify(location));
    });
});


const getLocationPayload = function() {
    return $('form#elementForm').serializeObject();
};
