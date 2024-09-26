odoo.define('kw_greetings.tree_view_button', function (require){
    "use strict";
    
    // var core     = require('web.core');
    // var ListView = require('web.ListView');
    // var QWeb     = core.qweb;

    // var viewRegistry    = require('web.view_registry');
    var ListController  = require('web.ListController');

    // var KanbanView = require('web.KanbanView');
    var KanbanController  = require('web.KanbanController');

    var includeDict = {

            renderButtons: function () {

                this._super.apply(this, arguments);

                if (typeof this !== "undefined" && this.hasOwnProperty('modelName')){

              
                    if (this.modelName === "hr_employee_greetings") {

                        this.$buttons.find('button.o_button_import').hide();

                        this.$buttons.find('button.o-kanban-button-new').hide();
                        this.$buttons.find('button.o_list_button_add').hide();

                       // this.draggable = false;

                        // this.$buttons.find('.o_list_wish_button_all').click(this.proxy('tree_view_action'));
                        var self = this;
                        this.$buttons.on('click', '.o_list_wish_button_all', function () {

                            // var state   = self.model.get(self.handle, {raw: true});
                            // var context = state.getContext()
                            
                            // var self = this;
                            self._rpc({

                                model: 'kw_greetings_send_wishes',
                                method: 'action_send_wish_all',
                                args: [{'action_id': self.res_id}],
                                
            
                            }).then(function (data) {
                                // console.log(data)
            
                                if(data){
                                    self.trigger_up('reload');
                                }
                                
                            });


                        });

                    }

                }
            },          

            
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);


    
       /* var WishesListController = ListController.extend({

            buttons_template: 'WishListView.buttons',
            /**
             * Extends the renderButtons function of ListView by adding an event listener
             * on the bill upload button.
             *
             * @override
             */
         /*   renderButtons: function () {
                this._super.apply(this, arguments); // Possibly sets this.$buttons
                if (this.$buttons) {
                    var self = this;

                    // this.$buttons.find('.o_list_wish_button_create').click(this.proxy('tree_view_action'));

                    this.$buttons.on('click', '.o_list_wish_button_all', function () {

                        var state   = self.model.get(self.handle, {raw: true});
                        var context = state.getContext()
                        
                        // var self = this;
                        self._rpc({

                            model: 'kw_send_wish',
                            method: 'action_send_wish_all',
                            args: [{'action_id': self.res_id}],
                            
        
                        }).then(function (data) {

                            // console.log(data)
        
                            if(data){
                                self.trigger_up('reload');
                            }
                            
                        });


                    });
                }
            } 
            // tree_view_action: function () {           
            //     console.log('sssssssssss')
            //     // this.do_action({
            //     //         type: "ir.actions.act_window",
            //     //         name: "send wish all",
            //     //         res_model: "kw_send_wish",
            //     //         views: [[false,'form']],
            //     //         target: 'current',
            //     //         view_type : 'form',
            //     //         view_mode : 'form',
            //     //         flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            //     // });
            //     // return { 'type': 'ir.actions.client','tag': 'reload', } 

    

        });
    
        var WishListView = ListView.extend({
            config: _.extend({}, ListView.prototype.config, {
                Controller: WishesListController,
            }),
        });
    
      //  viewRegistry.add('send_wish_tree', WishListView);
        */

    
});


