odoo.define('kw_assessment_feedback.feedback_form', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    $('#finish').on('click', function (e) {
        e.preventDefault();
        var form = $(this).parents('form');
        if (form.valid()){
            
            swal({
                text: "Are you sure want to submit ?",
                icon: "warning",
                dangerMode: true,
                closeOnClickOutside: false,
                closeModal: false,
                buttons: {
                    confirm: { text: 'Yes, Submit', className: 'btn-info' },
                    cancel: 'Cancel'
                },
            }).then(function (isConfirm) {
                if (isConfirm) {
                    var iname = $('#instructor').children("option:selected").html();
                    var params = {
                        training_id: $('input[name$="tid"]').val(),
                        instructor_type: $('input[name$="instructor_type"]').val(),
                        emp_id: $('input[name$="eid"]').val(),
                        instructor_id: $('#instructor').children("option:selected").val(),
                        
                    };
                    rpc.query({
                        model: 'kw_training_feedback',
                        method: 'check_feedback_given',
                        args: [params],
                    }).then(function (result) {
                        if (result==false){
                            swal({
                                text: "You have already submitted feedback for " + iname ,
                                icon: "warning",
                                dangerMode: true,
                                closeOnClickOutside: false,
                                closeModal: false,
                                buttons: {
                                    cancel: 'Close'
                                },
                            });
                        } 
                        else {
                            $('form').submit();
                        }
                       
                    });
                } else {
                    swal.close();
                }
            });
        }
    });
});