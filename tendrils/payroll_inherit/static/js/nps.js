odoo.define('payroll_inherit.update_nps_details_web_template', function (require) {
    'use strict';

    var $ = require('jquery');

    var bank = {
        init: function () {
            $('#handleButtonClick').on('click', function (e) {
                var nps_interested = $("#nps_interested").val();
                if (nps_interested === null) {
                    swal("Please update your NPS status!");
                    return false;
                }
                var percentage = $("#percentage").val();
                if (nps_interested === 'Yes' && (percentage === null || percentage === '')) {
                    swal("Please select the contribution options  for NPS!");
                    return false;
                }
                var have_pran = $("#have_pran").val();
                if (nps_interested === 'Yes' && (have_pran === null || have_pran === '')) {
                    swal("Please update your PRAN status!");
                    return false;
                }
                var pran_number = $("#pran_number").val();
                if (have_pran === 'Yes' && (pran_number === null || pran_number === '')) {
                    swal("Please update your PRAN!");
                    return false;
                }
                if (have_pran === 'Yes' && (pran_number.length != 12)) {
                    swal("Please update valid PRAN!");
                    return false;
                }

            });
        }
    };

    $(document).ready(function() {
        bank.init();  
    });
});
