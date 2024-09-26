odoo.define('kw_resource_management.sync_consultant', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);

            if (this.modelName == 'sync_consultant_data' && this.viewType == 'list') {
                this.button_click_sync_counsultant_access();

            }
        },
        button_click_sync_counsultant_access: function () {
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_consultant_details', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Consultant",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                },
                    function (isConfirm) {
                        if (isConfirm) {
                            return rpc.query({
                                model: 'sync_consultant_data',
                                method: 'sync_consultant_data_upload',
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