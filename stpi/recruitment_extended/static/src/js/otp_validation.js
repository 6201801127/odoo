odoo.define('recruitment_extended.website_hr_recruitment_email', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var otp = {
        init: function () {
            $(document).on("click", '#send_otp', function () {
                var email = $("#u_email").val();
                var atposition = email.indexOf("@");
                var dotposition = email.lastIndexOf(".");
                if (atposition < 1 || dotposition < atposition + 2 || dotposition + 2 >= email.length) {
                    alert("Please enter a valid e-mail address.");
                    return false;
                }
                else {
                    console.log("Email :", email)
                    ajax.jsonRpc("/searchEmail", 'call', { 'email': email, })
                        .then(function (values) {
                            console.log(values)
                            if (values['state'] == '200') {
                                document.getElementById("u_email").disabled = true;
                                document.getElementById("otp_validation").disabled = false;
                                document.getElementById("otp").disabled = false;
                                if ($("#send_otp").html() == 'Generate OTP') {
                                    $("#send_otp").html("Resend OTP");
                                    $("#send_otp").prop('class', 'btn btn-primary btn-md');
                                }
                                document.getElementById("otp_msg").innerHTML = '<b class="mt-2 ml-2">Please check your email and put the OTP in the above textbox.</b>'
                            }
                        });
                }
            });

            $(document).on("click", '#otp_validation', function () {
                var email = $("#u_email").val();
                var otp = $("#otp").val();
                // var job = $("#job").val();
                var apply_url = $("#apply_url").val();
                if (otp == ''){
                    alert("Please enter OTP.")
                }
                else if (email && otp) {
                    console.log("Email :", email, "OTP :", otp)
                    ajax.jsonRpc("/validateOTP", 'call', { 'email': email, 'otp': otp })
                        .then(function (values) {
                            console.log(values)
                            if (values['state'] == '200') {
                                window.location.href = apply_url
                            }
                            else {
                                document.getElementById("otp_msg").innerHTML = '<b class="text-danger mt-2 ml-2">Invalid OTP !</b>';
                            }
                        });
                }
            });
        },

    };

    $(function () {
        otp.init();
    });
});