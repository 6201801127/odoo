odoo.define('kw_inventory.InventoryUserGuideTemplate', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var ListController = require('web.ListController');

    var InventoryUserGuide = AbstractAction.extend(ControlPanelMixin, {
        need_control_panel: false,
        template: 'InventoryUserGuideTemplate',
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

            if(this.modelName == 'kw_material_management' && this.viewType == 'list' && this.searchView.action.name == 'Apply'){
                this.button_click_inventory_guide();
            }
            if(this.modelName == 'kw_material_management' && this.viewType == 'list' && this.searchView.action.name == 'Pending Action'){
                this.button_click_sbu_inventory_guide();
            }
            if(this.modelName == 'kw_material_management' && this.viewType == 'list' && this.searchView.action.name == 'Pending Actions'){
                this.button_click_store_manager_inventory_guide();
            }
            if(this.modelName == 'kw_purchase_requisition' && this.viewType == 'list' && this.searchView.action.name == 'Take action'){
                this.button_click_store_hod_purchase_guide();
            }
            if(this.modelName == 'kw_requisition_requested' && this.viewType == 'list'){
                this.button_click_store_pr_team_purchase_guide();
            }
            if(this.modelName == 'stock.picking' && this.viewType == 'list'){
                this.button_click_store_manager_stock_guide();
            }
            // if(this.modelName == 'kw_service_register' && this.viewType == 'list'){
            //     this.button_click_store_manager_service_register_guide();
            // }
            if(this.modelName == 'purchase.order.line' && this.viewType == 'list'){
                this.button_click_store_manager_service_entry_guide();
            }
           
        },
        button_click_inventory_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_inventory_guide_button', function () {
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
                var $iframe = $('<iframe src="kw_inventory/static/src/material_request_apply.pdf" width="100%" height="600px"></iframe>');
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
        button_click_sbu_inventory_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_inventory_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("SBU Representative Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/sbu_representative_manual.pdf" width="100%" height="600px"></iframe>');
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
        button_click_store_manager_inventory_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_inventory_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("Store Manager Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/Store_manager_manual.pdf" width="100%" height="600px"></iframe>');
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
        button_click_store_hod_purchase_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_purchase_requisition_guide', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("HOD Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/Department_head_manual.pdf" width="100%" height="600px"></iframe>');
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
        button_click_store_pr_team_purchase_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_purchase_requested_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("PR Team Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/Pr_team_user_manual.pdf" width="100%" height="600px"></iframe>');
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
        button_click_store_manager_stock_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_stock_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("Store Manager Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/store_manager_manual2.pdf" width="100%" height="600px"></iframe>');
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
        button_click_store_manager_service_entry_guide: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_ses_guide_button', function () {
                // Create a modal-like container
                var $modalContainer = $('<div class="modal fade" role="dialog">');
                var $modalDialog = $('<div class="modal-dialog modal-lg">');
                var $modalContent = $('<div class="modal-content">');
                var $modalHeader = $('<div class="modal-header">');
                var $modalBody = $('<div class="modal-body">');
                var $modalFooter = $('<div class="modal-footer">');
                
                // Set modal title and close button
                var $modalTitle = $('<h4 class="modal-title">').text("Store Manager Guide");
                var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
                $modalHeader.append($modalTitle, $closeButton);
                
                // Set the iframe to display PDF or Word content
                var $iframe = $('<iframe src="kw_inventory/static/src/store_manager_manual_service.pdf" width="100%" height="600px"></iframe>');
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
        // button_click_store_manager_service_register_guide: function(){
        //     var self = this;
        //     this.$buttons.on('click', '.oe_action_service_register_guide_button', function () {
        //         // Create a modal-like container
        //         var $modalContainer = $('<div class="modal fade" role="dialog">');
        //         var $modalDialog = $('<div class="modal-dialog modal-lg">');
        //         var $modalContent = $('<div class="modal-content">');
        //         var $modalHeader = $('<div class="modal-header">');
        //         var $modalBody = $('<div class="modal-body">');
        //         var $modalFooter = $('<div class="modal-footer">');
                
        //         // Set modal title and close button
        //         var $modalTitle = $('<h4 class="modal-title">').text("Store Manager Guide");
        //         var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
        //         $modalHeader.append($modalTitle, $closeButton);
                
        //         // Set the iframe to display PDF or Word content
        //         var $iframe = $('<iframe src="kw_inventory/static/src/store_manager_manual_service.pdf" width="100%" height="600px"></iframe>');
        //         $modalBody.append($iframe);
                
        //         // Set modal footer
        //         var $closeModalButton = $('<button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>');
        //         $modalFooter.append($closeModalButton);
                
        //         // Assemble modal content
        //         $modalContent.append($modalHeader, $modalBody, $modalFooter);
        //         $modalDialog.append($modalContent);
        //         $modalContainer.append($modalDialog);
                
        //         $modalContainer.modal('show');
        //     });

        // }  
    });
    return ListController, InventoryUserGuide;
});
