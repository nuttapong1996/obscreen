jQuery(function ($) {

    const main = function () {
        fileUpload();
    };

    const fileUpload = function () {
        $('.btn-super-upload').each(function () {
            const $button = $(this);
            const $input = $(this).find('input[type=file]');
            $input.fileupload({
                url: $(this).attr('data-route'),
                dropZone: $('body'),
                formData: {},
                singleFileUploads: false,
                dataType: 'json',
                add: function (e, data) {
                    const $alert = $('.alert-danger');
                    const $bar = $button.find('.progress-bar');
                    $bar.css('width', '0%');
                    $button.addClass('uploading').removeClass('btn-info btn-super-upload').addClass('btn-naked btn-super-upload-busy');
                    $alert.addClass('hidden').text('');
                    data.submit();
                },
                progressall: function (e, data) {
                    const progress = parseInt(data.loaded / data.total * 100, 10);
                    const $bar = $button.find('.progress-bar');
                    const $percent = $button.find('.percent');
                    $bar.css('width', progress + '%');
                    $percent.text(progress + '%');
                },
                always: function (e, data) {
                    const response = data._response.jqXHR;
                    let statusCode = response.status;
                    $button.removeClass('uploading').removeClass('btn-naked btn-super-upload-busy').addClass('btn-info btn-super-upload');

                    let errorComment = response.responseText.match(/<!--\s*error=(\d+);\s*-->/);
                    if (errorComment && errorComment[1]) {
                        statusCode = parseInt(errorComment[1], 10);
                    }

                    if (statusCode !== 200) {
                        const $alert = $('.alert-upload').removeClass('hidden');
                        if (statusCode === 413) {
                            $alert.html(`<i class="fa fa-warning"></i>${l.js_common_http_error_413}`);
                        } else {
                            $alert.html(`<i class="fa fa-warning"></i>${l.js_common_http_error_occured.replace('%code%', statusCode)}`);
                        }
                    } else {
                        document.location.reload();
                    }
                }
            });
        });
    };

    main();

    $(document).on('click', '.btn-super-upload', function (e) {
        $(this).find('input[type=file]')[0].click();
    });

    $(document).on('dragenter', 'body', function () {
        $(this).addClass('dragenter');
        return false;
    });

    $(document).on('dragover', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
        return false;
    });

    $(document).on('dragleave', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragenter dragover');
        return false;
    });

    $(document).on('drop', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragenter dragover');

        const $dz = $('.dropzone:visible');

        if (isset($dz.attr('data-handle-drop') && $dz.attr('data-handle-drop') === '1')) {
            const $inputTarget = $("#" + $dz.attr('data-related-input'));
            const droppedFiles = e.originalEvent.dataTransfer.files;
            $inputTarget.prop("files", droppedFiles).trigger('change');
        }

        return false;
    });
});

