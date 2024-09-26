odoo.define('kwantify_theme.login_page', function (require) {
    "use strict";
    // const crypto = require('crypto');
    var ajax = require('web.ajax');
    var session = require('web.session');
    // Generate Aplha-Numberic key for AES Encription
    $(function() {
//        $(document).on('mousedown','.passwordToggle', function(){
//            $(this).removeClass('icon-eye').addClass('icon-eye-off');
//            $('#password').attr('type','text');
//        });
//
//        $(document).on('mouseup','.passwordToggle', function(){
//            $(this).removeClass('icon-eye-off').addClass('icon-eye');
//            $('#password').attr('type','password');
//        });
//
//        $(document).on('mousedown','.passwordToggle1', function(){
//            $(this).removeClass('icon-eye').addClass('icon-eye-off');
//            $('#confirm_password').attr('type','text');
//        });
//
//        $(document).on('mouseup','.passwordToggle1', function(){
//            $(this).removeClass('icon-eye-off').addClass('icon-eye');
//            $('#confirm_password').attr('type','password');
//        });

        $("#login_option_button").click(function() {
            var host = window.location.hostname;
//             console.log("host=========",host.slice(0,7))
            const local_ip ='127.0.0.1'
            const stg_local_ip ='10.1.1.164'
            var host_headers = ['localhost','odoostg.csm.tech','192.168.61.158','192.168.27.120','164.164.122.169','192.168.27.189','10.1.1.164', '172.27.32.154','172.27.29.18','192.168.27.189','172.27.28.221','172.27.30.120','172.27.29.18','172.27.29.170','172.27.30.79','172.27.29.193']
            // console.log("host name--------------------",host,host_headers.includes(host))
            if (!(host_headers.includes(host)) && !(local_ip.includes(host.slice(0,7))) && !(stg_local_ip.includes(host.slice(0,7)))){
                window.location.href = '/forbidden-page'
            }else{
                // console.log("host name--------------------",host)
                var inputField = document.getElementById('password');
                console.log("on click of event");
                const password = $('#password').val();
                const auth_secret_key = $('#hidden_field_val').val()
                // var encrypted = CryptoJS.AES.encrypt(password, key).toString();
                const key = CryptoJS.enc.Hex.parse(auth_secret_key);
                // Encryption
                const encrypted = CryptoJS.AES.encrypt(password, key, {
                                        mode: CryptoJS.mode.ECB,
                                        padding: CryptoJS.pad.Pkcs7,
                                    });
                inputField.value = encrypted;
                // Make an Ajax request to set the value in the session
                $('#login_form').submit()
            }
        });
        $(document).on('keyup','#password', function(event){
            if (event && event.keyCode === 13) {
                $("#login_option_button").trigger("click");
            }
        });
    });

});