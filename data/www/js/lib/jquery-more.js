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

        $.fn.serializeObject = function() {
            const obj = {};

            this.find('input, select, textarea').each(function() {
                const field = $(this);
                const name = field.attr('name');

                if (!name) return; // Ignore fields without a name

                if (field.is(':checkbox')) {
                    const isOnOff = field.val() === 'on' || field.val() === '1';
                    obj[name] = field.is(':checked') ? field.val() : (isOnOff ? false : null);
                } else if (field.is(':radio')) {
                    if (field.is(':checked')) {
                        obj[name] = field.val();
                    } else if (!(name in obj)) {
                        obj[name] = false;
                    }
                } else {
                    const tryInt = parseInt(field.val());
                    obj[name] = isNaN(tryInt) ? field.val() : tryInt;
                }
            });

            return obj;
        };

    });
});
