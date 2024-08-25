
jQuery(document).ready(function ($) {
    const contentData = JSON.parse($('#content-edit-location').val());
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

    $(document).on('input', '#elementForm input', function () {

    });
});
