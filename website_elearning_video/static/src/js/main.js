odoo.define("website_slide_video.website_slide_video",function(require){
    "use strict";
    var publicWidget = require('web.public.widget');
    var fullscreen = require('website_slides.fullscreen');
    publicWidget.registry.websiteSlidesFullscreenPlayer.include({
        xmlDependencies: (publicWidget.registry.websiteSlidesFullscreenPlayer.prototype.xmlDependencies || [])
        .concat(['/website_elearning_video/static/xml/extend_video_slides.xml']),
    })
    $( document ).ready(function() {
      $(document).on('contextmenu', '.video-file video', function (ev) {
        ev.preventDefault();
      })
    })
})
