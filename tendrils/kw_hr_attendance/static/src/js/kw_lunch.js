odoo.define('hr_attendance.lunchIn_lunchOut', function (require) {
    "use strict";
    
    var AbstractAction  = require('web.AbstractAction');
    var core            = require('web.core');
    var framework       = require('web.framework');
    var QWeb = core.qweb;
    var _t = core._t;

    var lunchin_lunchout = AbstractAction.extend({
        events: {
            "click .lunch_in": _.debounce(function() {
              
                this.update_myoffice_time('lunch_in');
            }, 200, true),

            "click .lunch_out": _.debounce(function() {
                var lunch_out_alert = confirm("Do you want to update lunch out time?");
                if(lunch_out_alert == true)
                {
                    this.update_myoffice_time('lunch_out');
                    return true;
                }
                else
                {
                    return false;
                }
            }, 200, true),

            "click .check_in": _.debounce(function() {
             
                this.update_myoffice_time('check_in');
            }, 200, true),

            "click .check_out": _.debounce(function() {
                // console.log('check out')
                this.update_myoffice_time('check_out');
            }, 200, true),
           
            
        },
        start: function (sync_status =0) {
            var self = this;
            var def = this._rpc({
                model : 'kw_daily_employee_attendance',
                method: 'get_current_user_office_time_details',
            })
            .then(function (res) {
                $(".o_menu_apps").find('.dropdown-menu[role="menu"]').removeClass("show");
                self.employee = res;      
                // console.log('check late entry and other status >>> ')
                //check late entry and other status
                // _.debounce(self.check_after_log_in_activities(res.attendance_rec_id), 200, true);
                // disabled to resolve the problem of concurrent update of leave tour and sync status
                if(sync_status==1){
                    _.debounce(self.check_after_log_in_activities(res.attendance_rec_id), 200, true);
                //     _.debounce(self.share_attendance_info_with_kwantify(res.attendance_rec_id), 4000, true);
                }
                
                //console.log('after sync')
               
                self.$el.html(QWeb.render("MyOfficeTime", {widget: self}));
                
            });
    
            return $.when(def, this._super.apply(this, arguments));
        },
        update_myoffice_time: function(status){
            var self = this;
            this._rpc({
                model   : 'kw_daily_employee_attendance',
                method  : 'update_myoffice_time',
                args    : [{
                    'update_status':status,
                }],
            }).then(function(res){
                self.lunchIn = res;
                if (status  == 'check_in' || status  == 'check_out'){
                    self.start(1);
                }else{
                    self.start(0);
                }                 
            });
        },
        share_attendance_info_with_kwantify: function(attendance_rec_id){            
            //share the attendance info with kwantify
            this._rpc({
                 model   : 'kw_daily_employee_attendance',
                 method  : 'call_share_attendance_info_with_kwantify',
                 args    : [{                     
                     'attendance_rec_id':attendance_rec_id,
                 }],
             }).then(function(res){
                 
                console.log('attendance info shared')
                //  console.log(res)              
            });
        },
        check_after_log_in_activities: function(attendance_rec_id){            
            //share the attendance info with kwantify
            this._rpc({
                 model   : 'kw_daily_employee_attendance',
                 method  : 'check_after_log_in_activities',
                 args    : [{                     
                     'attendance_rec_id':attendance_rec_id,
                 }],
             }).then(function(res){
                console.log(res)
                console.log('log-in activities success')

                //if late entry url exists
//                if(res && res.le_url != '' && res.le_url != null){
//                    framework.redirect(res.le_url);
//                }

//                if(res && res.epf_url != '' && res.epf_url != null){
//                    framework.redirect(res.epf_url);
//                }

                if(res && res.redirect_url != '' && res.redirect_url != null){
                    framework.redirect(res.redirect_url);
                }

                if(res && res.user_redirect_urls != '' && res.user_redirect_urls != null){
                    framework.redirect(res.user_redirect_urls);                    
                }

            });
        },

    });

    core.action_registry.add('my_office_time', lunchin_lunchout);
    return lunchin_lunchout;
});