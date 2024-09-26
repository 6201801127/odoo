odoo.define('kw_career_sync.ListController', function (require) {
    "use strict";
    
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if(this.modelName == 'hr.applicant' && this.viewType == 'list'){
                this.button_click_fetch_application();
            }
           
        },
        button_click_fetch_application: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_application_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Applications Data from Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'hr.applicant',
                            method: 'sync_career_applicant',

                        })

                    }
                  }
                );
            });
        },
    
    });
    
    return ListController;
    
    });
    