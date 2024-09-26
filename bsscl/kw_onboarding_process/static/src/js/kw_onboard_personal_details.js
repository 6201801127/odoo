odoo.define('kw_onboarding_process.kwonboard_personal_details', function (require) {
    'use strict';
    var personal = {
        current_id:'',
        clone:'',
        dateFormat: 'dd-mm-yyyy',
        init: function(){
            this.validation();
            this.showHideButton();
            this.dateRestrict('0');


            $('#ddlMaritalStatus option:selected').attr('code') == 'M' || $('#ddlMaritalStatus option:selected').attr('code') == 'C' ? $('.anniversary-block').show() : $('.anniversary-block').hide();

            $('#ddlMaritalStatus').on('change',function(){
                var marital_code = $('#ddlMaritalStatus option:selected').attr('code')
                $('#marital_code').val(marital_code)
                marital_code == 'M' || marital_code == 'C' ?$('.anniversary-block').show() : $('.anniversary-block').hide(),$('#txtWedAniversary').val("");
            })

            $('input[name="willing_travel"]').on('change',function(){
                let input_val = $('input[name="willing_travel"]:checked').val()
                input_val == '1'?$('.travel-options').show():$('.travel-options').hide(),$('input[name="travel_abroad"]').val(['0']),$('input[name="travel_domestic"]').val(['0']);
            })
            $('input[name="willing_travel"]:checked').val() == '0'?$('.travel-options').hide():$('.travel-options').show();

            $('#display-success').hide();
            $('#display-error').hide();

            this.current_id = $('#language_known_block').find('tr').size();
            this.clone = $('#language_known_block').find('tr').eq(0).clone();

            $(document).on("click",'.btn_add_lang',function(){
                personal.addMore();
            });
            $(document).on("click",".btn_remove_lang",function(){
                personal.removeRow(this);
            });

            $(document).on("change","#fupPhoto",function(){
                
                var filename = $("#fupPhoto").val();
                if (/^\s*$/.test(filename)) {
                  $(".file-upload").removeClass('active');
                  $("#noFile").text("No file chosen..."); 
            
                  $("#ProfilePhotoFile").text(""); 
                  $("#hdnimagename").val(""); 
            
                } else {
                  $(".file-upload").addClass('active');
                  $("#noFile").text(filename.replace("C:\\fakepath\\", "")); 
            
                  $("#ProfilePhotoFile").text(filename.replace("C:\\fakepath\\", "")); 
                  $("#hdnimagename").val(filename.replace("C:\\fakepath\\", "")); 
                }
            });

            $(document).on("change","#medicPhoto",function(){
                
                var fname = $("#medicPhoto").val();
                if (/^\s*$/.test(fname)) {
                  $(".file-up").addClass('active');
                  $("#noFile").text("No file chosen...");
                  $("#MedicalCertificateFile").text(""); 
                  $("#hdnmcertificatename").val(""); 
            
                } else {
                   
                  $(".file-up").addClass('active');
                  $("#noFile").text(fname.replace("C:\\fakepath\\", ""));
                  $("#MedicalCertificateFile").text(fname.replace("C:\\fakepath\\", "")); 
                  $("#hdnmcertificatename").val(fname.replace("C:\\fakepath\\", "")); 
                }
            });

            // Same as Above code :start----
            $('#chkCopyAddress').on("click", function () {
                if ($('#chkCopyAddress').is(':checked')) {
                    $('#txtPermAddressLine1').val($('#txtPresAddressLine1').val()).change();
                    $('#txtPermAddressLine2').val($('#txtPresAddressLine2').val()).change();
                    $('#ddlPermCountry').val($('#ddlPresentContry').val()).select2();
                    // $('#ddlPermstate').val($('#ddlPresState').val());
                    $('#ddlPermstate').attr('data-select', $('#ddlPresState').val());
                    $('#txtPermCity').val($('#txtPresCity').val()).change();
                    $('#txtPermPinCode').val($('#txtPresPin').val()).change();
                }

            });
            // Same as Above code :End----

            //Input field not accepting special characters
            $(document).on("keydown keyup", '.special', function(){
                var $el = $(this);
                var val = $el.val().replace(new RegExp("^[ ]+", "g"), "");
                if ($el.hasClass("address")) { //Address
                    val = val.replace(/[^a-z\d\-\s\,]/gi, '');
                }else if ($el.hasClass("city")) { //City
                    val = val.replace(/[^a-z\s]/gi, '');
                }else if ($el.hasClass("pincode")) { //Pincode
                    val = val.replace(/[^\d\s]/gi, '');
                }
                $el.val(val);
            });
            // Personal Information validation :Start : ------------------------------
            this.select2();
        },
        addMore: function(){
            var current_id = this.current_id++;
            var newElement = this.clone.clone();
            newElement.find('select option[value="0"]').attr("selected",true);
            
            //for new element set the id value to zero
            newElement.find('.clslangids').val("0");

            newElement.find('select,input').each(function(){
                $(this).attr('id',$(this).attr('id').replace(/\d+/,current_id));
                $(this).attr('name',$(this).attr('name').replace(/\d+/,current_id));
            });
            $('.btn_remove_lang:last').show();
            $("#language_known_block").append(newElement);
            this.showHideButton();
            this.select2();
            // $('#lang_tbl tr').length <= $('#select[id^="lang_"] option').length ?
            //$(".btn_add_lang").attr('enabled','enabled'):$(".btn_add_lang").attr('disabled','disabled');
            return true;
        },
        showHideButton: function(){
            $("#language_known_block").find('tr').size() > 1 ?
                        $('.btn_remove_lang').removeClass('disabled').addClass('anchor').attr('disabled',false) :
                        $('.btn_remove_lang').addClass('disabled').removeClass('anchor').attr('disabled',true);
            $("#language_known_block").find('tr').size() < $("#language_known_block").find('select').eq(0).find('option').size() - 1 ?
                        $('.btn_add_lang').removeClass('disabled').addClass('anchor').attr('disabled',false) :
                        $('.btn_add_lang').addClass('disabled').removeClass('anchor').attr('disabled',true);

            return true;
            //$('.btn_add_lang').not(':last').hide();
            //$('.btn_remove_lang:last').hide();
        },
        removeRow: function(el){
            $(el).closest('tr').remove();
            this.showHideButton();
        },
        dateRestrict: function(cnt){
            var to = $("#txtWedAniversary").datepicker({
                maxDate: '0d',
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-60: +0"
            });

            var from = $("#txtDateOfBirth").datepicker({
                minDate: new Date(1954, 1 - 1, 1), 
                maxDate: '-18Y', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-60:-18"
            });
            var father_dob = $("#txtFatherDob").datepicker({
                minDate: new Date(1944, 1 - 1, 1),
                maxDate: '-18Y', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-90:-18"
            });

            var mother_dob = $("#txtMotherDob").datepicker({
                minDate: new Date(1944, 1 - 1, 1),
                maxDate: '-18Y', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-90:-18"
            });

            $("#txtDateOfBirth" ).datepicker("option", "showAnim", "slideDown");
            $("#txtWedAniversary").datepicker("option", "showAnim", "slideDown");
            $("#txtFatherDob").datepicker("option", "showAnim", "slideDown");
            $("#txtMotherDob").datepicker("option", "showAnim", "slideDown");
            
        },
        getDate: function( element ) {
            var date;
            try {
                date = $(element).datepicker('getDate');
            } catch( error ) {
                date = null;
            }
            return date;
        },
        validation: function(){

            $.validator.messages.selectListItem = 'Language is required.';
            $.validator.addClassRules({drp: {selectListItem: "0"},});

            $("form#frm_personal_data").validate({
                // Specify validation rules
                rules: {
                    txtFullName: {
                        //lettersOnly: true,
                        required: true
                    },
                    txtDateOfBirth: {
                        required: true,
                        // check_date: 18
                    },
                    fupPhoto: {
                        required: function(){
                            return $('#hdnimagename').val() == ''
                        },
                        accept      : "image/png,image/jpeg,image/jpg",
                        filesize    : 1048576
                    },
                    
                    medicPhoto: {
                        required: function(){
                            return $('#hdnmcertificatename').val() == ''
                        },
                        accept      : "image/png,image/jpeg,image/jpg,application/pdf",
                        filesize    : 4194304
                    },
                    txtFatherName: {
                        required: true
                    },
                    txtMotherName: {
                        required: true
                    },
                    rbtGender: { selectListItem: "0" },
                    ddlBloodGroup: { selectListItem: "0" },
                    ddlNationality: { selectListItem: "0" },
                    ddlReligion: { selectListItem: "0" },
                    ddlMaritalStatus: { selectListItem: "0" },
                    txtWedAniversary: {
                        required: function(){

                            $('#ddlMaritalStatus option:selected').attr('code')

                            if($("#ddlMaritalStatus option:selected").attr('code') == 'M' || $("#ddlMaritalStatus option:selected").attr('code') == 'C'){
                                        return true;
                            }
                        },
                        // WedAnniversary:true
                    },
                    txtMobNo1: {
                        required: true,
                        maxlength: 10,
                    },
                    txtEmail: {
                        required: true,
                        email: true
                    },
                    txtFatherDob: {
                        required: true
                        
                    },
                    txtMotherDob: {
                        required: true
                    },
                    // txtAccountNo: {
                    //     required: true
                    // },
                    // txtBankName: {
                    //     required: true
                    // },
                    // txtIFSCcode: {
                    //     required: true
                    // },
                    
                    txtPresAddressLine1: "required",
                    txtPresAddressLine2: "required",
                    ddlPresentContry: { selectListItem: "0" },
                    ddlPresState: { selectListItem: "0" },
                    txtPresCity: "required",
                    txtPresPinCode: {
                        pincode: true,
                        required: true,
                        number: true,
                        maxlength: 6,
                    },
                    txtPermAddressLine1: "required",
                    txtPermAddressLine2: "required",
                    ddlPermCountry:  { selectListItem: "0" },
                    ddlPermstate: { selectListItem: "0" },
                    txtPermCity: "required",
                    txtPermPinCode: {
                        pincode: true,
                        required: true,
                        number: true,
                        maxlength: 6,
                    },
                    txtMobNo2: "required",
                    txtEmgrPer: "required",
                    txtEmgrPhn: "required",
                    linkedin_url: "required",
                    ddlEmgrRel: { selectListItem: "0" }, 
                    txtAccountNo: "required",
                    txtBankName: "required",
                    txtIFSCcode: "required", 

                },
                // success:function()
                // {
                //     $('#display-success').show();

                // },
                //Specify validation messages
                messages: {
                    txtFullName: { lettersOnly: 'Please do not use spaces and numbers', required: "Please provide your full name " },
                    txtFirstName: { lettersOnly: 'Please do not use spaces and numbers', required: "Please provide your first name " },
                    txtLastName: { lettersOnly: 'Please do not use spaces and numbers', required: "Please provide your last name " },
                    txtDateOfBirth: {
                        required: 'Please provide your date of birth.',
                        // check_date: "You are not old enough !! Your age must 18+ ."
                    },
                    fupPhoto: {
                        required: 'Please upload a Photo.',
                        accept  : "Only jpg,jpeg and png Image is Supported.",
                        filesize:  "Maximum allowed file size is 1 MB."
                    },
                    rbtGender: "Please select your gender",
                    ddlBloodGroup: { selectListItem: "Please select your blood group" },
                    ddlNationality: { selectListItem: "Please select your nationality" },
                    ddlReligion: { selectListItem: "Please select your religion" },
                    ddlMaritalStatus: { selectListItem: "Please provide your marital status" },
                    txtWedAniversary: {
                        required: 'Please provide your Wedding Anniversary',
                        // WedAnniversary:'How soon you got married !'
                    },
                    // fupPhoto: "Please upload your photo",
                    txtMobNo1: {
                        required: "Please provide your mobile number",
                        maxlength: 'Maximum length should must be 10 digit.'
                    },
                    txtMobNo2: {
                        required: "Please provide your whatsapp number",
                        maxlength: 'Maximum length should must be 10 digit.'
                    },
                    txtAccountNo: {
                        required:  "Please provide your personal account number",
                        maxlength: 'Maximum length should must be 15 digit.'
                    },
                    txtFatherName: "Please provide your father's name",
                    txtFatherDob: "Please provide your father's date of birth ",
                    txtMotherName: "Please provide your mother's name",
                    txtMotherDob: "Please provide your mother's date of birth",
                    txtBankName: "Please provide yourpersonal bank name",
                    txtIFSCcode: "Please provide your personal bank ifsc",
                    txtEmail: "Please enter a valid email address",
                    txtPresAddressLine1: "Please provide your present address 1",
                    txtPresAddressLine2: "Please provide your present address 2",
                    ddlPresentContry: { selectListItem: "Please select your present country" },
                    ddlPresState: { selectListItem: "Please select your present State" },
                    txtPresCity: "Please provide your Present city",
                    txtPresPinCode: {
                        required: "Please enter your pincode",
                        pincode: 'This is not a valid pincode .'
                    },
                    txtPermAddressLine1: "Please provide your Permanent address 1",
                    txtPermAddressLine2: "Please provide your Permanent address 2",
                    ddlPermCountry: { selectListItem: "Please select your Permanent country" },
                    ddlPermstate: { selectListItem: "Please select your Permanent State" },
                    txtPermCity: "Please provide your Permanent city",
                    txtPermPinCode: {
                        required: "Please enter your pincode",
                        pincode: 'This is not a valid pincode .'
                    },
                    txtEmgrPer: "Please provide emergency contact person",
                    txtEmgrPhn: {
                        required: "Please provide your mobile number",
                        maxlength: 'Maximum length should must be 10 digit.'
                    },
                    linkedin_url: {
                        required: "Please provide your LinkedIN URL",
                    },
                    ddlEmgrRel: { selectListItem: "Please select your relationship" },

                    // langdrpLanguage: { selectListItem: "Please choose your language" },
                },

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
            });  //End of form validation


        },
        select2: function(){
            $('select').select2();
            //$('.mdb-select').materialSelect();
            $('[data-rel="tooltip"]').tooltip();
        }
        
    };
    $(function(){
        personal.init();
    }); //end of ready function

    
}); // End of module

