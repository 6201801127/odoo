odoo.define('kw_onboarding_process.kwonboard_intermediate_view', function (require) {  // how it works ??
    'use strict';
    console.log("jjjjjjjjjjjjjjjjjjjjjj")
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
        },
        hideLoading: function(){
            $.unblockUI();
        },
    };
    $(function () {
            $('#btnSubmitMobile').on('click',function(){
                console.log("jjjjjjjjjjjjjjjjjjjjjj")
                var find_mob = $('#txtMobNum').val();
                var get_mobile1 = find_mob.substring(0,2);
                var get_mobile2 = find_mob.substring(7,10);
                    if(find_mob=="")
                    {
                        $("#errspan").text("Please enter your registered mobile number.")
                        // alert("Enter Ref no");
                    }
                    else
                    {
                        enroll.showLoading();
                        var ajax = require('web.ajax');
                        ajax.jsonRpc("/searchMobNo", 'call', {'user_input_mobile' :find_mob ,})
                            .then(function (values) {
                                // alert(values)
                                var get_email = values
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
                                    // w.document.write("OTP has been send to your <br>Mobile no :"+"<span style='color:red;'>"+ "*******"+get_mobile+"</span>"+"<br>Email : "+"<span style='color:red;'>"+get_email+"</span>" )
                                    // w.focus()
                                    // setTimeout(function() {w.close();}, 3000)
                                    //$("#desc").html("OTP has been send to your <br> Mobile No :"+get_mobile1+"*****"+get_mobile2 +"<br>Email : "+get_email );
                                    $("#desc").html("OTP has been send to your <br>Email : "+get_email );
                        
                                    // tempAlert("OTP has been send to your <br> Mobile no : *******"+get_mobile +"<br>Email : "+get_email,2000);
                                    $("#errspan").text("")
                                    startTimer(600);
                                    // $("#resendotp").hide()
                                }
                                console.log(values)
                        }); 
                    }
            })
    
            $('#btnSubmit').on('click',function(){
                    
                var find_otp = $('#txtOtpNum').val();
                var find_mob = $('#txtMobNum').val();
                // console.log("Your OTP is :",find_otp)
                enroll.showLoading();
                var ajax = require('web.ajax');
                ajax.jsonRpc("/searchOTP", 'call', {'mobile' :find_mob ,'otp':find_otp})
                    .then(function (values) {
                        enroll.hideLoading();
                        // alert(values)
                        if(values == 'status0')
                        {
                            $("#rmvid").text("Invalid OTP!");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status1')
                        {
                            $("#rmvid").text("Your OTP has been expired! Please give your Recent OTP.");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status2')
                        {
                            $("#rmvid").text("Sorry, Invalid OTP !");
                            // $("#resendotp").hide()
                        }
                        else if(values == 'status3')
                        {
                            $("#rmvid").text("Your time has been expired! Please resend to move forward.");
                            // $("#resendotp").show()
                        }
                        else
                        {
                            $("#time_left").hide()
                            $("#rmvid").text(" Congrats !! Welcome to CSM Technologies !!");
                            window.location.href = "/personaldetails/";
                        }
                        //console.log(values)

                    });
    
            });
            
            $('#resendotp').on('click',function(){

                var find_mob = $('#txtMobNum').val();
                var get_mobile1 = find_mob.substring(1,2);
                var get_mobile2 = find_mob.substring(7,10);
                enroll.showLoading();
                var ajax = require('web.ajax');
                ajax.jsonRpc("/searchMobNo", 'call', {'user_input_mobile' :find_mob})
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
                            //$("#desc").text("OTP has been sent successfully to"+ get_mobile1 +"*****"+get_mobile2 +' and '+get_email);
                            $("#desc").text("OTP has been sent successfully to "+get_email);
                            // tempAlert("hii",3000);
                            $.unblockUI();
                            // $("#resendotp").hide()
                        }
                         console.log(values)
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
                        }
                    });
                
            }
            function closeTimer(){
                clearInterval(timer);
            }

            //   Timer Function : End....

            // function tempAlert(msg,duration)
            //     {
            //     var new_element = document.getElementById("#OTPnumber").createElement("div");
            //     new_element.setAttribute("style","z-index:1;position:absolute;float:right;top:10%;left:80%;background-color:gray;border-radius:5px;height:100;width:200;padding:5px;color:red;");
            //     new_element.innerHTML = msg;
            //     setTimeout(function(){
            //         new_element.parentNode.removeChild(new_element);
            //     },duration);
            //     document.body.appendChild(new_element);
            //     }
    
    }); 
    
});