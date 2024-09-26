odoo.define('kw_onboarding.kwonboard_document_details_upload', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var document = {
        init: function () {
            console.log("inside init----")
            
            this.validation();
            
            function readDocument(input) {
                console.log("read doc called------")
                if (input.files && input.files[0]) {
                    var reader = new FileReader();
                    var params = {}
                    var data_field = ''
                    var data_file_name = ''
                    var data_upload_type = ''
                    var data_record_id = ''
                    reader.onload = function(e) {
                        $(input).attr('filedata', '"'+ e.target.result +'"');
                        $(input).attr('filename', '"'+ input.files[0].name +'"');
                        var document_data = e.target.result.replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                        var document_name = input.files[0].name;
                        if ($(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-upload-type') == 'upload_educational_document')
                        {
                            data_field = $(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-field')
                            data_file_name = $(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-file-name')
                            data_upload_type = $(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-upload-type')
                            data_record_id = $(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-id');
                        }
                        else{
                            data_field = $(input).closest('tr').find('td:nth-child(2) > input[type="file"]').attr('data-field')
                            data_file_name = $(input).closest('tr').find('td:nth-child(2) > input[type="file"]').attr('data-file-name')
                            data_upload_type = $(input).closest('tr').find('td:nth-child(2) > input[type="file"]').attr('data-upload-type')
                            data_record_id = $(input).closest('tr').find('td:nth-child(2) > input[type="file"]').attr('data-id');
                        }
                        params[data_upload_type] = data_upload_type
                        params[data_field] = document_data
                        params[data_file_name] = document_name
                        if (data_upload_type == 'upload_identification_document') { params['identification_id'] = data_record_id}
                        else if (data_upload_type == 'upload_experience_document') { params['experience_id'] = data_record_id}
                        else if (data_upload_type == 'upload_educational_document') { params['education_id'] = data_record_id}
                        else if (data_upload_type == 'upload_payslip_document1') { params['previous_payslip_available'] = data_record_id}
                        else if (data_upload_type == 'upload_payslip_document2') { params['previous_payslip_available'] = data_record_id}
                        else if (data_upload_type == 'upload_payslip_document3') { params['previous_payslip_available'] = data_record_id}
                        console.log('params >>> ', params);
                        ajax.jsonRpc("/saveDocumentDetailsOnchange", 'call', params).then(function (values) {
                            if ($(input).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-upload-type') == 'upload_educational_document')
                            {
                                $(input).closest('tr').find('td:nth-child(3) > input[type="file"]').css('display','none');
                                $(input).closest('tr').find('td:nth-child(3)> span').html("<i class='fa fa-file text-success mr-2'></i>"+values[Object.keys(values)[0]]);
                                $(input).closest('tr').find('td:nth-child(4)> a').attr('href',"/web/content/"+values[Object.keys(values)[1]]);
                                $(input).closest('tr').find('td:nth-child(4)> a').removeAttr('style');
                                $(input).closest('tr').find('td:nth-child(5)> a').removeAttr('style');
                            }
                            else{
                                console.log('values >>>> ', values, Object, Object.keys(values));
                                $(input).closest('tr').find('td:nth-child(2) > input[type="file"]').css('display','none');
                                $(input).closest('tr').find('td:nth-child(2)> span').html("<i class='fa fa-file text-success mr-2'></i>"+values[Object.keys(values)[0]]);
                                $(input).closest('tr').find('td:nth-child(3)> a').attr('href',"/web/content/"+values[Object.keys(values)[1]]);
                                $(input).closest('tr').find('td:nth-child(3)> a').removeAttr('style');
                                $(input).closest('tr').find('td:nth-child(4)> a').removeAttr('style');
                            }
                        });
                    }
                    reader.readAsDataURL(input.files[0]);
                }
            };       

            $(".document_upload").change(function() {
                var file_size = this.files[0].size;
                var file_name = this.files[0].name.toLowerCase();
                var fileExtension = file_name.substr((file_name.lastIndexOf('.') + 1));
                if ($(this).closest('tr').find('td > input[type="file"]').attr('data-upload-type') == 'upload_image'){
                    if (file_size > 1048576) alert("Maximum allowed file size is 1 MB.")
                    else if($.inArray(fileExtension, ['jpeg','png','jpg']) == -1) {
                        alert('Only jpg,jpeg and png Image is Supported.');
                    }
                    else{
                        readDocument(this);
                    }
                }
                if ($(this).closest('tr').find('td > input[type="file"]').attr('data-upload-type') != 'upload_image'){
                    if (file_size > 4194304) alert("Maximum allowed file size is 4 MB.")
                    else if($.inArray(fileExtension, ['jpeg','png','jpg','pdf']) == -1) {
                        alert('Only jpg,jpeg,png and pdf document is Supported.');
                    }
                    else{
                        readDocument(this);
                    }
                }
            });

            $('.document_reupload').click(function(){
                if ($(this).closest('tr').find('td:nth-child(3) > input[type="file"]').attr('data-upload-type') == 'upload_educational_document')
                {
                    $(this).closest('tr').find('td:nth-child(3)> input.document_upload').click();
                }
                else{
                    $(this).closest('tr').find('td:nth-child(2)> input.document_upload').click();
                }
            });
            
        },
        validation: function(){
            // console.log("inside validation",$(this).data("doctype"),$(this).data("id"))
            
            $("form#frm_documents_upload").validate({
                // Specify validation rules
                rules: {
                    upload_personal_image: {
                        required    : true,
                        accept      : "image/png,image/jpeg,image/jpg",
                        filesize    : 1048576
                    },
                    
                    // upload_medical_certificate: {
                    //     required    : false ,
                    //     accept      : "image/png,image/jpeg,image/jpg,application/pdf",
                    //     filesize    : 4194304
                    // },
                },
                messages: {
                    upload_personal_image: {
                        required: 'Please upload a Photo.',
                        accept  : "Only jpg,jpeg and png Image is Supported.",
                        filesize:  "Maximum allowed file size is 1 MB."
                    },
                    upload_payslip_document: {
                        required: 'Please upload a Payslip.',
                        accept  : "Only jpg,jpeg and png Image is Supported.",
                        filesize:  "Maximum allowed file size is 1 MB."
                    },
                    // upload_medical_certificate: {
                    //     required: 'Please upload medical Certificate.',
                    //     accept  : "Only jpg,jpeg,png and pdf is Supported.",
                    //     filesize:  "Maximum allowed file size is 4 MB."
                    // },
                },

                // validateEducationData: function(){
                //     $("form#frm_documents_upload").validate({});
                    
                // },

                // Make sure the form is submitted to the destination defined
                // in the "action" attribute of the form when valid
                submitHandler: function (frm) {
                   
                    // console.log('submit..')
                    frm.submit();
                },
                errorElement: "div",
                highlight: function (element) {
                    $(element).css('background', '#ffdddd');
                },
                unhighlight: function (element) {
                    $(element).css('background', '#ffffff');
                }
            });
            $("input[data-doctype='education_data']").each(function(){
                $(this).rules("add" ,
                {
                    required    : true,
                    accept      : "image/png,image/jpeg,image/jpg",
                    filesize    : 4194304
                });
                
            }); 
            $("input[data-doctype='work_experience_data']").each(function(){
                $(this).rules("add" ,
                {
                    required    : true,
                    accept      : "image/png,image/jpeg,image/jpg",
                    filesize    : 4194304
                });
                
            });  //End of form validation
            $("input[data-doctype='identification_data']").each(function(){
                $(this).rules("add" ,
                {
                    required    : true,
                    accept      : "image/png,image/jpeg,image/jpg",
                    filesize    : 4194304
                });
                
            });


        },
        
    };
    $(function(){
        document.init();
    }); 
});