odoo.define('restrict_logins.login_clear_session', function (require) {  // how it works ??
    'use strict';

    var ajax = require('web.ajax');
    var timer;

    var restrict = {
        generate_otp: function(user_name, failed_uid){
            restrict.showLoading();
            ajax.jsonRpc("/auth/generate-otp", 'call',{'uname' : user_name,'fuid' : failed_uid })
                .then(function (values) {
                    restrict.hideLoading();
                    console.log(values);
                    if(!values )
                    {
                        closeTimer();
                        $(".modal-content #otptxt").text('');
                        $(".modal-content #desc").html("Your OTP has not been sent! Please, try again.");
                    }
                    else
                    {
                        var usr_id = values[0];
                        var mobile = values[1] && typeof values[1] != 'undefined' ? "<br>Mobile No.:"+values[1] : '';
                        var email = typeof values[2] != 'undefined' ? "<br>Email: "+values[2] : '';
                        $(".modal-content #uid").val( usr_id );
                        $(".modal-content #umobile").val( mobile );
                        $(".modal-content #txtOtpNum").val('');
                        $(".modal-content #otptxt").text('');
                        $(".modal-content #desc").html("OTP has been send to your "+mobile+""+email );
                        $('#restrict_login_otp').modal({ backdrop:'static',keyboard:false });
                        closeTimer();
                        startTimer(600);
                    }
                });
        },
        validate_otp: function(otp, failed_uid, user_name){
            ajax.jsonRpc("/auth/validate-otp", 'call',{'otpnum' : otp, 'fuid' : failed_uid, 'uname': user_name})
                .then(function (values) {
                    status = values[0]
                    console.log(status)
                    console.log(typeof status)
                    if(status == 'status0')
                    {
                        $("#otptxt").text("Invalid OTP!");
                    }
                    else if(status == 'status1')
                    {
                        $("#otptxt").text("Your time has been expired! Please resend to move forward.");
                    }
                    else if(status == 'status2')
                    {
                        var user = values[1]
                        $("#otptxt").text("OTP has been verified successfully! Please try login now.");
                        window.setTimeout(function() {
                            window.location.href = window.location.origin + "/clear_all_sessions?f_uid="+user;
                        }, 2000);
                    }
                });
        },
        showLoading: function(){
            $.blockUI({
                message:'Loading...',
                fadeIn:700,
                fadeOut:1000,
                centerY:true,
                showOverlay:true,
                css:$.blockUI.defaults.grow1CSS
            });
        },
        hideLoading: function(){
            $.unblockUI();
        },
    };

    function startTimer(sec) {
        // clearInterval(timer);
        $("#time_left").html("");
        var now = new Date().getTime();
        var targetTime = sec * 1000;
        var targetMs = now + targetTime;
        timer = setInterval(function() {

            var now = new Date().getTime();
            var distance = targetMs - now;
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Output the result in an element with id="timeLeft"
            $("#time_left").html(minutes + " m : " + seconds + " s ");

            // If the count down is over, write some text
            if (distance < 0) {
                clearInterval(timer);
                $("#time_left").html("TIME EXPIRED!");
            }
        });

    }
    function closeTimer(){
        clearInterval(timer);
    }

    $(function () {
        $('#btnSubmitMobile').on('click', function () {
            var user_name = $('#login').val();
            var failed_uid = $('#fuid').val();
            restrict.generate_otp(user_name, failed_uid);
        });

        $('#resendotp').on('click',function(){
            var user_name = $('#login').val();
            var failed_uid = $('#uid').val();
            restrict.generate_otp(user_name, failed_uid);
        });
        
        $('#OTPSubmit').on('click', function () {
            var otp = $('#txtOtpNum').val();
            var failed_uid = $('#fuid').val();
            var user_name = $('#login').val();
            restrict.validate_otp(otp, failed_uid, user_name);
        });
    });
});