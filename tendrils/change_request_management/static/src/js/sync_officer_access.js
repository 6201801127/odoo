odoo.define('change_request_management.sync_officer', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'cr_officer_access' && this.viewType == 'list'){
                this.button_click_officer_access();
                
            }
        },
        button_click_officer_access: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_officer_access', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Officer Access",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'cr_officer_access',
                            method: 'give_officer_group_access',
                            args: [[]],  
                        }).then(function (e) {
                            console.log(e);                            
                        });
                    }
                  }
                );
            });

        }
    });
    

    return ListController;

});