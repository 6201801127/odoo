odoo.define('kw_appraisal.count_text', function (require) {
    'use strict';
    var results = {
        init: function () {
            $('textarea').keyup(function () {

                var characterCount = $(this).val().length,
                    current = $(this).next().find('#current'),
                    maximum = $(this).next().find('#maximum'),
                    theCount = $(this).next().find('#the-count');

                current.text(characterCount);

                if (characterCount < 10) {
                    current.css('color', '#666');
                }
                if (characterCount > 10 && characterCount < 30) {
                    current.css('color', '#6d5555');
                }
                if (characterCount > 30 && characterCount < 50) {
                    current.css('color', '#793535');
                }
                if (characterCount > 50 && characterCount < 70) {
                    current.css('color', '#841c1c');
                }
                if (characterCount > 70 && characterCount < 90) {
                    current.css('color', '#8f0001');
                }

                if (characterCount >= 100) {
                    maximum.css('color', '#8f0001');
                    current.css('color', '#8f0001');
                    theCount.css('font-weight', 'bold');
                } else {
                    maximum.css('color', '#666');
                    theCount.css('font-weight', 'normal');
                }
            });
            // $(document).ready(function() {
            //     var value = $('textarea').val().length;
            //     $(this).next().find('#current').text(value);
            // });

        },
    };

    $(function () {
        results.init();
    });
});