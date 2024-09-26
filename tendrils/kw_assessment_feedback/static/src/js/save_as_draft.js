odoo.define('kw_assessment_feedback.save_as_draft', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var the_form = $('#kw_assessment_feedback_form');
    var submit_controller = the_form.attr("data-back");
    var feedback = {
        init: function () {
            $(document).on("click", '#save_as_draft', function () {
                window.location.href = '/web#action=kw_assessment_feedback.kw_feedback_final_config_action&amp;model=kw_feedback_final_config&amp;view_type=kanban&amp;menu_id=kw_assessment_feedback.kw_assessment_final_config_add_feedback'
                // var prevs = 'prevs'
                // swal({
                //     text: "Are you sure want to save and go back ?",
                //     icon: "warning",
                //     dangerMode: true,
                //     closeOnClickOutside: false,
                //     closeModal: false,
                //     buttons: {
                //         confirm: { text: 'Yes, Go Back', className: 'btn-primary' },
                //         cancel: 'Cancel'
                //     },
                // }).then(function (isConfirm) {
                //     if (isConfirm) {
                //         feedback.ajax_call(prevs);
                //         window.location.href= "window.history.go(-1);" 
                //     } else {
                //         swal.close();
                //     }
                // });
            });
            $(document).on("click", '#back_to_goal', function () {
                var feedback_details = the_form.find('#feedback').val()
                var token = the_form.find("#token").val()
                window.location.href = "/kw/feedback/goal/" + feedback_details + "/" + token
            });
        },
        ajax_call: function (prevs) {
            var result = {};
            $.each($('#kw_assessment_feedback_form').serializeArray(), function () {
                result[this.name] = this.value;
            });
            ajax.jsonRpc(submit_controller, 'call', {
                'kw_feedback_form':result,
                'prevs':prevs,
            }).then(function (data) {
                if (data['redirect']=='prevs'){
                    window.location.href = '/web#action=kw_assessment_feedback.kw_feedback_final_config_actions&amp;model=kw_feedback_details&amp;view_type=kanban&amp;menu_id=kw_assessment_feedback.kw_assessment_feedback_menu_root'                        
                }
            });
        },
    };

    $(function () {
        feedback.init();
    });
});