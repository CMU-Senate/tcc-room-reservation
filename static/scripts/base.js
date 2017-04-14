'use strict';

/* global app */

const HTTP_OK = 200;

$(document).ready(() => {
    $('.button-collapse').sideNav();

    $.ajaxPrefilter((options, originalOptions, jqXHR) => {
        jqXHR.setRequestHeader('X-CSRF-Token', app.csrfToken);
    });

    $(document).ajaxComplete((event, xhr) => {
        if (xhr.status === HTTP_OK && xhr.responseJSON && xhr.responseJSON.csrf_token) {
            app.csrfToken = xhr.responseJSON.csrf_token;
        }
    });
});
