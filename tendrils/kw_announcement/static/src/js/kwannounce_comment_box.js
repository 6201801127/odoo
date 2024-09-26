/*
odoo.define('kw_announcement.comments', function(require) {
    "use strict";

    var KanbanController = require("web.KanbanController");
    var ListController = require("web.ListController");

    // var FormController = require("web.FormController");

    
    var includeDict = {

        renderButtons: function () {
            this._super.apply(this, arguments);

            if (this.modelName === "kw_announcement") {

               // console.log('aaaaaaaaaa')

                this.$buttons.find('button.o_button_import').hide();

                //this.$buttons.find('button.o_chatter_button_log_note').hide();
            }
        }

    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);


});    
*/


odoo.define('kw_announcement.load_comments', function (require) {
    "use strict";
    //console.log('sdsdsdsdsd')

    var mailUtils       = require('mail.utils');

    var AbstractField   = require('web.AbstractField');
    var concurrency     = require('web.concurrency');

    var core            = require('web.core');
    var field_registry  = require('web.field_registry');
    
    var QWeb            = core.qweb;    
    var time            = require('web.time');

    var FieldKwCommentChart = AbstractField.extend({
    
       events: {
            "click .o_announcement_write_comment": "_onCommentWrite",
        },
        /**
         * @constructor
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);            
            this.dm = new concurrency.DropMisordered();
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Get the chart data through a rpc call.
         *
         * @private
         * @param {integer} annuncement_id
         * @returns {Deferred}
         */
        _getCommentData: function (annuncement_id) {
            var self = this;
            return this.dm.add(this._rpc({
                route: '/kwannouncement/get_comment_list',
                params: {
                    annuncement_id: annuncement_id,
                },
            })).then(function (data) {
              
                var  date_en = ''
                data.posted_comments.forEach(function(item){   

                    date_en         = item.created_on ? moment(time.str_to_datetime(item.created_on)) : moment(); 
                    item.lapse_time = mailUtils.timeFromNow(date_en);
                });

                self.comntData = data;
            });
        },
        /**
         * @override
         * @private
         */
      _render: function () {

            //console.log("Inside render"+ this.recordData.id)
            if (!this.recordData.id) {

                return this.$el.html(QWeb.render("kwannounce_comment_box", {
                    posted_comments: []
                }));             
            }

            var self = this;
            return this._getCommentData(this.recordData.id).then(function () {

               self.$el.html(QWeb.render("kwannounce_comment_box", self.comntData));
            });
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * Redirect to the employee form view.
         *
         * @private
         * @param {MouseEvent} event
         * @returns {Deferred} action loaded
         */
        _onCommentWrite: function (event) {

            event.preventDefault();

            var comment = $('.o_announcement_comment_text_field').val();
            var announcement_id = this.recordData.id;
            var self = this;

            if (comment) {
                return this.dm.add(this._rpc({
              
                    route: '/kwannouncement/post_comment',
                    params: {
                        annuncement_id: announcement_id,
                        comments: comment,
                    },

                })).then(function (data) {

                    if(data){

                        var  date_en = ''
                        data.posted_comments.forEach(function(item){   
                            date_en         = item.created_on ? moment(time.str_to_datetime(item.created_on)) : moment(); 
                            item.lapse_time = mailUtils.timeFromNow(date_en);
                        });
                        self.$el.html(QWeb.render("kwannounce_comment_box",data));  
                    }
                   
                });
            }   
           
        },
      

    });
    
    field_registry.add('list.kwannounce_comment_box', FieldKwCommentChart);
    return FieldKwCommentChart;
});
    
/*
odoo.define('kw_announcement.web_search_disable_add_custom_filter', function (require) {
    'use strict';
    
    var FilterMenu = require('web.FilterMenu');
    
    FilterMenu.include({
        start: function () {
            this._super();
            if (!this.searchview.is_action_enabled('enable_custom_filter')) {
                this.$('.divider:last').hide();
                this.$add_filter.hide();
            }
        }
    });
    
});

*/
