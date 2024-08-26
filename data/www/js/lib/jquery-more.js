jQuery(function () {
    $(document).ready(function () {
        function adjustValue(inputElement, delta) {
            const currentValue = parseInt(inputElement.value) || 0;
            const newValue = currentValue + delta;
            if (("" + newValue).length <= inputElement.maxLength) {
                inputElement.value = newValue >= 0 ? newValue : 0;
                $(inputElement).trigger('input');
            }
        }

        $('.numeric-input').on('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        $('.numeric-input').on('keydown', function (e) {
            switch (e.key) {
                case 'ArrowUp':
                    e.preventDefault();
                    adjustValue(this, e.shiftKey ? 10 : 1);
                    break;

                case 'ArrowDown':
                    e.preventDefault();
                    adjustValue(this, e.shiftKey ? -10 : -1);
                    break;
            }
        });


        function updateRadioActiveClass() {
            $('.radio-group label').removeClass('active');
            $('input[type="radio"]:checked').next('label').addClass('active');
        }
        updateRadioActiveClass();
        $('.radio-group input[type="radio"]').change(function() {
            updateRadioActiveClass();
        });


        function updateCheckboxActiveClass() {
            $('.checkbox-group label').each(function() {
                const checkbox = $(this).prev('input[type="checkbox"]');
                if (checkbox.is(':checked')) {
                    $(this).addClass('active');
                } else {
                    $(this).removeClass('active');
                }
            });
        }
        updateCheckboxActiveClass();
        $('.checkbox-group input[type="checkbox"]').change(function() {
            updateCheckboxActiveClass();
        });

    });
});
