odoo.define('trustcode_documentation_insider.documentation', function (require) {
  'use strict';

  var ajax = require('web.ajax');
  $(document).ready(function () {
      function register_like(linkButton)  {
          let doc_id = $(linkButton).attr('data-id');
          let name = $(linkButton).attr('name');
          let url = '/document/like/' + doc_id;
          if (name == 'thumbs-down') {
              url = '/document/dislike/' + doc_id;
          }

          ajax.post(url, {}).then((result) => {
              $('.thumbs-like').fadeOut('slow');
              $('.thanks-like').fadeIn('slow');
          });
      };

      $('.thumbs-up-doc').click(function(e) {
          register_like(this);
      });
      $('.thumbs-down-doc').click(function(e) {
          register_like(this);
      });
  });
});
