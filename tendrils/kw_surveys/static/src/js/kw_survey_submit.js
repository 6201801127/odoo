odoo.define('kw_assessment_feedback.feedback_form', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    $('#finish').on('click', function (e) {
        e.preventDefault();
        // alert("called");
        var form = $(this).parents('form');
        // console.log(form);
        // console.log(form.valid());
        if (form.valid()){
            // loop over the text areas and find the content inside iframe and set  the content to the text area.
            $("textarea").each(function(){
                // alert(this.id);
                var frame_div_id = '#cke_'+this.id;
                // alert(frame_div_id);
                var content = $(frame_div_id).contents().find('iframe').contents().find('body').html();
                // alert(content);
                this.value = content;
            });
            $('form').submit();
                       
        }
    });
});