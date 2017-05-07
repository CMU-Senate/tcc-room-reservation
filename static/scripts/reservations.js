'use strict';

/* global app */

$(document).ready(() => {
    const columnOffset = app.admin ? 1 : 0;

    // eslint-disable-next-line new-cap
    $('#reservations').DataTable({
        pageLength: 25,
        order: [[0, 'asc'], [1, 'desc']].map(([i, o]) => [i + columnOffset, o]),
        initComplete: () => {
            $('.dataTables_length select').addClass('browser-default');
        },
        drawCallback: () => {
            $('.paginate_button').removeClass('paginate_button').addClass('btn-flat');
        },
    });
});
