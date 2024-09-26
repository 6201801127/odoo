odoo.define('kw_gallery.tour', function (require) {
    "use strict";
    
    var core = require('web.core');
    var tour = require('web_tour.tour');
    
    var _t = core._t;
    
    tour.register('gallery_kw_tour', {
        url: "/web",
    }, [tour.STEPS.SHOW_APPS_MENU_ITEM, {
        trigger: '.o_app[data-menu-xmlid="kw_gallery.kw_website_gallery_menu_root"]',
        content: _t('Want to <b>See Photos Of CSM </b>?<br/><i>Click on Gallery to start.</i>'),
        position: 'right',
        edition:'community'
    }, 
    {
        trigger: '.o-kanban-button-new',
        content: _t("Create a new album here to upload photos."),
        position: 'bottom',
        edition: 'enterprise',
    }
]);
    
    });
    