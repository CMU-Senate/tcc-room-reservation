'use strict';

/* global app */

const CALENDAR_DAYS_INTO_FUTURE = 10,
    RESERVATION_TOAST_DURATION_SECONDS = 3000;

$(document).ready(() => {
    $('.calendar').each((_i, calendar) => {
        const roomId = $(calendar).data('room-id');
        $(calendar).fullCalendar({
            defaultView: 'agendaWeek',
            allDaySlot: false,
            selectable: true,
            eventOverlap: false,
            // TODO: add editable
            // TODO: add deletion
            header: {
                left: 'today',
                center: '',
                right: 'prev, next',
            },
            events: (start, end, _timezone, callback) => {
                $.get({
                    url: `/reservations/${roomId}`,
                    data: {
                        start: start.clone().startOf('week').unix(),
                        end: end.unix(),
                    },
                    success: (events) => {
                        callback(events.map(
                            (event) => {
                                if (event.user === app.userId) {
                                    event.color = 'green';
                                }
                                if (event.cancelled) {
                                    event.color = 'lightgray';
                                }

                                return event;
                            }
                        ));
                    },
                });
            },
            select: (start, end) => {
                $.post({
                    url: '/reservation/add',
                    data: {
                        room: roomId,
                        start: start.unix(),
                        end: end.unix(),
                    },
                    success: (response) => {
                        if (response.success) {
                            Materialize.toast('Success! Your reservation has been made.', RESERVATION_TOAST_DURATION_SECONDS);
                        }
                        else {
                            Materialize.toast(`Failed to create a reservation: ${response.error}.`, RESERVATION_TOAST_DURATION_SECONDS);
                        }
                        app.csrfToken = response.csrf_token;
                    },
                    error: () => {
                        Materialize.toast('Failed to create a reservation.', RESERVATION_TOAST_DURATION_SECONDS);
                    },
                    complete: () => {
                        $(calendar).fullCalendar('refetchEvents');
                    },
                });
            },
            validRange: function (now) {
                return {
                    start: now,
                    end: now.clone().add(CALENDAR_DAYS_INTO_FUTURE, 'days'),
                };
            },
        });
    });
});
