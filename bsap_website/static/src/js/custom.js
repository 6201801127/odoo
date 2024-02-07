odoo.define('bsap_website.custom_js', function (require) {
    'use strict';

    var swiper;
    
    $(document).ready(function () {
        var swiper = new Swiper(".mySwiper", {
            slidesPerView: 5,
            spaceBetween: 10,
            freeMode: true,
            pagination: {
              el: ".swiper-pagination",
              clickable: true
            },
             navigation: {
              nextEl: ".swiper-button-next",
              prevEl: ".swiper-button-prev",
            },
             autoplay: {
             delay: 5000,
            },
              breakpoints: {
               320: {
                slidesPerView: 1
              },
              500: {
                slidesPerView: 1
              },
              700: {
                slidesPerView: 2
              },
              1366: {
                slidesPerView: 5
              },
              1920: {
                slidesPerView: 5
              }
            }
        });
    });

    $('.whitetheme').click(function(){
        body.className='o_connected_user lightMode';
    });
    $('.blacktheme').click(function(){
        body.className='o_connected_user darkMode';
    });
    // function darkMode(){
    //     body.className='darkMode';
    // }

    // $(document).ready(function () {
    $('#increasetext').click(function() {
        // curSize = parseInt($('.content').css('font-size')) + 2;
        if ((parseInt($('body').css('font-size')) + 2) <= 20)
        $('body').css('font-size', (parseInt($('body').css('font-size')) + 2));
    });
    
    $('#resettext').click(function() {
        if ((parseInt($('body').css('font-size')) + 2) != 18)
        $('body').css('font-size', 16);
    });
    
    $('#decreasetext').click(function() {
        if ((parseInt($('body').css('font-size')) - 2) >= 14)
        $('body').css('font-size', (parseInt($('body').css('font-size')) - 2));
    });
    // });
});