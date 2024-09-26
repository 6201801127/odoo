odoo.define('recruitment_extended.website_hr_recruitment_templates', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var goals = {
        init: function () {
            $("#applicable_fee").change(function() {
                if (this.value == 'Yes') $('.enter-applicable-fee, .payment-document, .payment-details').removeClass('d-none');
                else $('.enter-applicable-fee, .payment-document, .payment-details').addClass('d-none');

            });

            $("#address_details").on('change',"select[id^='country_']",(event) => {
                let select_id = event.target.id; // country_1,country_2.. etc
                let dynamic_id = select_id.split('_')[1]; // 1,2... etc
                let dynamic_state_element = $("#state_"+dynamic_id);
                dynamic_state_element.empty();
                dynamic_state_element.append($("<option></option>").attr("value", "0").text("Select"));
                let country_id = event.target.value;
                let params = {country_id : country_id}
                ajax.jsonRpc("/get_country_state/", 'call', params).then( (response) => {
                for(const element of response){
                    dynamic_state_element.append($("<option></option>").attr("value", element[0]).text(element[1]));
                    }
                });
            });

            $("#address_details").on('change',"select[id^='state_']",(event) => {
                let select_id = event.target.id; // state_1,state_2.. etc
                let dynamic_id = select_id.split('_')[1]; // 1,2... etc
                let dynamic_city_element = $("#city_district_"+dynamic_id);
                dynamic_city_element.empty();
                dynamic_city_element.append($("<option></option>").attr("value", "0").text("Select"));
                let state_id = event.target.value;
                let params = {state_id : state_id}
                ajax.jsonRpc("/get_state_city/", 'call', params).then( (response) => {
                for(const element of response){
                    dynamic_city_element.append($("<option></option>").attr("value", element[0]).text(element[1]));
                    }
                });
            });
            
            $( "#gender, #category" ).change(function() {
                var gender = $("#gender").val();
                var category = $("#category").val();
                var published_advertisement = $("#published_advertisement_id").val();
                ajax.jsonRpc("/applicant_fees", 'call', {'published_advertisement_id':published_advertisement,'gender' :gender,'category':category})
                    .then(function (fees) {
                        if (fees >0){
                            $("#applicable_fee").val("Yes");
                            $("#applicable_fee").prop('disabled', true);
                            $("#enter_applicable_fee").prop('disabled', true);
                            $("#enter_applicable_fee").val(fees);
                            $('.enter-applicable-fee, .payment-document, .payment-details').removeClass('d-none');
                        }else{
                            $("#applicable_fee").val("No");
                            $("#enter_applicable_fee").val(0);
                            $('.enter-applicable-fee, .payment-document, .payment-details').addClass('d-none');
                        }
                });

            });

            function readURL(input) {
                if (input.files && input.files[0]) {
                    if (input.files[0].size > 1 * 1024 * 1024){
                        alert('Maximum size of image should be 1MB.')
                    }
                    else {

                        var reader = new FileReader();
                        reader.onload = function(e) {
                            $('#imagePreview').css('background-image', 'url('+e.target.result +')');
                            $('#imagePreview').hide();
                            $('#imagePreview').fadeIn(650);
                        }
                        reader.readAsDataURL(input.files[0]);
                    }
                }
            };
            
            $("#imageUpload").change(function() {
                readURL(this);
            });

            $('#pan_no').keyup(function () {
                $(this).val($(this).val().toUpperCase());
            });
            
            $(document).ready(function () {
                document.getElementById("cardNo").value = document.getElementById("aadhar_no").value;
            });

            $(document).on('submit', '#recruitment_form', function () {
                $("form#recruitment_form").validate({
                    rules: {
                        partner_salutation: {
                            required: true
                        },
                        partner_first_name: "required",
                        // partner_middle_name: "required",
                        partner_last_name: "required",
                        mobile: {
                            required: true,
                            minlength: 10
                        },
                        cardNo: {
                            required: true,
                            minlength: 12
                        },
                        pan_no: {
                            // required: true,
                            minlength: 10
                        },
                        dob: {
                            required: true,
                            date: true
                        },
                        gender: "required",
                        nationality: "required",
                        category: "required",
                        religion: "required",
                        kind_of_disability: {
                            required: function(element) {
                                return $("#physically_handicapped").val() == 'yes' && !$("#kind_of_disability").val();
                            }
                        },
                        perc_disability: {
                            required: function(element) {
                                return $("#physically_handicapped").val() == 'yes';
                            }
                        },
                        upload_certificate_upload: {
                            required: function(element) {
                                return $("#physically_handicapped").val() == 'yes' && $(".hidden-certificate-upload").length == 0;
                            }
                        },
                        enter_applicable_fee: {
                            required: function(element) {
                                return $("#applicable_fee").val() == 'Yes';
                            }
                        },
                        upload_other_documents: {
                            required: function(element) {
                                return $("#applicable_fee").val() == 'Yes';
                            }
                        },
                        payment_details:{
                            required: function(element) {
                                return $("#applicable_fee").val() == 'Yes' && !$("#payment_details").val().trim();
                            }
                        },
//                        upload_signature: {
//                            required: function(element) {
//                                return $("#upload_signature").val() == '' && $(".hidden-signature").length == 0;
//                            }
//                        },
                        // upload_dob_doc:{
                        //     required: function(element) {
                        //         return $("#upload_dob_doc").val() == '' && $(".hidden-dob-doc").length == 0;
                        //     }
                        // },
                        upload_aadhar_upload:{
                            required: function(element) {
                                return $("#upload_aadhar_upload").val() == '' && $(".hidden-aadhar-upload").length == 0;
                            }
                        },
                        // upload_pan_upload:{
                        //     required: function(element) {
                        //         return $("#upload_pan_upload").val() == '' && $(".hidden-pan-upload").length == 0;
                        //     }
                        // },
                        upload_nationality_upload:{
                            required: function(element) {
                                return $("#nationality").val() != '' && ($("#nationality option:selected").text()).toUpperCase() != 'INDIAN' && $(".hidden-nationality-upload").length == 0;
                            }
                        }
                    },
                    messages: {
                        partner_salutation: { required: "Please specify your salutation." } ,
                        partner_first_name: { lettersonly: 'Digits are not allowed', required: "Please specify your first name. " },
                        // partner_middle_name: { lettersonly: 'Digits are not allowed', required: "Please specify your middle name. " },
                        partner_last_name: { lettersonly: 'Digits are not allowed', required: "Please specify your last name. " },
                        mobile: {minlength:"Please specify your 10 digits modile number.", required: "Please specify your mobile no. "},
                        cardNo: {minlength:"Please specify your 12 digits Aadhar number.", required: "Please specify your Aadhar no. "},
                        pan_no: {
                            minlength:"PAN number length should be 10.",
//                            required: "Please specify your PAN no. "},
                        },
                        gender: {required: "Please specify your Gender. "}, 
                        dob: {required: "Please specify your Date of Birth. "},
                        nationality: {required: "Please specify your nationality. "},
                        category: {required: "Please specify your Category. "},
                        religion: {required: "Please specify your Religion. "},
                        kind_of_disability: {required: "Please select kind of disability."},
                        perc_disability: {required: "Please specify % of disability."},
                        upload_certificate_upload: {required: "Please upload your document for disability."},
                        enter_applicable_fee: {required: "Please specify applicable fee. "},
                        upload_other_documents: {required: "Please upload your payment document."},
                        payment_details:{required: "Please enter payment details."},
//                        upload_signature: {required: "Please upload your signature."},
                        upload_dob_doc:{required:"Please upload date of birth document."},
                        upload_aadhar_upload:{required:"Please upload aadhaar document."},
                        upload_pan_upload:{required:"Please upload PAN document."},
                        upload_nationality_upload:{required:"Please upload nationality document."},
                    },
                    errorElement: "div",
                    highlight: function (element) {
                        $(element).css('background', '#ffdddd');
                    },
                    unhighlight: function (element) {
                        $(element).css('background', '#ffffff');
                    }
                });
                if($("#recruitment_form").valid())
                {
                    var reg = '^[A-Za-z]{5}[0-9]{4}[A-Za-z]$'
                    if(($('#imageUpload').val() == '') && ($('#imagePreview').attr('exist_image') == 'no')){
                        alert("Please upload your image.")
                    }
                    if($('#educational_details tbody tr').length == 1)
                    {
                        alert("Please add your educational qualification.")
                    }
//                    else if(!$("#pan_no").val().match(reg)){
//                        alert("Please enter correct PAN Card Number.")
//                    }
                    // else if($('#experience_details tbody tr').length == 1)
                    // {
                    //     alert("Please add your employment details.")
                    // }
                    else if($("#age_required").val()== '1'){
                        var birthDayDate = $("#dob").val();
                        var min_age = parseInt($("#min_age").val());
                        var max_age = parseInt($("#max_age").val());

                        const ageInYears = moment().diff(new Date(birthDayDate), 'years');
                        if (!(ageInYears >= min_age && ageInYears <= max_age)){
                            alert("Your age is "+ageInYears+". Minimum age required is "+min_age + " and maximum age required is "+max_age);
                        }
                        else{
                            goals.submit('submit');
                        }
                    }
                    else{
                        goals.submit('submit');
                    }
                }
            });

            $('#hr_recruitment_save_as_draft_button').click(function () {
                // if($("#recruitment_form").valid())
                // {   
                //     if(($('#imageUpload').val() == '') && ($('#imagePreview').attr('exist_image') == 'no')){
                //         alert("Please upload your image.")
                //     }
                //     else if($('#educational_details tbody tr').length == 1)
                //     {
                //         alert("Please add your educational qualification.")
                //     }
                //     else if($('#experience_details tbody tr').length == 1)
                //     {
                //         alert("Please add your employment details.")
                //     }
                //     else{
                
                goals.submit('draft');
                
                    // }
                // }
            });
        },
        
        get_education_details: function () {
            var education = []
            var count = 0

            if ($('#educational_details tbody tr').length > 0) {
                $("#educational_details tbody tr").each(function () {
                    if (this.id != 'tr_0') {
                        var certificateBase64 = '';
                        var certificateName = '';
                        if($(this).find('td:nth-child(7) > input ').attr('filedata')){
                            certificateBase64 = $(this).find('td:nth-child(7) > input ').attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                            certificateName = $(this).find('td:nth-child(7) > input ').attr('filename').replace(/"/g, "");
                        }
                        else if (!$(this).find('td:nth-child(7) > input ').attr('filedata')){
                            certificateBase64 = $(this).find('td:nth-child(7) > input ').closest('td').find('.hidden-certificate').attr('filedata');
                            certificateName = $(this).find('td:nth-child(7) > input ').closest('td').find('.hidden-certificate').attr('filename');
                        }
                        var educations_values = {}
                        var grade = $(this).find('td:first-child > input').val();
                        var field = $(this).find('td:nth-child(2) > input ').val();
                        var stream = $(this).find('td:nth-child(3) > input ').val();
                        var school_name = $(this).find('td:nth-child(4) > input ').val();
                        var passing_year = $(this).find('td:nth-child(5) > input ').val();
                        var percentage = $(this).find('td:nth-child(6) > input ').val();
                        var certificate = certificateBase64;
                        var certificate_name = certificateName;
                        
                        console.log(certificate)
                        // if ($(this).find('td:nth-child(6) > input').is(':checked')) {
                        //     high_edu = true
                        //     count++;
                        // }

                        educations_values["grade"] = grade
                        educations_values["field"] = field
                        educations_values["stream"] = stream
                        educations_values["school_name"] = school_name
                        educations_values["passing_year"] = passing_year
                        educations_values["percentage"] = percentage
                        educations_values["certificate"] = certificate
                        educations_values["file_name"] = certificate_name
                        education.push(educations_values)
                    }

                })
            }
            // if (count > 1){
            //     alert("Maximum 1 higher education allowed.")
            //     return false;
            // }
            return education
        },

        get_experience_details: function () {
            var experience = []

            if ($('#experience_details tbody tr').length > 0) {
                $("#experience_details tbody tr").each(function () {
                    if (this.id != 'tr_0') {
                        var experience_values = {}
                        var documentBase64 = '';
                        var documentName = '';
                        var from_date = $(this).find('td:first-child > input ').val();
                        var to_date = $(this).find('td:nth-child(2) > input ').val();
                        var employer_name_address = $(this).find('td:nth-child(3) > input').val();
                        var position_held = $(this).find('td:nth-child(4) > input ').val();
                        var job_description = $(this).find('td:nth-child(5) > textarea ').val();
                        // var reason = $(this).find('td:nth-child(5) > input ').val();
                        var pay_scale = $(this).find('td:nth-child(6) > input ').val();
                        if($(this).find('td:nth-child(7) > input ').attr('filedata')){
                            documentBase64 = $(this).find('td:nth-child(7) > input ').attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                            documentName = $(this).find('td:nth-child(7) > input ').attr('filename').replace(/"/g, "");
                        }
                        else if (!$(this).find('td:nth-child(7) > input ').attr('filedata')){
                            documentBase64 = $(this).find('td:nth-child(7) > input ').closest('td').find('.hidden-experience-doc').attr('filedata');
                            documentName = $(this).find('td:nth-child(7) > input ').closest('td').find('.hidden-experience-doc').attr('filename');
                        }

                        experience_values["from_date"] = from_date
                        experience_values["to_date"] = to_date
                        experience_values["employer_name_address"] = employer_name_address
                        experience_values["position_held"] = position_held
                        experience_values["job_description"] = job_description
                        experience_values["pay_scale"] = pay_scale
                        experience_values["document"] = documentBase64;
                        experience_values["document_name"] = documentName;
                        // experience_values["reason"] = reason
                        experience.push(experience_values)
                    }

                })
            }
            return experience
        },

        get_address_details: function () {
            var address = []

            if ($('#address_details tbody tr').length > 0) {
                $("#address_details tbody tr").each(function () {
                    if (this.id != 'tr_0') {
                        var address_values = {}
                        var address_type = $(this).find('td:first-child > select').val();
                        var address_one = $(this).find('td:nth-child(2) > textarea ').val();
                        var address_two = $(this).find('td:nth-child(3) > textarea ').val();
                        var city = $(this).find('td:nth-child(4) > select ').val();
                        var state = $(this).find('td:nth-child(5) > select ').val();
                        var country = $(this).find('td:nth-child(6) > select ').val();
                        var pincode = $(this).find('td:nth-child(7) > input ').val();

                        address_values["address_type"] = address_type
                        address_values["address_one"] = address_one
                        address_values["address_two"] = address_two
                        address_values["city"] = city
                        address_values["state"] = state
                        address_values["country"] = country
                        address_values["pincode"] = pincode
                        address.push(address_values)
                    }

                })
            }
            // if (count > 1){
            //     alert("Maximum 1 higher education allowed.")
            //     return false;
            // }
            return address
        },

        submit: function (value) {

            var educational_details = goals.get_education_details();
            var experience_details = goals.get_experience_details();
            var address_details = goals.get_address_details();
            var image_base64 = $("#imagePreview").css('background-image');
            var image_data = image_base64.replace("url(\"data:","").replace('\")',"").split('base64,')[1];

            var params = {
                image : image_data,
                salutation: $('#partner_salutation').val(),
                partner_first_name: $('#partner_first_name').val(),
                partner_middle_name: $('#partner_middle_name').val(),
                partner_last_name: $('#partner_last_name').val(),
                father_name: $("#applicant_father_name").val(),
                mother_name: $("#applicant_mother_name").val(),
                email_from: $("#email_from").val(),
                mobile: $("#mobile").val(),
                phone_with_area_code : $("#phone_with_area_code").val(),
                aadhar_no: $("#aadhar_no").val(),
                pan_no: $("#pan_no").val(),
                dob: $("#dob").val(),
                gender : $("#gender").val(),
                nationality: $("#nationality").val(),
                category: $("#category").val(),
                religion : $("#religion").val(),
                ex_service: $("#ex_service").val(),
                govt_employee : $("#govt_employee").val(),
                physically_handicapped: $('#physically_handicapped').val(),
                kind_of_disability: $('#kind_of_disability').val(),
                perc_disability: $('#perc_disability').val(),
                address_details: address_details,
                image:image_data,
                educational_details:educational_details,

                achievements:$("#achievements").val(),
                experience_details: experience_details,
                
                additional_information : $("#additional_information").val(),
                penalty_last_10_year:$("#penalty").val(),
                inquiry_going_on:$("#action_injury").val(),
                criminal_case_pending:$("#criminal_vigilance").val(),
                relative_ccs:$("#relative_ccs").val(),
                relative_ccs_name:$("#relative_ccs_name").val(),
                applicable_fee: $("#applicable_fee").val(),
            }
//            if ($("#upload_signature").attr('filedata')){
//                params.signature = $("#upload_signature").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
//                params.signature_filename = $("#upload_signature").attr('filename').replace(/"/g, "");
//            }else{
//                params.signature = $(".hidden-signature").attr('filedata');
//                params.signature_filename = $(".hidden-signature").attr('filename');
//            }

            if ($("#other_document").attr('filedata')){
                params.other_doc = $("#other_document").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.other_doc_file_name = $("#other_document").attr('filename').replace(/"/g, "");
            }else{
                params.other_doc = $(".hidden-other-doc").attr('filedata');
                params.other_doc_file_name = $(".hidden-other-doc").attr('filename');
            }
            
            if ($("#upload_dob_doc").attr('filedata')){
                params.dob_doc = $("#upload_dob_doc").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.dob_doc_file_name = $("#upload_dob_doc").attr('filename').replace(/"/g, "");
            }else{
                params.dob_doc = $(".hidden-dob-doc").attr('filedata');
                params.dob_doc_file_name = $(".hidden-dob-doc").attr('filename');
            }

            if ($("#upload_aadhar_upload").attr('filedata')){
                params.aadhar_upload = $("#upload_aadhar_upload").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.aadhar_upload_filename = $("#upload_aadhar_upload").attr('filename').replace(/"/g, "");
            }else{
                params.aadhar_upload = $(".hidden-aadhar-upload").attr('filedata');
                params.aadhar_upload_filename = $(".hidden-aadhar-upload").attr('filename');
            }

            if ($("#upload_pan_upload").attr('filedata')){
                params.pan_upload = $("#upload_pan_upload").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.pan_upload_filename = $("#upload_pan_upload").attr('filename').replace(/"/g, "");
            }else{
                params.pan_upload = $(".hidden-pan-upload").attr('filedata');
                params.pan_upload_filename = $(".hidden-pan-upload").attr('filename');
            }

            if ($("#upload_certificate_upload").attr('filedata')){
                params.certificate_upload = $("#upload_certificate_upload").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.certificate_upload_filename = $("#upload_certificate_upload").attr('filename').replace(/"/g, "");
            }else{
                params.certificate_upload = $(".hidden-certificate-upload").attr('filedata');
                params.certificate_upload_filename = $(".hidden-certificate-upload").attr('filename');
            }

            if ($("#upload_nationality_upload").attr('filedata')){
                params.nationality_upload = $("#upload_nationality_upload").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.nationality_upload_filename = $("#upload_nationality_upload").attr('filename').replace(/"/g, "");
            }else{
                params.nationality_upload = $(".hidden-nationality-upload").attr('filedata');
                params.nationality_upload_filename = $(".hidden-nationality-upload").attr('filename');
            }

            if (params.applicable_fee == "Yes"){
                params.fees_amount = $("#enter_applicable_fee").val();
                params.payment_details = $("#payment_details").val();
                params.payment_document = $("#upload_other_documents").attr('filedata').replace("url(\"data:","").replace('\")',"").split('base64,')[1];
                params.payment_filename = $("#upload_other_documents").attr('filename');
            }

            if (value == 'draft') {
                params['to_do'] = 'draft'
            }
            else {
                params['to_do'] = 'submit'
            }

            console.log("Submitting Data");
            $('#hr_recruitment_button').attr('disabled','disabled');
            var advertisement_slug = $("#advertisement_slug").val();
            ajax.jsonRpc("/website_form/submit/"+advertisement_slug, 'call', params).then(function (response) {
                // alert(response.success);
                if (response.success == true)
                {
                    $('#hr_recruitment_button').attr('disabled','disabled');
                    alert("Your data has been saved successfully.");
                    window.location.href = response.url
                }
                else {
                    $('#hr_recruitment_button').removeAttr('disabled');
                    console.log(response);
                }
            });
        },
    };

    $(function () {
        goals.init();
    });
});