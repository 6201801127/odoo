odoo.define('kw_eos.UserGuideTemplate', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var ListController = require('web.ListController');

    var InventoryUserGuide = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        template: 'EosUserGuideTemplate',
        init: function (parent, action) {
            this.actionManager = parent;
            this.action = action;
            this.domain = [];
            return this._super.apply(this, arguments);
        },
   
    });

    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);

            if(this.modelName == 'kw_resignation' && this.viewType == 'list'){
                this.button_click_eos_guide();
            }
            // if(this.modelName == 'kw_material_management' && this.viewType == 'list' && this.searchView.action.name == 'Pending Action'){
            //     this.button_click_sbu_inventory_guide();
            // }
           
           
        },
        button_click_eos_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_resignation_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("User Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_eos/static/src/offboarding_user_manual.pdf" width="100%" height="600px"></iframe>');
                $modalBody.append($iframe);
                
                // Set modal footer
                var $closeModalButton = $('<button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>');
                $modalFooter.append($closeModalButton);
                
                // Assemble modal content
                $modalContent.append($modalHeader, $modalBody, $modalFooter);
                $modalDialog.append($modalContent);
                $modalContainer.append($modalDialog);
                
                $modalContainer.modal('show');
            });

        },
        
    });
    return ListController, UserGuideTemplate;
});
