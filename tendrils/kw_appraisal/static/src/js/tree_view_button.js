odoo.define('kw_appraisal.ListControllerButton', function (require) {
    "use strict";
    
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    
    ListController.include({
        renderButtons: function($node) {
            var self = this;
            self.current_act_window = this.getParent().actions;
            if (self.current_act_window !== undefined && self.current_act_window !== null) {
                $.each(self.current_act_window,function(key,value){
                    self.current_act_window_id = value['id'];

                })
            }

            this._super.apply(this, arguments);
            if(this.modelName == 'shared_increment_promotion' && this.viewType == 'list'){
                setTimeout(this.user_chro_group.bind(this), 100);

                // this.user_chro_group(); // CHRO
                this.chro_button_click(); //CHRO
                // this.user_manager_group(); // Manager
                setTimeout(this.user_manager_group.bind(this), 100);

                this.manager_button_click();  // Manager
                // this.user_ceo_group(); //CEO Submit
                setTimeout(this.user_ceo_group.bind(this), 100);
                this.ceo_button_click(); //CEO Submit
                // this.user_hod_group(); //HOD
                setTimeout(this.user_hod_group.bind(this), 100);

                this.hod_button_action(); //HOD
            }
        },
      
        hod_button_action: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_send_to_chro', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to send data to CHRO !",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Share",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'shared_increment_promotion',
                            method: 'action_send_to_chro',  // Send to CHRO 
        
                        }).then(function (result) {
                            location.reload();
                    });
                     
                    }
                  }
                );
            });
        },
        user_hod_group: function(){
            var self = this;
            var user = session.uid;
            let params = (new URL(document.location)).searchParams;
            var new_url = document.URL
            var list = new_url.split("=")
            var menu_id = list[list.length-4]
            var numberPattern = /\d+/;
            // Extracting the number using match() method
            var match = self.current_act_window_id;
            return rpc.query({
                    model: 'shared_increment_promotion',
                    method: 'check_hod_group',
                    args:[{'action': match}]
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_send_to_chro').hide();
                    }
                });
        },
        chro_button_click: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_send_to_ceo', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to send data to CEO !",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Share",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'shared_increment_promotion',
                            method: 'action_send_to_ceo',  // Send to CEO
                        }).then(function (result) {
                            location.reload();
                    });
                     
                    }
                  }
                );
            });
        },
        user_chro_group: function(){
            var self = this;
            var user = session.uid;
            let params = (new URL(document.location)).searchParams;
            var new_url = document.URL
            var list = new_url.split("=")
            var menu_id = list[list.length-4]
            var numberPattern = /\d+/;
            // Extracting the number using match() method
            var match = self.current_act_window_id;
            console.log('dekhiba kan hauchi',match)
            return rpc.query({
                    model: 'shared_increment_promotion',
                    method: 'check_chro_group',
                    args:[{'action': match}]
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_send_to_ceo').hide();
                    }
                });
        },
        manager_button_click: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_send_to_hod_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to send data to IAA (Increment Approval Authority) !",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Share",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({
                            model: 'shared_increment_promotion',    
                            method: 'action_send_to_hod',   // Send to HOD
                        }).then(function (result) {
                                location.reload();
                        });
                    }
                });
            });
        },
        
        user_manager_group: function(){
            var self = this;
            var user = session.uid;
            let params = (new URL(document.location)).searchParams;
            var new_url = document.URL
            var list = new_url.split("=")
            var menu_id = list[list.length-4]
            var numberPattern = /\d+/;
            var match = self.current_act_window_id;
            return rpc.query({
                    model: 'shared_increment_promotion',
                    method: 'check_manager_group',
                    args:[{'action': match}]
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_send_to_hod_button').hide();
                    }
                });
        },
        ceo_button_click: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_ceo_submit_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to submit the data !",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Share",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'shared_increment_promotion',
                            method: 'action_ceo_submit',  // CEO Submit Button
        
                        }).then(function (result) {
                            location.reload();
                    });
                     
                    }
                  }
                );
            });
        },
        user_ceo_group: function(){
            var self = this;
            var user = session.uid;
            let params = (new URL(document.location)).searchParams;
            var new_url = document.URL
            var list = new_url.split("=")
            var menu_id = list[list.length-4]
            var numberPattern = /\d+/;
            var match = self.current_act_window_id;
            return rpc.query({
                    model: 'shared_increment_promotion',
                    method: 'check_ceo_group',
                    args:[{'action': match}]
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_ceo_submit_button').hide();
                    }
                });
        },
    });
    return ListController;
    
    });
    