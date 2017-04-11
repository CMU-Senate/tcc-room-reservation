'use strict';

$(document).ready(() => {
    $('.calendar').fullCalendar({
        defaultView: 'agendaWeek',
        allDaySlot: false,
        selectable: true,
        eventOverlap: false,
        header: {
            left: 'today',
            center: '',
            right: 'prev, next',
        },
        validRange: function (now) {
            return {
                start: now,
                end: now.clone().add(10, 'days'),
            };
        },
    });
});
