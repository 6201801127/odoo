odoo.define('performance_improvement_plan.sync_lk_user', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'pip_l_k_training_access' && this.viewType == 'list'){
                this.button_click_lk_access();
            }
        },
       
        button_click_lk_access: function(){
            // console.log("in report access==========================")
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_lk_access', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync L&k User Access",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'pip_l_k_training_access',
                            method: 'give_notify_lk_access',
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