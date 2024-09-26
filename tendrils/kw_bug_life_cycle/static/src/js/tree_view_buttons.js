odoo.define('kw_bug_life_cycle.ListControllerButton', function (require) {
    "use strict";
    
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;

    var ajax = require('web.ajax');
    var session = require('web.session');
    var FormController = require('web.FormController');
    var core = require('web.core');
    var _t = core._t;
    
    ListController.include({
        renderButtons: function($node) {
            console.log('renderButtons');
            this._super.apply(this, arguments);
            if(this.modelName == 'kw_test_case_upload' && this.viewType == 'list'){
                console.log('inside if');
                this.$buttons.on('click', '.oe_action_download_format', function () {
                    console.log('button clicked');
                    var base_url = window.location.origin || window.location.protocol + '//' + window.location.host;
                    var result_url = base_url + '/download-csv-format/';
                    window.location.href = result_url
                });
            }
        },

        renderButtons: function($node) {
            this._super.apply(this, arguments);
            
            var self = this;
            rpc.query({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                args: ['kw_bug_life_cycle.view_test_scenario_tree','view_scenario'],  // Replace with your actual external ID
            })
            .then(function(viewId) {
                if (self.modelName === 'test_scenario_master' && self.viewType === 'list' && self.displayName ==='View Scenario') {
                    if (self.$buttons) {
                        self.$buttons.on('click', '.oe_action_download_ts_format', function () {
                            var selectedIds = self.getSelectedIds();
                            if (selectedIds.length === 0) {
                                swal("Warning", "No records selected", "warning");
                                return;
                            }
                            return swal({
                                title: "Are You Sure?",
                                text: "You are going to Download",
                                type: "warning",
                                confirmButtonColor: "#108fbb",
                                showCancelButton: true,
                                confirmButtonText: "Download Ts",
                                cancelButtonText: "No",
                            }, function(isConfirm) {
                                if (isConfirm) {
                                    return rpc.query({
                                        model: 'test_scenario_master',
                                        method: 'get_download_test_scenario',
                                        args: [selectedIds,],  // Pass selected IDs here
                                    }).then(function(action) {
                                        // Redirect to the generated action URL
                                        window.location.href = action.url;
                                    });
                                }
                            });
                        });
                    }
                }
                else {
                    if (self.$buttons) {
                        self.$buttons.on('click', '.oe_action_download_ts_format', function () {
                            swal("Warning", "This Button only access in view scenario page.", "warning");
                        });
                    }
                }

            }).fail(function(err) {
                console.error('Error fetching view ID:', err);
            });
        },
        

        getSelectedIds: function() {
            var selectedIds = this.getSelectedRecords().map(record => record.res_id);
            return selectedIds;
        },
        
    });   


    FormController.include({
        _onSave: function (ev) {
            var self = this;
            var record = this.model.get(this.handle);

            if (record.model === 'test_scenario_master') {
                var description = record.data.scenario_description || '';
                var expectedTestCases = record.data.expected_no_of_test_case || 0;

                if (description && description.length > 200) {
                      swal('Scenario Description length cannot be more than 200 characters.');
                    ev.preventDefault();
                    return;
                }
              if (expectedTestCases < 1) {
                swal('Expected number of Test cases should be greater than 0.');
                ev.preventDefault();
                return;
                }
            }
            this._super.apply(this, arguments);
        },
    });


    return {
        FormController: FormController,
        ListController: ListController
    };
});
    