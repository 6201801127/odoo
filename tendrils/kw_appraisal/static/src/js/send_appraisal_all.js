odoo.define('kw_appraisal.send_appraisal_all', function(require) {
    "use strict";

    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');
    var session = require('web.session');

    var includeDict = {

        renderButtons: function() {

            this._super.apply(this, arguments);

            if (typeof this !== "undefined" && this.hasOwnProperty('modelName')) {


                if (this.modelName === "hr.appraisal") {
                    var self = this;
                    self._rpc({

                        model: 'hr.appraisal',
                        method: 'check_groups',
                        args: [{ 'user_id': session.uid }],

                    }).then(function(data) {
                        if(data == false){
                            // $('.o_list_start_button_all').hide();
                            // $('.o_list_publish_button_all').hide();
                            $('.o_dropdown_toggler_btn').hide();
                        }
                    });


                    this.$buttons.find('button.o_button_import').hide();

                    this.$buttons.find('button.o-kanban-button-new').hide();
                    this.$buttons.find('button.o_list_button_add').hide();

                    var self = this;

                }

            }
        },


    };

    KanbanController.include(includeDict);
    // ListController.include(includeDict);

});