jQuery(document).ready(function ($) {
    let currentElement = null;
    let elementCounter = 0;

    $('#screen').css({
        width: $('#screen').width(),
        height: $('#screen').height(),
        position: 'relative',
    }).parents('.screen-holder:eq(0)').css({
        width: 'auto',
        'padding-top': '0px'
    });

    function createElement(config = null) {
        const screen = $('#screen');
        const screenWidth = screen.width();
        const screenHeight = screen.height();

        const elementWidth = config ? (config.widthPercent / 100) * screenWidth : 100;
        const elementHeight = config ? (config.heightPercent / 100) * screenHeight : 50;
        let x = config ? (config.xPercent / 100) * screenWidth : Math.round(Math.random() * (screenWidth - elementWidth));
        let y = config ? (config.yPercent / 100) * screenHeight : Math.round(Math.random() * (screenHeight - elementHeight));
        const zIndex = config ? config.zIndex : elementCounter++;

        x = Math.round(Math.max(0, Math.min(x, screenWidth - elementWidth)));
        y = Math.round(Math.max(0, Math.min(y, screenHeight - elementHeight)));

        const elementId = zIndex;
        const element = $('<div class="element" id="element-' + zIndex + '" data-id="' + zIndex + '"><i class="fa fa-cog"></i></div>');
        // const element = $('<div class="element" id="' + elementId + '"><button>Button</button><div class="rotate-handle"></div></div>');

        element.css({
            left: x,
            top: y,
            width: elementWidth,
            height: elementHeight,
            zIndex: zIndex,
            transform: `rotate(0deg)`
        });

        element.draggable({
            containment: "#screen",
            start: function (event, ui) {
                focusElement(ui.helper);
            },
            drag: function (event, ui) {
                updateForm(ui.helper);
            }
        });

        element.resizable({
            containment: "#screen",
            handles: 'nw, ne, sw, se',
            start: function (event, ui) {
                focusElement(ui.element);
            },
            resize: function (event, ui) {
                updateForm(ui.element);
            }
        });

        /*
        element.rotatable({
            handle: element.find('.rotate-handle'),
            rotate: function(event, ui) {
                updateForm(ui.element);
            }
        });
        */

        element.click(function () {
            focusElement($(this));
        });

        screen.append(element);
        addElementToList(elementId);

        if (config !== null && config.contentId !== null) {
            element.attr('data-content-id', config.contentId);
            element.attr('data-content-name', config.contentName);
            element.attr('data-content-type', config.contentType);

            applyContentToElement({
                id: config.contentId,
                name: config.contentName,
                type: config.contentType,
            }, element);

            updateForm(element);
        } else {
            setTimeout(function () {
                focusElement(element);
            }, 10);
        }

        return element;
    }

    $(document).on('click', '.element-list-item', function(){
        focusElement($('#element-' + $(this).attr('data-id')));
    })

    $(document).on('click', '.remove-element', function(){
        if (confirm(l.js_common_are_you_sure)) {
            removeElementById($(this).attr('data-id'));
        }
    })

    function removeElementById(elementId) {
        $('.element[data-id='+elementId+'], .element-list-item[data-id='+elementId+']').remove();
        updateZIndexes();
    }

    function addElementToList(elementId) {
        const listItem = `<div class="element-list-item" data-id="__ID__">
            <i class="fa fa-cog"></i>
            <div class="inner">
                <label>__EMPTY__ __ID__ </label>
                <button type="button" class="btn btn-naked remove-element" data-id="__ID__">
                    <i class="fa fa-trash"></i>
                </button>
                <button type="button" class="btn btn-neutral configure-element content-explr-picker" data-id="__ID__">
                    <i class="fa fa-cog"></i>
                </button>
            </div>
        </div>`;
        $('#elementList').append(
            $(listItem
                .replace(/__ID__/g, elementId)
                .replace(/__EMPTY__/g, l.js_common_empty)
            )
        );
        updateZIndexes();
    }

    function unfocusElements() {
        $('.element, .element-list-item').removeClass('focused');
        currentElement = null;
        updateForm(null);
    }

    function focusElement(element) {
        unfocusElements();
        currentElement = element;
        currentElement.addClass('focused');
        const listElement = $('.element-list-item[data-id="' + currentElement.attr('data-id') + '"]');
        listElement.addClass('focused');
        updateForm(currentElement);
    }

    function updateForm(element) {
        if (!element) {
            $('form#elementForm input').val('').prop('disabled', true);
            $('.form-element-properties').addClass('hidden');
            return;
        }

        $('.form-element-properties').removeClass('hidden');
        $('form#elementForm input').prop('disabled', false);

        const offset = element.position();

        if (offset !== undefined) {
            $('#elem-x').val(offset.left);
            $('#elem-y').val(offset.top);
            $('#elem-width').val(element.width());
            $('#elem-height').val(element.height());
        }

        $(element).find('i').css('font-size', Math.min(element.width(), element.height()) / 3);
        /*
        const rotation = element.css('transform');
        const values = rotation.split('(')[1].split(')')[0].split(',');
        const angle = Math.round(Math.atan2(values[1], values[0]) * (180/Math.PI));
        $('#elem-rotate').val(angle);
        */
    }

    $(document).on('input', '#elementForm input', function () {
        if (currentElement) {
            const screenWidth = $('#screen').width();
            const screenHeight = $('#screen').height();

            let x = Math.round(parseInt($('#elem-x').val()));
            let y = Math.round(parseInt($('#elem-y').val()));
            let width = Math.round(parseInt($('#elem-width').val()));
            let height = Math.round(parseInt($('#elem-height').val()));
            // let rotation = parseInt($('#elem-rotate').val());

            // Constrain x and y
            x = Math.max(0, Math.min(x, screenWidth - width));
            y = Math.max(0, Math.min(y, screenHeight - height));

            // Constrain width and height
            width = Math.min(width, screenWidth - x);
            height = Math.min(height, screenHeight - y);

            currentElement.css({
                left: x,
                top: y,
                width: width,
                height: height
                // transform: `rotate(${rotation}deg)`
            });

            // Update form values to reflect clamped values
            $('#elem-x').val(x);
            $('#elem-y').val(y);
            $('#elem-width').val(width);
            $('#elem-height').val(height);
        }
    });

    // $(document).on('click', '#addElement', function () {
    //     createElement();
    // });

    $(document).on('click', '#removeAllElements', function () {
        if (confirm(l.js_common_are_you_sure)) {
            $('.element, .element-list-item').remove();
            updateZIndexes();
        }
    });

    $(document).on('dblclick', '.element', function (e) {
        $('.content-explr-picker[data-id='+$(this).attr('data-id')+']').click();
    });

    $(document).on('mousedown', function (e) {
        const keepFocusedElement = $(e.target).hasClass('element')
            || $(e.target).hasClass('element-list-item')
            || $(e.target).parents('.element:eq(0)').length !== 0
            || $(e.target).parents('.element-list-item:eq(0)').length !== 0
            || $(e.target).is('input,select,textarea')

        if (!keepFocusedElement) {
            unfocusElements();
        }
    })

    $(document).on('click', '#presetGrid2x2', function () {
        const screenWidth = $('#screen').width();
        const screenHeight = $('#screen').height();
        let elements = $('.element');
        if (elements.length < 4) {
            while (elements.length < 4) {
                createElement();
                elements = $('.element');
            }
        }

        const gridPositions = [
            {x: 0, y: 0},
            {x: screenWidth / 2, y: 0},
            {x: 0, y: screenHeight / 2},
            {x: screenWidth / 2, y: screenHeight / 2}
        ];

        elements.each(function (index) {
            const position = gridPositions[index];
            $(this).css({
                left: position.x,
                top: position.y,
                width: screenWidth / 2,
                height: screenHeight / 2
            });
            updateForm($(this));
        });
    });

    $(document).on('click', '.content-explr-picker', function () {
        const elementId = $(this).attr('data-id');
        const isNew = !elementId;
        const $element = isNew ? $(createElement()) : $('#element-'+elementId);

        showPickers('modal-content-explr-picker', function (content) {
            applyContentToElement(content, $element)
        });
    });

    const applyContentToElement = function (content, $element) {
        $element.attr('data-content-id', content.id);
        $element.attr('data-content-name', content.name);
        $element.attr('data-content-type', content.type);
        const $elementList = $('.element-list-item[data-id='+$element.attr('data-id')+']');
        const iconClasses = ['fa', content_type_icon_classes[content.type]].join(' ');
        $element.find('i').get(0).classList = iconClasses;
        $elementList.find('label').text(content.name);
        $elementList.find('i:eq(0)').get(0).classList = iconClasses;
    };

    $(document).on('submit', 'form.form', function (e) {
        unfocusElements();
        const layers = getLayersPayload();
        $('#content-edit-location').val(JSON.stringify(layers));
    });

    function updateZIndexes() {
        const zindex = $('.element-list-item').length + 1;
        $('.element-list-item').each(function(index) {
            const id = $(this).attr('data-id');
            $('#element-' + id).css('z-index', zindex - index);
        });
    }

    $('#elementList').sortable({
        update: function(event, ui) {
            updateZIndexes();
        }
    });

    const applyElementsFromContent = function() {
        const contentData = JSON.parse($('#content-edit-location').val());
        for (let i = 0; i < contentData.length; i++) {
            createElement(contentData[i]);
        }
    };

    applyElementsFromContent();
});

const getLayersPayload = function() {
    const screen = $('#screen');
    const screenWidth = screen.width();
    const screenHeight = screen.height();
    const layers = [];

    $('.element').each(function () {
        const offset = $(this).position();
        const x = offset.left;
        const y = offset.top;
        const width = $(this).width();
        const height = $(this).height();

        const xPercent = (x / screenWidth) * 100;
        const yPercent = (y / screenHeight) * 100;
        const widthPercent = (width / screenWidth) * 100;
        const heightPercent = (height / screenHeight) * 100;
        const contentId = $(this).attr('data-content-id');
        const contentName = $(this).attr('data-content-name');
        const contentType = $(this).attr('data-content-type');

        layers.push({
            xPercent: xPercent,
            yPercent: yPercent,
            widthPercent: widthPercent,
            heightPercent: heightPercent,
            zIndex: parseInt($(this).css('zIndex')),
            contentId: contentId ? parseInt(contentId) : null,
            contentName: contentName ? contentName : null,
            contentType: contentType ? contentType : null
        });
    });

    layers.sort(function(a, b) {
        return parseInt(b.zIndex) - parseInt(a.zIndex);
    });

    return layers;
};