odoo.define('kw_recruitment.kw_recruitment_offer_letter_mail_redirect', function (require) {
    'use strict';
    
    $(function() {
        $('#accept').click(function() {
            var obj = $(this)
            if ($('#terms_conditions').is(':checked')) {
                swal.close();
                //$('#accept').find('a').trigger('click');
                window.location.href=obj.attr('thref');
            }
            else {
                swal({ title:"Offer Letter",text: "Please accept the terms & conditions.", icon: "warning", buttons: { cancel: 'OK' } });
                //alert('Please accept the terms & conditions.');
                return false;
            }
        })
    })


});