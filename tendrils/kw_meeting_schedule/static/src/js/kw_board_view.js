odoo.define('kw_meeting_schedule.custom_dashboard_modification', function (require) {
    "use strict";


    var BoardView = require('board.BoardView');

    var viewRegistry = require('web.view_registry');

    var FormController = require('web.FormController');
    var boardviewRegistry = require('board.viewRegistry');
    // print('sssssssssss')
    // print(BoardView.BoardController)

    // var BoardViewNew = BoardView.extend({

    //     init: function (viewInfo) {
    //         this._super.apply(this, arguments);

    //         console.log('343533434')
    //         // this.controllerParams.customViewID = viewInfo.custom_view_id;
    //     },
    // });   

    //  return BoardViewNew
    /* BoardView.BoardController.extend({

        
        // events: _.extend({}, BoardView.prototype.events, {
        //     'save_dashboard': '_saveDashboard',
        // }),
    
        _saveDashboard: function () {
            var board = this.renderer.getBoard();
            var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
            console.log('sssssssss')
            // custom_id: this.customViewID!=null ?this.customViewID:'',
            // this.actionViews[0]['viewID']
            // view_id = this.actionViews[0]['viewID']

            return this._rpc({
                    route: '/web/view/edit_custom',
                    params: {
                        custom_id: this.customViewID!=null ?this.customViewID:'',
                        arch: arch,
                        view_id:view_id
                    }
                }).then(dataManager.invalidate.bind(dataManager));
        },



    });  
     */


});