'use strict';$(document).ready(function(){$('.button-collapse').sideNav(),$.ajaxPrefilter(function(a,b,c){c.setRequestHeader('X-CSRF-Token',app.csrfToken)})});
//# sourceMappingURL=base.js.map
