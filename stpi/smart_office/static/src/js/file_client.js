odoo.define('smart_office.efile_content', function(require) {
    "use strict";

    var ListController = require("web.ListController");
    // var KanbanView = require('web.KanbanView');
    var KanbanController  = require('web.KanbanController');

    var includeDict = {

            renderButtons: function () {

                this._super.apply(this, arguments);

                // if (typeof this !== "undefined" && this.hasOwnProperty('modelName')){

                    console.log(this);
                    // console.log()
                    if (this.modelName === "see.file") {
                        setTimeout(function(){
                            $('.o_control_panel').addClass('o_hidden');
                            $('.o_content').css('overflow','hidden');
                            $('#efile_frame').attr("height", screen.height);
                        },0);
                        // $('.o_content').addClass('overflow_scroll');
                    //     // this.$buttons.find('button.o_button_import').hide();

                    //     // this.$buttons.find('button.o-kanban-button-new').hide();
                    //     // this.$buttons.find('button.o_list_button_add').hide();

                    //    // this.draggable = false;

                    //     // this.$buttons.find('.o_list_wish_button_all').click(this.proxy('tree_view_action'));
                    }
                    // if(this.modelName != "see.file")
                    else {
                        setTimeout(function(){
                            $('.o_control_panel').removeClass('o_hidden');
                            $('.o_content').css('overflow','auto');
                        },0);
                        // $('.o_content').removeClass('overflow_scroll');
                    }

                // }
            },          

            
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);

    // var core = require('web.core');
    // var ajax = require('web.ajax');
    // var ActionManager = require('web.ActionManager');
    // var view_registry = require('web.view_registry');
    // var AbstractAction = require('web.AbstractAction');
    // var ControlPanelMixin = require('web.ControlPanelMixin');
    // var QWeb = core.qweb;

    // var efileClient = AbstractAction.extend(ControlPanelMixin,{
    //     need_control_panel: false,
    //     init: function(parent, context) {
    //         this._super(parent, context);
    //         var self = this;
    //         context.context['content'] = context.context.content;
    //         if (context.tag == 'efile.notesheet')
    //         {
    //             setTimeout(function(){
    //                 self.render(context);
    //             },500);
    //         }
    //     },
    //     willStart: function() {
    //         return $.when(ajax.loadLibs(this), this._super());
    //    },
    //    start: function() {
    //        var self = this;
    //        return this._super();
    //    },
    //    render: function(url) {
    //     //    var super_render = this._super;
    //     //    console.log("url",url.context.uid)
    //     console.log(url)
    //         var self = this;
    //         var efileQweb = QWeb.render('EfileNotesheet',{widget: url.context.content});
    //         $( ".o_control_panel" ).addClass( "o_hidden" );
    //         $(efileQweb).prependTo(self.$el);
    //         return efileQweb;
    //    },
    //    reload: function () {
    //         window.location.href = this.href;
    //     },
    // });
    // core.action_registry.add('efile.notesheet',efileClient);
    // return efileClient;
});