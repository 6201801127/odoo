odoo.define('kw_recruitment.external_button', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var ListController = require('web.ListController');
    var session = require('web.session');

    var includeDict = {

        renderButtons: function () {

            this._super.apply(this, arguments);

            if (typeof this !== "undefined" && this.hasOwnProperty('modelName')) {


                if (this.modelName === "kw_hr_job_positions") {

                    var self = this;
                    this.$buttons.on('click', '.o_kanban_sync_job_button', function () {

                        self._rpc({

                            model: 'kw_hr_job_positions',
                            method: 'sync_job_lists',
                            args: [{ 'action_id': self.res_id }],

                        }).then(function (data) {

                            if (data) {
                                self.trigger_up('reload');
                            }

                        });

                    });

                    this.$buttons.on('click', '.o_kanban_sync_master_button', function () {

                        self._rpc({

                            model: 'kw_hr_job_positions',
                            method: 'sync_job_master',
                            args: [{ 'action_id': self.res_id }],

                        }).then(function (data) {

                            if (data) {
                                self.trigger_up('reload');
                            }

                        });

                    });

                }

            }
        },


    };

    KanbanController.include(includeDict);
    
});