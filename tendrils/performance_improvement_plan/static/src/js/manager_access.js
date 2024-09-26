odoo.define('performance_improvement_plan.sync_manager', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'pip_manager_access' && this.viewType == 'list'){
                this.button_click_manager_access();
            }
        },
        
        button_click_manager_access: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_manager_access', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Manager Access",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'pip_manager_access',
                            method: 'give_manager_group_access',
                            args: [[]],
                        }).then(function (e) {
                            console.log(e);
                        });

                    }
                  }
                );
            });

        },
    });
    

    return ListController;

});