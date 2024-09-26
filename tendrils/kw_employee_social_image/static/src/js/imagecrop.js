odoo.define('kw_employee_social_image.imagecrop', function (require) {
    'use strict';
    var ajax = require('web.ajax');

    var image_crop = {
        init: function (){
            image_crop.imageCropWeb();
        },

        imageCropWeb: function(){
            var $modal = $('#modal');
            var image = document.getElementById('image');

            // var cropper;
            $("body").on("change", ".social_image", function(e) {
                var files = e.target.files;
                console.log(files)
                var done = function(url) {
                    console.log(url)
                    console.log(image)
                    image.src = url;
                    $modal.modal('show');
                };
                var reader;
                var file;
                // var url;
                if (files && files.length > 0) {
                    file = files[0];
                    if (URL) {
                        done(URL.createObjectURL(file));
                    } else if (FileReader) {
                        reader = new FileReader();
                        reader.onload = function(e) {
                            done(reader.result);
                        };
                        reader.readAsDataURL(file);
                    }
                }
            });
            $modal.on('shown.bs.modal', function() {
                image_crop.cropper = new Cropper(image, {
                    aspectRatio: 32 / 21,
                    viewMode: 2,
                    preview: '.preview',
                    dragCrop: false,
                    cropBoxMovable: true,
                    cropBoxResizable: true,
                    minCropBoxWidth: 96,
                    minCropBoxHeight: 63,
                    dragMode: 'move',
                });
            }).on('hidden.bs.modal', function() {
                image_crop.cropper.destroy();
                image_crop.cropper = null;
            });
            $("#crop").click(function() {
                image_crop.canvas = image_crop.cropper.getCroppedCanvas({
                    width: 96,
                    height: 63,
                    imageSmoothingQuality : "high",
                    imageSmoothingEnabled : true,
                });
                image_crop.canvas.toBlob(function(blob) {
                    image_crop.url = URL.createObjectURL(blob);
                    var reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = function() {
                        var base64data = reader.result;

                        ajax.jsonRpc("/candid-image/submit-image", 'call', {'socialPhoto' :base64data})
                            .then(function (response) {
                                console.log(response);
                                window.location.href = response.url
                                //alert("Crop image successfully uploaded");
                            });
                        // console.log(base64data);
                        // $('.final-preview').html("<img scr='"+base64data+"'/>");

                    }

                });
            })
            
        },
    };
   

    $(function(){
        image_crop.init();
    });
});


