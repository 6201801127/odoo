odoo.define('performance_improvement_plan.sync_report_user', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
     
            if(this.modelName == 'pip_report_access' && this.viewType == 'list'){
                this.button_click_report_access();
            }
        },
       
        button_click_report_access: function(){
            // console.log("in report access==========================")
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_report_access', function () {
                // console.log("in swal-----------------------")
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Report Access",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        return rpc.query({
                            model: 'pip_report_access',
                            method: 'give_report_group_access',
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