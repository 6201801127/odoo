odoo.define('kw_emp_profile.appmenu', function (require) {
    "use strict";

    var page = require('web.UserMenu');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    var core = require('web.core');
    var framework = require('web.framework');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var _t = core._t;
    var QWeb = core.qweb;

    var usepage = page.include({
        _onMenuManual: function () {
//            console.log('Calling RPC...')
            var self = this;
            var session = this.getSession();
            this.trigger_up('clear_uncommitted_changes', {
               callback: function () {
                   self._rpc({
                       model:'kw_emp_profile',
                       method:'view_profile_employee'
                   })
                   .done(function (result) {
                        if (result != undefined){
                            var profile_url = '/web#id='+result[0]+'&action='+result[2]+'&model=kw_emp_profile&view_type=form';
                            window.location.href = profile_url;
                        }
                   });
               },
            },)
        },
        _onMenuJob_role: function(){
            var self = this;
            var session = this.getSession();
            self._rpc({
                model: 'hr.employee',
                method: 'get_my_job_role',
                kwargs: {'uid': session.uid},
            })
            .done(function (result) {
                console.log("result >>>> ", result);
                new Dialog(this, {
                    size: 'large',
                    dialogClass: 'o_act_window',
                    title: _t("My Job Role & Autonomy"),
                    $content: $(QWeb.render("kw_emp_profile.job_role", {'res':result})),
                    buttons: [{
                        text: _t("Close"),
                        classes : "btn-primary",
                        close: true,
                    }]
                }).open();
            });
        }
    });
});