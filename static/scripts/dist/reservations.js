'use strict';

$(document).ready(function () {
    $('#calendar').fullCalendar({
        defaultView: 'agendaWeek',
        allDaySlot: false,
        selectable: true,
        eventOverlap: false,
        header: {
            left: 'today',
            center: '',
            right: 'prev, next'
        },
        validRange: function validRange(now) {
            return {
                start: now,
                end: now.clone().add(10, 'days')
            };
        }
    });
});
//# sourceMappingURL=reservations.js.map
