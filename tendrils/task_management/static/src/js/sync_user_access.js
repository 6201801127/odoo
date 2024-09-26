odoo.define('task_management.sync_users', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'task_management_user_access' && this.viewType == 'list'){
                this.button_click_configuration_access();
                
            }
        },
        button_click_configuration_access: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_users_access', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync User Access",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Users",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'task_management_user_access',
                            method: 'give_config_user_group_access',
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