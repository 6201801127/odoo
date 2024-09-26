odoo.define('kw_resource_management.emp_survey_skill', function (require) {
    'use strict';

    var personal = {
        init: function(){
            this.validation();
        },
        validation: function(){
            $.validator.messages.selectListItem = 'Skill is required.';
            $.validator.addClassRules({drp: {selectListItem: "0"}});
            
            $("form#frm_emp_skills").validate({
                // Specify validation rules
                rules: {
                    txtskil1_id: { selectListItem: "0" },
                },
                messages: {
                    txtskil1_id: { selectListItem: "Please provide your primary skill" },
                },
                submitHandler: function (frm) {
                    var skill_id = $("#txtskil1_id").val();
                    if (skill_id == 0) {
                        swal("Please Select The Primary Skill!");
                        return false;
                    }
                    frm.submit();
                },
                errorElement: "span",
                highlight: function (element) {
                    $(element).css('background', '#ffdddd');
                },
                unhighlight: function (element) {
                    $(element).css('background', '#ffffff');
                }
            });  //End of form validation
        }
    };
    
    $(function(){
        personal.init();
        
        $('#txtskil1_id').on('change', function() {
            if ($(this).find("option:selected").attr('rel') == 'other') {
                $('#others_reason').show();
                $('#others_reason').prop('required', true);
            } else {
                $('#others_reason').hide();
                $('#others_reason').prop('required', false);
            }
        });
        $('#txtskil2_id').on('change', function() {
            if ($(this).find("option:selected").attr('rel') == 'other') {
                $('#others_reason2').show();
                $('#others_reason2').prop('required', true);
            } else {
                $('#others_reason2').hide();
                $('#others_reason2').prop('required', false);
            }
        });
        $('#txtskil3_id').on('change', function() {
            if ($(this).find("option:selected").attr('rel') == 'other') {
                $('#others_reason3').show();
                $('#others_reason3').prop('required', true);
            } else {
                $('#others_reason3').hide();
                $('#others_reason3').prop('required', false);
            }
        });
        
        // $("form#frm_emp_skills").on('submit', function(e) {
        //     var skill_id = $("#txtskil1_id").val();
        //     if (skill_id === '9') {
        //         var textareaValue = $("#others_reason").val();
        //         console.log("textareaValue====================",textareaValue)
               
        //     }
            
        // });
    }); //end of ready function
});
