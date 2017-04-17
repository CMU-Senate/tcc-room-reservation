'use strict';

/* global app */

const RESERVATION_TOAST_DURATION_SECONDS = 3000;

$(document).ready(() => {
    $('#cancel-reservation-modal').modal();

    $('#cancel-reservation').click((event) => {
        const reservation = $(event.target).data('reservation');
        $.post({
            url: `reservation/${reservation.id}/cancel`,
            success: (response) => {
                if (response.success) {
                    Materialize.toast('Success! Your reservation was cancelled.', RESERVATION_TOAST_DURATION_SECONDS);
                }
                else {
                    Materialize.toast(`Failed to cancel your reservation: ${response.error}.`, RESERVATION_TOAST_DURATION_SECONDS);
                }
            },
            error: () => Materialize.toast('Failed to cancel your reservation.', RESERVATION_TOAST_DURATION_SECONDS),
            complete: () => $(`.calendar[data-room-id="${reservation.room}"]`).fullCalendar('refetchEvents'),
        });
    });

    $('.calendar').each((_i, calendar) => {
        const roomId = $(calendar).data('room-id');
        $(calendar).fullCalendar({
            defaultView: 'agendaWeek',
            allDaySlot: false,
            selectable: true,
            eventOverlap: stillEvent => stillEvent.canceled,
            selectOverlap: event => event.cancelled,
            eventOrder: '-cancelled',
            timeFormat: 'hh:mm A',
            contentHeight: 'auto',
            editable: true,
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
                                event.editable = !event.cancelled;
                                if (event.user === app.userId) {
                                    event.color = 'green';
                                }
                                if (event.cancelled) {
                                    event.color = 'gray';
                                }
                                if (app.admin) {
                                    event.title = event.user;
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
                    },
                    error: () => Materialize.toast('Failed to create a reservation.', RESERVATION_TOAST_DURATION_SECONDS),
                    complete: () => $(calendar).fullCalendar('refetchEvents'),
                });
            },
            validRange: function (now) {
                return {
                    start: now.clone().subtract(1, 'days'),
                    end: now.clone().add(app.CALENDAR_DAYS_INTO_FUTURE, 'days'),
                };
            },
            selectAllow: info => info.end.diff(info.start, 'hours') <= app.MAXIMUM_DURATION_HOURS || app.admin,
            eventAllow: info => info.end.diff(info.start, 'hours') <= app.MAXIMUM_DURATION_HOURS || app.admin,
            eventClick: (event) => {
                if (!event.cancelled && (event.user === app.userId || app.admin)) {
                    $('#cancel-reservation-modal').modal('open');
                    $('#cancel-reservation-modal').find('#cancel-reservation').data('reservation', event);
                }
            },
            eventDrop: (event) => {
                $.post({
                    url: `reservation/${event.id}/edit`,
                    data: {
                        room: roomId,
                        start: event.start.unix(),
                        end: event.end.unix(),
                    },
                    success: (response) => {
                        if (response.success) {
                            Materialize.toast('Success! Your reservation was edited.', RESERVATION_TOAST_DURATION_SECONDS);
                        }
                        else {
                            Materialize.toast(`Failed to edit your reservation: ${response.error}.`, RESERVATION_TOAST_DURATION_SECONDS);
                        }
                    },
                    error: () => Materialize.toast('Failed to edit your reservation.', RESERVATION_TOAST_DURATION_SECONDS),
                    complete: () => $(`.calendar[data-room-id="${event.room}"]`).fullCalendar('refetchEvents'),
                });
            },
            eventResize: (event) => {
                $.post({
                    url: `reservation/${event.id}/edit`,
                    data: {
                        room: roomId,
                        start: event.start.unix(),
                        end: event.end.unix(),
                    },
                    success: (response) => {
                        if (response.success) {
                            Materialize.toast('Success! Your reservation was edited.', RESERVATION_TOAST_DURATION_SECONDS);
                        }
                        else {
                            Materialize.toast(`Failed to edit your reservation: ${response.error}.`, RESERVATION_TOAST_DURATION_SECONDS);
                        }
                    },
                    error: () => Materialize.toast('Failed to edit your reservation.', RESERVATION_TOAST_DURATION_SECONDS),
                    complete: () => $(`.calendar[data-room-id="${event.room}"]`).fullCalendar('refetchEvents'),
                });
            },
            eventRender: (event, element) => {
                if (!event.cancelled && (event.user === app.userId || app.admin)) {
                    $(element).append($('<i class="material-icons tiny cancel-reservation-icon">delete</i>'));
                    $(element).css('cursor', 'pointer');
                }
            },
            viewRender: () => {
                $('button', calendar).addClass('btn waves-effect waves-light red darken-4');
            },
        });
    });
});
