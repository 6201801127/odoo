odoo.define('kw_recruitment.kwapplicant_common_methods', function (require) {  // how it works ?? 
    'use strict';

    $(function(){
        // $(document).on('change', 'input[type=file]', function () {
        //     if(typeof this.files[0] !== "undefined"){
        //         $(this).parent().find("span.txt-filename").html(this.files[0].name);
        //         $(this).parent().find("input:hidden").val(this.files[0].name);
        //     }else{
        //         $(this).parent().find("span.txt-filename").html('');
        //         $(this).parent().find("input:hidden").val('');
        //     }
        // });
        if(typeof $.validator != 'undefined'){
            // To append the selected file name Under Browse Option:Start---
            $.validator.addMethod("selectListItem", function (value, element, arg) {
                return arg !== '' && arg !== element.value;
            });
            $.validator.addMethod('filesize', function (value, element, param) {
                if (typeof element.files[0] !== "undefined"){
                    return this.optional(element) || (element.files[0].size <= param)
                } else{
                    return true
                }
            }, 'File size must be less than {0}');

            $.validator.addMethod("check_date", function (value, element, min) {
                var today = new Date();
                var birthDate = new Date(value);
                var age = today.getFullYear() - birthDate.getFullYear();
                if (age > min + 1) {
                    return true;
                }
                var m = today.getMonth() - birthDate.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                return age >= min;
            });

            $.validator.addMethod("lettersOnly", function (value, element) {
                return this.optional(element) || /^([a-zA-Z]{3,16})$/i.test(value);
            }, "Letters only please");

            $.validator.addMethod("pincode", function (value, element) {
                return this.optional(element) || /^[1-9][0-9]{5}$/i.test(value);
            });

            jQuery.validator.addMethod('likert', function (value, element) {
                var $inputs = $(element).closest('tr.likert').find('.likert-field:filled');
                if (0 < $inputs.length  && !($(element).val())) {
                    return false;
                } else {
                    return true;
                }
            }, 'Partially completed rows are not allowed');
            // Likert Fields
            jQuery.validator.addClassRules('likert-field', {
                likert: true
            });
        }
       
    //     setTimeout(function(){
    //         $('.file_upload').each(function(){
    //             console.log('hello method called');
    //             var el  = $(this);
    //             console.log(el.attr('id'));
    //             var x = $('#'+el.attr('id')).uploadifive({
    //                 'auto'             : false,
    //                 'dnd'               : false,
    //                 //'checkScript'      : 'check-exists.php',
    //                 'fileType'         : '.jpg,.jpeg,.gif,.png',
    //                 'formData'         : {
    //                                     'timestamp' : '1111',
    //                                     'token'     : '1111',
    //                                     'rec': el.attr('id')
    //                                     },
    //                 'queueID'          : 'queue',
    //                 'uploadLimit'       : 1,
    //                 'simUploadLimit':1,
    //                 'uploadScript'     : '/uploadify',
    //                 'onUploadComplete' : function(file, data) { console.log('onUploadComplete', file,data); },
    //                 'onAddQueueItem' : function(file) { console.log('onAddQueueItem',file, file.name); },
    //                 'onUploadFile' : function(file) { console.log('onUploadFile',file, file.name); },
    //                 'onUpload' : function(file) { console.log('onUpload',file, file.name); },
    //             });
    //             console.log(x);
    //         });
    // },2000);

    });
});
