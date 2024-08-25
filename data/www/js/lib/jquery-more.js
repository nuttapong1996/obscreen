jQuery(function () {
    $(document).ready(function () {
        $('.numeric-input').on('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });
})