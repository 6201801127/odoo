odoo.define('kw_visiting_card.hide_create_button', function(require) {
    "use strict";
    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');
    var session = require('web.session');

    var includeDict = {

        renderButtons: function() {
            this._super.apply(this, arguments);
            if (typeof this !== "undefined" && this.hasOwnProperty('modelName')) {
                if (this.modelName === "kw_visiting_card_apply") {
                    var self = this;
                    self._rpc({
                        model: 'kw_visiting_card_apply',
                        method: 'check_groups',
                        args: [{ 'user_id': session.uid }],
                    }).then(function(data) {
                        if(data == true){
                            $('.o_list_button_add').hide();
                            $('.o-kanban-button-new').hide();
                            // $('.breadcrumb-item').text("Applied Cards");
                        }
                    });

                    // this.$buttons.find('button.o_button_import').hide();
                    // this.$buttons.find('button.o-kanban-button-new').hide();
                    // this.$buttons.find('button.o_list_button_add').hide();

                    var self = this;
                }
            }
        },
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);

});