/*Part of Xao Xao Digital CO.,LTD. See LICENSE file for full copyright and licensing details.*/


$(document).ready(function () {
    $("div#xx_companion_collapser").click(function(e) {
    	e.stopPropagation();
    	e.preventDefault();

    	$("#xx_companion_collapser > .companion-collapser-button").toggleClass("companion-collapser-button-checked");

        $("#app-sidebar").animate({
            width: ['toggle', 'swing'],
            opacity: 'toggle'
        }, 150, 'linear');
    });
});

    
