odoo.define('kw_appraisal.surveys', function (require) {
    'use strict';

    var personal = {
        init: function(){
            this.validation();
        },
        validation: function(){

            $.validator.messages.selectListItem = 'Score is required.';
            $.validator.addClassRules({drp: {selectListItem: ""},});


            $("form#kw_survey_form").validate({
                // Specify validation rules
                rules: {
                    justify: {required: true},
                    score: { selectListItem: "" },
                    },
                messages: {
                    justify: { lettersOnly: 'Please do not use spaces and numbers', required: "Please provide a justification " },
                    score: { selectListItem: "Please select your Score" },
                },
                submitHandler: function (frm) {
                   
                    console.log('submit..')
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


        },

    };
    $(function(){
        personal.init();
    }); //end of ready function
});