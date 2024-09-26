odoo.define('kw_epf_form.kw_employee_epf_form', function (require) { 
    'use strict';
    var epf_form = {
        current_id:'',
        clone:'1',
        dateFormat: 'dd-mm-yyyy',
        init: function(){
            this.validation();
            this.showHideButton();
            this.clone = $('#epf_block').find('tr').eq(0).clone();
            $(document).on("click",'.add-row',function(){
                console.log("called method")
                epf_form.addMore();
            });
            $(document).on("click",".remove-row",function(){
                epf_form.removeRow(this);
            });
            var datepickerelmts = $('.dob-datepicker').length
            if (datepickerelmts>0){
                var totpicklength = datepickerelmts/2
                for (let index = 0; index < datepickerelmts/2; index++) {                    
                    this.dateRestrict(index);
                } 
            }
            // $(document).on("change","#upload_photo",function(){
                
            //     var filename = $("#upload_photo").val();
            //     if (/^\s*$/.test(filename)) {
            //       $(".file-upload").removeClass('active');
            //       $("#noFile").text("No file chosen..."); 
            
            //       $("#AdhaarPhotoFile").text(""); 
            //       $("#hdnimagename").val(""); 
            
            //     }
            //     else {
            //       $(".file-upload").addClass('active');
            //       $("#noFile").text(filename.replace("C:\\fakepath\\", "")); 
            
            //       $("#AdhaarPhotoFile").text(filename.replace("C:\\fakepath\\", "")); 
            //       $("#hdnimagename").val(filename.replace("C:\\fakepath\\", "")); 
            //     }
            // });

            // $(document).on("change","#upload_hsc_photo",function(){
                
            //     var hscfilename = $("#upload_hsc_photo").val();
            //     if (/^\s*$/.test(hscfilename)) {
            //       $(".file-hsc").removeClass('active');
            //       $("#noFile").text("No file chosen..."); 
            
            //       $("#HscPhotoFile").text(""); 
            //       $("#hdnimagehsc").val(""); 
            
            //     }
            //     else {
            //       $(".file-hsc").addClass('active');
            //       $("#noFile").text(hscfilename.replace("C:\\fakepath\\", "")); 
            
            //       $("#HscPhotoFile").text(hscfilename.replace("C:\\fakepath\\", "")); 
            //       $("#hdnimagehsc").val(hscfilename.replace("C:\\fakepath\\", "")); 
            //     }
            // });

            $(document).on("change","#upload_epf_photo",function(){
                
                var epffilename = $("#upload_epf_photo").val();
                if (/^\s*$/.test(epffilename)) {
                  $(".file-epf").removeClass('active');
                  $("#noFile").text("No file chosen..."); 
            
                  $("#EpfPhotoFile").text(""); 
                  $("#hdnimageepf").val(""); 
            
                }
                else {
                  $(".file-epf").addClass('active');
                  $("#noFile").text(epffilename.replace("C:\\fakepath\\", "")); 
            
                  $("#EpfPhotoFile").text(epffilename.replace("C:\\fakepath\\", "")); 
                  $("#hdnimageepf").val(epffilename.replace("C:\\fakepath\\", "")); 
                }
            });

            //Input field not accepting special characters
            $(document).on("keydown keyup", '.special', function(){
                console.log("inside js....")
                var $el = $(this);
                var val = $el.val().replace(new RegExp("^[ ]+", "g"), "");
                if ($el.hasClass("address")) { //Address
                    val = val.replace(/[^a-z\d\-\s\,]/gi, '');
                }else if ($el.hasClass("name")) { //name
                    val = val.replace(/[^a-z\s]/gi, '');
                $el.val(val);
                }else if ($el.hasClass("number")) { //number
                    val = val.replace(/[^\d\s]/gi, '');
                }
            });
            // Personal Information validation :Start : ------------------------------
            this.select2();
        },
        
        removeRow: function(el){
            $(el).closest('tr').remove();
            this.showHideButton();
        },
        addMore: function(){
            var current_id = ++this.current_id;
            var newElement = this.clone.clone();
            newElement.find('select option[value="0"]').attr("selected",true);
            
            //for new element set the id value to zero

            newElement.find('select,input').each(function(){
                $(this).attr('id',$(this).attr('id').replace(/\d+/,current_id));
                $(this).attr('name',$(this).attr('name').replace(/\d+/,current_id));
            });
            $('.remove-row:last').show();
            $("#epf_block").append(newElement);
            this.dateRestrict(current_id);
            this.showHideButton();
            this.select2();
            return true;
        },
        
        showHideButton: function(){
            $("#epf_block").find('tr').size() > 1 ?
                        $('.remove-row').removeClass('disabled').addClass('anchor').attr('disabled',false) :
                        $('.remove-row').addClass('disabled').removeClass('anchor').attr('disabled',true);
            // $("#epf_block").find('tr').size() < $("#epf_block").find('select').eq(0).find('option').size() - 1 ?
            //             $('.add-row').removeClass('disabled').addClass('anchor').attr('disabled',false) :
            //             $('.add-row').addClass('disabled').removeClass('anchor').attr('disabled',true);

            return true;
            //$('.btn_add_lang').not(':last').hide();
            //$('.btn_remove_lang:last').hide();
        },
        dateRestrict: function(cnt){
            console.log("count==",cnt)
            var from = $("#txtDateOfBirth_"+cnt).datepicker({
                minDate: new Date(1954, 1 - 1, 1), 
                maxDate: '-0Y', 
                dateFormat: 'dd-mm-yy',
                changeMonth: true,
                changeYear: true
            })
            
            // $( "#txtDateOfBirth" ).datepicker("option", "showAnim", "slideDown");
            
        },
        validation: function(){
            $.validator.addClassRules({drp: {selectListItem: "0"},});

            $("form#epf_form").validate({
                // Specify validation rules
                rules: {
                    member_name: {
                        required: true
                    },
                    nominees_name_0: {
                        required: true,
                    },
                    nominees_relationship_0: { selectListItem: "0" },
                    nominees_address_0: {
                        required: true,
                    },
                    // upload_photo: {
                    //     required: function(){
                    //         return $('#hdnimagename').val() == ''
                    //     },
                    //     accept      : "image/png,image/jpeg,image/jpg",
                    //     filesize    : 1048576,

                    // },
                    // upload_hsc_photo: {
                    //     required: function(){
                    //         return $('#hdnimagehsc').val() == ''
                    //     },
                    //     accept      : "image/png,image/jpeg,image/jpg",
                    //     filesize    : 1048576,

                    // },
                    txtDateOfBirth_0: {
                        required: true,
                        // check_date: 18
                    },
                    upload_epf_photo: {
                        required    : function(element) {
                            return $('#period_of_service_year_0').val() != '0';
                        },
                        accept      : "image/png,image/jpeg,image/jpg",
                        filesize    : 4194304,
                    },
                    
                    // period_of_service: {
                    //     required: true,
                    //     maxlength: 2,
                    // },
                    // aadhaar_no: {
                    //     required: true,
                    //     maxlength: 12,
                    // },
                    uan_no: {
                        required    : function(element) {
                            return $('#period_of_service_year_0').val() != '0';
                        },
                        maxlength: 25,
                    },
                },
                
                //Specify validation messages
                messages: {
                    member_name: { required: "Please provide Father/Husband full name" },
                    nominees_name_0: { required: "Please provide Nominee name" },
                    nominees_address_0: { required: "Please provide Nominee's Address" },
                    nominees_relationship_0: { selectListItem: "Please provide Nominee's relationship with the member" },
                    // upload_photo: {
                    //     required: '<h6>Please upload document.</h6>',
                    //     accept  : "Only jpg,jpeg and png Image is Supported.",
                    //     filesize:  "Maximum allowed file size is 1 MB."
                    // },
                    // upload_hsc_photo: {
                    //     required: '<h6 style="margin-left: 220px;">Please upload document.</h6>',
                    //     accept  : "Only jpg,jpeg and png Image is Supported.",
                    //     filesize:  "Maximum allowed file size is 1 MB."
                    // },
                    txtDateOfBirth_0: {
                        required: 'Please Enter Date of Birth.',
                        // check_date: "You are not old enough !! Your age must 18+ ."
                    },
                    upload_epf_photo: {
                        required: '<h6 style="margin-left: 265px;width: 170px;">Please upload document.</h6>',
                        accept  : "Only jpg,jpeg and png Image is Supported.",
                        filesize:  "Maximum allowed file size is 1 MB."
                    },
                    // period_of_service: {
                    //     required: "Please provide Nominee's Period of service",
                    //     maxlength: 'Maximum length should must be 2 digit.'
                    // },
                    // aadhaar_no: {
                    //     required: "Please provide Nominee's Aadhaar Card number",
                    //     maxlength: 'Maximum length should must be 12 digit.'
                    // },
                    uan_no: {
                        required: "Please provide Nominee's UAN number",
                        maxlength: 'Maximum length should must be 25 digit.'
                    },
                },

                // Make sure the form is submitted to the destination defined
                // in the "action" attribute of the form when valid
                submitHandler: function (frm) {
                   
                    // console.log('submit..')
                    frm.submit();
                },
                errorElement: "div",
                highlight: function (element) {
                    $(element).css('background', '#FFFFFF');
                },
                unhighlight: function (element) {
                    $(element).css('background', '#FFFFFF');
                }
            });  //End of form validation

            $.validator.addClassRules({  
                clsrequired: {
                    required    : true,
                },
                clsoptrequired: {
                    selectListItem: "0",
                
                },
    
                    
            });
            if(typeof $.validator != 'undefined'){
                // To validate nomine relationship if not selected
                $.validator.addMethod("selectListItem", function (value, element, arg) {
                    return arg !== '' && arg !== element.value;
                })};
        },
        select2: function(){
            $('select').select2();
            $('[data-rel="tooltip"]').tooltip();
        }
        
    };
    $(function(){
        epf_form.init();
    }); //end of ready function

    
}); // End of module

