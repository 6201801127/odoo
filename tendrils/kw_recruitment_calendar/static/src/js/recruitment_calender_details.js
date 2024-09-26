odoo.define('kw_recruitment_calendar.recruitment_calender', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);

            if (this.modelName == 'kw_recruitment_positions' && this.viewType == 'list') {
                this.button_click_recruitment_calender_data_update();

            }
        },
        button_click_recruitment_calender_data_update: function () {
            var self = this;
            this.$buttons.on('click', '.oe_action_recruitment_calender_details', function () {
                return swal({
                    title: "Are You Sure?",
                    text: "You are going to update recruitment calender",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Update Data",
                    cancelButtonText: "No",
                },
                    function (isConfirm) {
                        if (isConfirm) {
                            return rpc.query({
                                model: 'kw_recruitment_positions',
                                method: 'recruitment_calendar_data_update',
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