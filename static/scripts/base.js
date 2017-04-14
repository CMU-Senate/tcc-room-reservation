'use strict';

/* global app */

$(document).ready(() => {
    $('.button-collapse').sideNav();

    $.ajaxPrefilter((options, originalOptions, jqXHR) => {
        jqXHR.setRequestHeader('X-CSRF-Token', app.csrfToken);
    });
});
