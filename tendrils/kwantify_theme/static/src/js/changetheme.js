odoo.define('kwantify_theme.usermenu', function (require) {
  "use strict";
  $(function() {
    $(document).on('click', ".header_button", function(){
        $(".header_button").each(function(){
            $('body').removeClass($(this).attr('data-clr'));
        });
        $('body').addClass($(this).attr('data-clr'));
        $('#changetheme').modal('hide');
    });

    $(document).on('click', ".portlet_button", function(){
      $(".portlet_button").each(function(){
          $('body').removeClass($(this).attr('data-clr'));
      });
      $('body').addClass($(this).attr('data-clr'));
      $('#changetheme').modal('hide');
    });

    $(document).on('click',"#no_sidebar", function(){
      $('body').addClass('no_sidebar').siblings().removeClass('active');
    });

    // $(document).on('click', 'input:radio', function(){
    //   $('input:radio').each(function(){
    //       $('body').removeClass($(this).attr('data-cls'));
    //   });
    //   $('body').addClass($(this).attr('data-cls'));
    //   $('#changetheme').modal('hide');
    // });
    
  });
});