odoo.define('kw_meeting_zoom_integration.ListController', function (require) {
"use strict";

var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;

ListController.include({
	renderButtons: function($node) {
        this._super.apply(this, arguments);
        if (typeof this !== "undefined" && this.hasOwnProperty('modelName') && this.hasOwnProperty('viewType')){
	        if(this.modelName == 'kw_meeting_events' && this.viewType == 'list'){
		        this.check_zoom_user();
		    }
		}  
		if (typeof(this.$buttons) !== 'undefined' && this.$buttons){  
	            this.$buttons.find('.oe_action_tag_zoom_button').click(this.proxy('on_action_tag_zoom'));
	    }
	},
	on_action_tag_zoom: function(e){
        e.preventDefault();
        this.do_action({
            name: _t("Tag Zoom Email ID"),
            type: "ir.actions.act_window",
            res_model: "zoom_email_employee",
            domain : [],
            views: [[false, "form"]],
            target: 'new',
            context: {},
            view_type : 'form',
            view_mode : 'form'
        });
    },
    check_zoom_user: function(){
        var self = this;
        var user = session.uid;
        return rpc.query({
                model: 'kw_zoom_users',
                method: 'check_zoom_user',
                args: [[user],{'id':user}],
            }).then(function (e) {
                $(".o_menu_apps").find('.dropdown-menu[role="menu"]').removeClass("show");
                if(e.status == 'success'){
                    self.$buttons.find('.oe_action_tag_zoom_button').hide();
                }else if(e.status == 'pending'){
                    self.$buttons.find(".oe_action_tag_zoom_button")
                                .html("Pending Zoom Activation")
                                .removeClass('btn-success')
                                .addClass('btn-warning')
                                .prop('disabled',true);

                }
            });
    }

});

return ListController;

});
