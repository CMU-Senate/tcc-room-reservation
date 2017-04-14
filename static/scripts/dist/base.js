'use strict';var HTTP_OK=200;$(document).ready(function(){$('.button-collapse').sideNav(),$.ajaxPrefilter(function(a,b,c){c.setRequestHeader('X-CSRF-Token',app.csrfToken)}),$(document).ajaxComplete(function(a,b){b.status===HTTP_OK&&b.responseJSON&&b.responseJSON.csrf_token&&(app.csrfToken=b.responseJSON.csrf_token)})});
//# sourceMappingURL=base.js.map
