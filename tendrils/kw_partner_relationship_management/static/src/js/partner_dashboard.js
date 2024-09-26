//odoo.define("partner_board.dashboard", function (require) {
//"use strict";
//    console.log('dashboard #1');
//    var BoardView = require('board.BoardView');
//    console.log('dashboard #2');
//    var partner_board = BoardView.include({
//        _saveDashboard: function () {
//            console.log('dashboard #3');
//            var board = this.renderer.getBoard();
//            var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
//            console.log('dashboard #3');
//            return this._rpc({
//                route: '/web/view/edit_custom',
//                params: {
//                    custom_id: this.customViewID !=null? this.customViewID: '',
//                    arch: arch,
//                }
//            }).then(dataManager.invalidate.bind(dataManager));
//        },
//    });
//    return partner_board;
//});

odoo.define('partner_board.BoardView', function (require) {
"use strict";
    var BoardView = require('board.BoardView');
    var core = require('web.core');
    var dataManager = require('web.data_manager');
    var _t = core._t;
    var _lt = core._lt;
    var QWeb = core.qweb;
    console.log('dashboard #33');
    var BoardController = BoardView.include({
        _saveDashboard: function () {
            console.log('dashboard #44');
            var board = this.renderer.getBoard();
            var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
            return this._rpc({
                route: '/web/view/edit_custom',
                params: {
                    custom_id: this.customViewID != null? this.customViewID: '',
                    arch: arch,
                }
            }).then(dataManager.invalidate.bind(dataManager));
        },
    });
});