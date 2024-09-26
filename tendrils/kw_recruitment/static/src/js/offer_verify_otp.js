odoo.define('kw_recruitment.kw_recruitment_offer_acceptance_button_redirect', function(require) { // how it works ??
    'use strict';
    var timer;
    var enroll = {
        init: function() {
            console.log("nit called ")
            enroll.startTimer(600);
        },
        startTimer: function(sec) {
//            console.log("timer called-------------------")
                // clearInterval(timer);
            $("#time_left").html("");
            var now = new Date().getTime();
            // console.log("now", now)
            var targetTime = sec * 1000;
            // console.log("targetTime", targetTime)
            var targetMs = now + targetTime;
            // console.log("targetMs", targetMs)
            timer = setInterval(function() {
                // console.log("inside interval.......")
                var now = new Date().getTime();
                // console.log("now", now)
                var distance = targetMs - now;
                // console.log("distance", distance)
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                // console.log("minutes", minutes)
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                // console.log("secondsv", seconds)
                // console.log(minutes + " m : " + seconds + " s ")

                // Output the result in an element with id="timeLeft"
                $("#time_left").html(minutes + " m : " + seconds + " s ");

                // If the count down is over, write some text 
                if (distance < 0) {
                    console.log("timer cleared")
                    clearInterval(timer);
                    $("#time_left").html("TIME EXPIRED");
                }
            }, 1000);
        },
        closeTimer: function() {
            clearInterval(timer);
        },
        showLoading: function() {
            $.blockUI({
                message: 'Loading...',
                fadeIn: 700,
                fadeOut: 1000,
                centerY: true,
                showOverlay: true,
                css: $.blockUI.defaults.grow1CSS
            });
        },
        hideLoading: function() {
            $.unblockUI();
        },

    };
    $(function() {
        // console.log("entered js----")
        $(document).on('click','#accept_download_offer_letter', function() {
            console.log("call download-------------------")
            var token = $('#offerApplicantToken').val();
            var find_name = $('#partner_name').text();
            var find_email = $('#applicant_email').text();
            var find_otp = $('#otpverification_download').val();
            // console.log("token=======",token,find_name,find_email,find_otp)
            if (find_otp == ''){
                $("#rmvid").text("Please enter the OTP.");
                return false;
            }
            var ajax = require('web.ajax');
            enroll.showLoading();
            ajax.jsonRpc("/recruitment/verify_offer_letter_download", 'call', {'token': token, 'otp': find_otp})
                .then(function(values) {
                    enroll.hideLoading();
                    if (values == 'invalid') {
                        $("#rmvid").text("Invalid OTP!");
                        // $("#resendotp").hide()
                    } else if (values == 'expired') {
                        $("#rmvid").text("Your OTP has been expired! Please give your Recent OTP.");
                    } else if (values == 'required') {
                        $("#rmvid").text("Please enter the OTP.");
                    } else {
                        $("#time_left").hide()
                        window.location.href = window.location.href+"?download=1";
                    }
                });
        });
        // console.log("resend otp===================")
        $('#resendotp_download_offer_letter').on('click', function() {    
            // var ajax = require('web.ajax');
            var find_name = $('#partner_name').text();
            var find_email = $('#applicant_email').text();
            // var find_otp = $('#otpverification_download').val();
            var token = $('#offerApplicantToken').val();
            // console.log("token resend otp=======",token,find_name,find_email)
            var ajax = require('web.ajax');
            enroll.showLoading();
            ajax.jsonRpc("/recruitment/send_otp/offer_letter", 'call', { 'name': find_name, 'email': find_email, 'token': token })
                .then(function(values) {
                    enroll.hideLoading();
                    if (values.success != 'yes') {
                        enroll.closeTimer();
                        // $("#rmvid").text('');
                        $("#desc").text("Your OTP has not been sent! Please, try again.");
                    } else {
                        // $('#txtOtpNum').val("");
                        // $("#rmvid").text('');
                        enroll.closeTimer();
                        enroll.startTimer(600);
                        $("#desc").text("OTP has been sent successfully!!");
                    }
                    // enroll.hideLoading();
                    console.log(values.success)
                });

        });
   
        // console.log("entered js----")

        $('#accept_offer_letter').on('click', function() {
            var token = $('#offerApplicantToken').val();
            var find_name = $('#partner_name').text();
            var find_email = $('#applicant_email').text();
            swal({
                text: "Are you sure to accept the offer letter?",
                icon: "success",
                dangerMode: true,
                closeOnClickOutside: false,
                closeModal: false,
                buttons: {
                    confirm: { text: 'Yes, Submit', className: 'btn-info' },
                    cancel: 'No'
                },
            }).then(function (isConfirm) {
                if (isConfirm) {
                    var ajax = require('web.ajax');
                    enroll.showLoading();
                    ajax.jsonRpc("/recruitment/verify_offer_letter", 'call', { 'name': find_name, 'email': find_email,
                    'token': token, 'otp': '' })
                        .then(function(values) {
                            if(values == 'success'){
                                window.location.href = "/recruitment/offer/accepted/";
                            }else{
                                enroll.hideLoading();
                                swal({ text: "Error !! Please try again later.", icon: "error", buttons: { cancel: 'OK' } })
                            }
                        });
                } else {
                    swal.close();
                }
            });
            return false;

        });

       $('input[type="radio"][name="offer_letter_decline"]').on('change', function() {
           var _el = $(this);
           if(_el.val() == 'Any other Reasons, Please specify'){
               $('#offer_letter_decline_reason').slideDown();
           }else{
               $('#offer_letter_decline_reason').slideUp();
           }
       });

       $('#offer_letter_decline_cancel').on('click', function() {
           $('input[type="radio"][name="offer_letter_decline"]').prop('checked', false);
           $('#offer_letter_decline_reason').slideUp();
           $("#offer_letter_decline_reasons").slideUp('slow');
           return false;
       });
       $('#decline_offer').on('click', function() {
           $("#offer_letter_decline_reasons").slideDown('slow');
           return false;
       });
        $('#offer_letter_decline_submit').on('click', function() {
            var reason = $('input[type="radio"][name="offer_letter_decline"]:checked').val();
            var token = $('#offerApplicantToken').val();
            var find_name = $('#partner_name').text();
            var find_email = $('#applicant_email').text();
            var other_reason = '';

            if(reason == 'Any other Reasons, Please specify') {
                other_reason = $('#offer_letter_decline_reason').val();
                console.log('Selected value for declining offer:', other_reason);
            }
            // console.log('Selected value for declining offer:', reason);
            swal({
                text: "Are you sure to decline the offer letter?",
                icon: "warning",
                dangerMode: true,
                closeOnClickOutside: false,
                closeModal: false,
                buttons: {
                    confirm: { text: 'Yes, Submit', className: 'btn-info' },
                    cancel: 'No'
                },
            }).then(function (isConfirm) {
                if (isConfirm) {
                    var ajax = require('web.ajax');
                    enroll.showLoading();
                    ajax.jsonRpc("/recruitment/decline_offer_letter", 'call', {
                        name:find_name, email:find_email, 'token': token, 'otp': '' ,'reason': reason,'other_reason': other_reason})
                        .then(function(values) {
                            if(values == 'success'){
                                window.location.href = "/recruitment/offer/declined/";
                            }else{
                                enroll.hideLoading();
                                swal({ text: "Error !! Please try again later.", icon: "error", buttons: { cancel: 'OK' } })
                            }
                        });
                } else {
                    swal.close();
                }
            });
            return false;

        });

        $('#resendotp').on('click', function() {
            var ajax = require('web.ajax');
            var find_name = $('#partner_name').text()
            var find_email = $('#applicant_email').text()
            var token = $('#offerApplicantToken').val();
            enroll.showLoading();
            ajax.jsonRpc("/recruitment/send_otp", 'call', { 'name': find_name, 'email': find_email, 'token': token })
                .then(function(values) {
                    if (values.success != 'yes') {
                        enroll.closeTimer();
                        // $("#rmvid").text('');
                        $("#desc").text("Your OTP has not been sent! Please, try again.");
                    } else {
                        // $('#txtOtpNum').val("");
                        // $("#rmvid").text('');
                        enroll.closeTimer();
                        enroll.startTimer(600);
                        $("#desc").text("OTP has been sent successfully!!");
                    }
                    enroll.hideLoading();
                    console.log(values.success)
                });

        });

        $('.txtvalid').keypress(function(evt) {
            if (evt.which < 48 || evt.which > 57) {
                evt.preventDefault();
            }
        });
        $('.closepage').on('click', function() {
            location.reload(true);
        });


        enroll.init();
    });

//    $(document).ready(function(){
//         enroll.init();
//    });
});