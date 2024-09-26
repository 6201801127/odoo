odoo.define('kw_appraisal.hide_button', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var goals = {
        init: function () {
            $(document).on('click', '#hides', function () {
                $(this).hide();
                $(document).find('.hidee').hide();
            });
        },
    };

    $(function () {
        goals.init();
    });
});