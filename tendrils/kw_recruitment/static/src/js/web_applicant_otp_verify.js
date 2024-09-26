odoo.define('kw_recruitment.kwrecruitment_intermediate_view', function (require) {  // how it works ??
    'use strict';
    var ajax = require('web.ajax');
    var find_mob = $('#txtMobNumber').val();
    var session = require('web.session');
    var enroll = {
        init: function(){},
        showLoading: function(){
            $.blockUI({
                message:'Loading...',
                fadeIn:700,
                fadeOut:1000,
                centerY:true,
                showOverlay:true,
                css:$.blockUI.defaults.grow1CSS
            });
            // console.log('1111111111111111111111111111111111111111111111111111111111')
        },
        hideLoading: function(){
            $.unblockUI();
        },
    };
    $(function () {
        // console.log('find_mob')
            $('#btnSubmitMobileno').on('click',function(){

                var find_mob = $('#txtMobNumber').val();
                var get_mobile1 = find_mob.substring(0,2);
                var get_mobile2 = find_mob.substring(7,10);
                // console.log("find_mob=====",find_mob)
                    if(find_mob=="")
                    {
                        $("#errspan").text("Please enter your registered mobile number.")
                        // alert("Enter Ref no");
                    }
                    else
                    {
                        enroll.showLoading();
                        var ajax = require('web.ajax');
                        ajax.jsonRpc("/searchMobNumber", 'call', {'user_input_mobile' :find_mob ,})
                            .then(function (values) {
                                // alert(values)
                                // console.log('values=================================',values)

                                var get_email = values
                                // var get_mobile1=find_mob
                                enroll.hideLoading();
                                if(values == 'status0')
                                {   
                                    $("#errspan").text("Invalid mobile number!")
                                }
                                else if(values == 'status1')
                                {
                                    $("#errspan").text("You were already enrolled as a Employee. Please contact to HR.")
                                }
                                else if(values == 'status2')
                                {
                                    $("#errspan").text("Your details have already been submitted.")
                                }
                                else
                                {
                                    $('#OTPnumber').modal({backdrop: 'static', keyboard: false})
                                    // var w = window.open('','','width=300,height=100,top=100, left=1500')
                                    // // w.moveTo(1500, 100);
                                    // w.document.write("OTP has been send to your <br>Mobile no :"+"<span style='color:red;'>"+ "*******"+get_mobile1+"</span>"+"<br>Email : "+"<span style='color:red;'>"+get_email+"</span>" )
                                    // w.focus()
                                    // setTimeout(function() {w.close();}, 3000)
                                    $("#desc").html("OTP has been send to your <br> Mobile No :"+get_mobile1 +"*****"+get_mobile2+"<br>Email : "+get_email );
                                    // $("#desc").html("OTP has been send to your <br>Email : "+get_email );
                        
                                    // tempAlert("OTP has been send to your <br> Mobile no : *******"+get_mobile1 +"<br>Email : "+get_email,2000);
                                    $("#errspan").text("")
                                    startTimer(600);
                                    maxTiesCount()
                                    // $("#resendotp").hide()
                                }
                                // console.log(values)
                        }); 

                        ajax.jsonRpc("/getmaxtries", 'call', {'user_input_mobile' :find_mob ,})
                            .then(function (values) {
                                // console.log("indexed values====",values)
                                if (values[1] == true){
                                    // console.log("if block-----");
                                    $("#try_after_block,#display_login_again").hide();
                                    $("#otp_button_action,#enter_otp_for_verification,#time_lable,#time_left,#btnSubmit,#resendotp,#max_attempt,#max_attempt_lable,#desc").show();
                                    closeRestrictTimer();
                                    startTimer(600);
                                }
                                else if (values[0]){
                                    // console.log("elif block-----")
                                    $("#max_attempt").text(values[0]);
                                }
                                else{
                                    // console.log("else--block---")
                                    $("#max_attempt").text(0);
                                    
                                }
                            });
                    }
            })

            const demo = $('#hidden_field_val').val()
            const auth_secret_key = demo
            $('#btnSubmit').on('click',function(){
                // console.log("buton submit---")
                var find_otp = $('#txtOtpNum').val();
                var find_mob = $('#txtMobNumber').val();
                // OTP encription on submission
                // const auth_secret_key = generateAESEncryptKey(32);
                // console.log("inputField======",auth_secret_key);
                // hex value conversion
                const key = CryptoJS.enc.Hex.parse(auth_secret_key);
                // Trying to convert the object to JSON
                // Encryption
                const encrypted = CryptoJS.AES.encrypt(find_otp, key, {
                    mode: CryptoJS.mode.ECB,
                    padding: CryptoJS.pad.Pkcs7,
                });
                // console.log("Your OTP is :",find_otp)
                // console.log("Your ph is :",find_mob)
                enroll.showLoading();
                var ajax = require('web.ajax');
                ajax.jsonRpc("/searchOTPno", 'call', {'otp':encrypted.toString()})
                    .then(function (values) {
                        enroll.hideLoading();
                        // alert(values)
                        // if(values == 'restrictLogin'){
                        //     restrictTimer(3600)
                        // }
                        // else 
                        if(values == 'status0')
                        {
                            maxTiesCount()
                            $("#rmvid").text("Invalid OTP!");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status1')
                        {
                            maxTiesCount()
                            $("#rmvid").text("Your OTP has been expired! Please give your Recent OTP.");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status2')
                        {
                            maxTiesCount()
                            $("#rmvid").text("Sorry, Invalid OTP !");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status3')
                        {
                            maxTiesCount()
                            $("#rmvid").text("Your time has been expired! Please resend to move forward.");
                            // $("#resendotp").show()
                        }
                        else
                        {
                            // console.log("value===============",values)
                            closeRestrictTimer()
                            $("#time_left").hide()
                            $("#rmvid").text(" Congrats !! Welcome to CSM Technologies !!");
                            // console.log("value====after otp validate=================",values)
                            window.location.href = "/receducationaldata/";
                        }
                    });
            });
            
            $('#resendotp').on('click',function(){
                var find_mob = $('#txtMobNumber').val();
                var get_mobile1 = find_mob.substring(0,2);
                var get_mobile2 = find_mob.substring(7,10);
                enroll.showLoading();
                var ajax = require('web.ajax');
                ajax.jsonRpc("/searchMobNumber", 'call', {'user_input_mobile' :find_mob})
                    .then(function (values) {
                        
                        // alert(values)
                        var get_email = values
                        if(!values )
                        {
                            closeTimer();
                            $("#rmvid").text('');
                            $("#desc").text("Your OTP has not been sent! Please, try again.");
                            // $("#resendotp").show()
                        }
                        else
                        {
                            $('#txtOtpNum').val("");
                            $("#rmvid").text('');
                            closeTimer();
                            startTimer(600);
                            maxTiesCount()
                            $("#desc").html("OTP has been send successfully to your <br> Mobile No :"+get_mobile1 +"*****"+get_mobile2+"<br>Email : "+get_email );
                            // $("#desc").text("OTP has been sent successfully to "+get_email);
                            // tempAlert("hii",3000);
                            $.unblockUI();
                            // $("#resendotp").hide()
                        }
                        // console.log(values)
                    });
                    
            });
            $('.txtvalid').keypress(function(evt){
                if (evt.which < 48 || evt.which > 57)
                {
                    evt.preventDefault();
                }
            });
            $('.closepage').on('click',function(){
                location. reload(true);
            });


            //   Timer Function : Start....
            var timer;
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
                            $("#time_left").html("TIME EXPIRED");
                            $("#try_after_block").hide();
                        }
                    });
                
            }
            function closeTimer(){
                clearInterval(timer);
            }
            function maxTiesCount() {
                var ajax = require('web.ajax');
                var find_mob = $('#txtMobNumber').val();
                ajax.jsonRpc("/getmaxtries", 'call', {'user_input_mobile' :find_mob})
                    .then(function (count) {
                        // console.log("count-------",count)
                        // max_attempt = count
                        if (count[0] > 0 || count[1] == true){
                            // console.log("show");
                            $("#max_attempt").text(count[0]);
                            $("#try_after_block,#display_login_again").hide();
                            $("#otp_button_action,#enter_otp_for_verification,#time_lable,#time_left,#btnSubmit,#resendotp,#max_attempt,#max_attempt_lable,#desc").show();
                        }
                        else{
                            // console.log("hide");
                            closeTimer();
                            $("#max_attempt").text(0);
                            $("#try_after_block,#otp_alert,#real_time").show();
                            $("#otp_alert").text("Security Alert - Multiple Incorrect OTP Attempts Detected");
                            $("#otp_button_action,#enter_otp_for_verification,#time_lable,#time_left,#btnSubmit,#resendotp,#max_attempt,#max_attempt_lable,#desc").hide();
                            $("#real_time").text(count[2]);
                            restrictTimer(count[3]);
                        }
                    });
            }
            var restrict_timer;
            function restrictTimer(sec) {
                    // clearInterval(timer);
                    $("#freezed_screen_time").html("");
                    var now = new Date().getTime();    
                    var targetTime = sec * 1000;
                    var targetMs = now + targetTime;  
                    restrict_timer = setInterval(function() { 

                        var now = new Date().getTime();        
                        var distance = targetMs - now;
                        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

                        // Output the result in an element with id="timeLeft"
                        $("#freezed_screen_time").html(minutes + " m : " + seconds + " s ");
                        
                        // If the count down is over, write some text 
                        if (distance < 0) {
                            clearInterval(restrict_timer);
                            closeTimer()
                            $("#display_login_again").html("You can login again.");
                            $("#rmvid").text("");
                            $("#try_after_block,#desc,#otp_alert,#real_time").hide()
                            $("#otp_button_action,#enter_otp_for_verification,#time_lable,#time_left,#btnSubmit,#resendotp,#max_attempt,#max_attempt_lable,#display_login_again").show();
                            startTimer(600);
                            var find_mob = $('#txtMobNumber').val();
                            // console.log("find_mob====",find_mob)
                            ajax.jsonRpc("/getmaxtries", 'call', {'user_input_mobile' :find_mob})
                                .then(function (values) {
                                    // console.log("time ends ====",values)
                                    if (values[0]){
                                        // console.log("elif block-time----")
                                        $("#max_attempt").text(values[0]);
                                    }
                                    else{
                                        // console.log("else--block--time-")
                                        $("#max_attempt").text(0);
                                        
                                    }
                                });
                        }
                    });
                
            }
            function closeRestrictTimer(){
                clearInterval(restrict_timer);
            }

    }); 
    
});