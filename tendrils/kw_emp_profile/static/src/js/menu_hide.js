odoo.define('kw_emp_profile.hideMenuScript', function (require) {  // how it works ??
    "use strict";

    $(function(){
        var rpc = require('web.rpc');
        rpc.query({
            model: 'kw_emp_profile',
            method: 'hide_usermenu',
        }).then(function(result){
            if (result == 0)
            {
                setTimeout(function(){
                    $('.user_class').hide();
                },2000)
            }
        });
    });
});