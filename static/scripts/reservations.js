'use strict';

/* global app */

const RESERVATION_TOAST_DURATION_SECONDS = 3000;

// https://www.cmu.edu/marcom/brand-standards/web-standards.html#colors
const CANCELLED_RESERVATION_COLOR = '#666',
    MY_RESERVATION_COLOR = '#085',
    OTHER_RESERVATION_COLOR = '#247';

function startLoading(calendar) {
    $(calendar)
        .addClass('loading')
        .siblings('.loading-indicator')
            .addClass('loading');
}

function endLoading(calendar) {
    $(calendar)
        .removeClass('loading')
        .siblings('.loading-indicator')
            .removeClass('loading');
}

function toast(message) {
    Materialize.toast(message, RESERVATION_TOAST_DURATION_SECONDS);
}

function handleReservationCancel(event) {
    const reservation = $(event.target).data('reservation');
    $.post({
        url: `reservation/${reservation.id}/cancel`,
        success: response => toast(
            response.success
                ? 'Success! Your reservation was cancelled.'
                : `Failed to cancel your reservation: ${response.error}.`
        ),
        error: () => toast('Failed to cancel your reservation.'),
        complete: () => $(`.calendar[data-room-id="${reservation.room}"]`).fullCalendar('refetchEvents'),
    });
}

function handleEventClick(event) {
    if (!event.cancelled && (event.user === app.userId || app.admin)) {
        $('#cancel-reservation-modal').modal('open');
        $('#cancel-reservation-modal').find('#cancel-reservation').data('reservation', event);
    }
}

function prepareEvent(event) {
    event.color = OTHER_RESERVATION_COLOR;

    event.editable = !event.cancelled && (app.admin || event.user === app.userId);
    if (event.user === app.userId) {
        event.color = MY_RESERVATION_COLOR;
    }
    if (event.cancelled) {
        event.color = CANCELLED_RESERVATION_COLOR;
    }

    if (app.admin || event.user === app.userId) {
        event.title = event.user;
    }
    else {
        event.title = 'reserved';
    }

    return event;
}

function init() {
    $('#cancel-reservation-modal').modal();
    $('#cancel-reservation').click(handleReservationCancel);

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
            nowIndicator: true,
            header: {
                left: 'today',
                center: '',
                right: 'prev, next',
            },
            events: (start, end, _timezone, callback) => {
                startLoading(calendar);
                $.get({
                    url: `/reservations/${roomId}`,
                    data: {
                        start: start.clone().startOf('week').unix(),
                        end: end.unix(),
                    },
                    success: events => callback(events.map(prepareEvent)),
                });
            },
            select: (start, end) => {
                startLoading(calendar);
                $.post({
                    url: '/reservation/add',
                    data: {
                        room: roomId,
                        start: start.unix(),
                        end: end.unix(),
                    },
                    success: response => toast(
                        response.success
                            ? 'Success! Your reservation has been made.'
                            : `Failed to create a reservation: ${response.error}.`
                    ),
                    error: () => toast('Failed to create a reservation.'),
                    complete: () => $(calendar).fullCalendar('refetchEvents'),
                });
            },
            validRange: now => ({
                start: now.clone().subtract(1, 'days'),
                end: now.clone().add(app.CALENDAR_DAYS_INTO_FUTURE, 'days'),
            }),
            selectAllow: info => info.end.diff(info.start, 'hours') <= app.MAXIMUM_DURATION_HOURS || app.admin,
            eventAllow: info => info.end.diff(info.start, 'hours') <= app.MAXIMUM_DURATION_HOURS || app.admin,
            eventClick: handleEventClick,
            eventDrop: (event) => {
                startLoading(calendar);
                $.post({
                    url: `reservation/${event.id}/edit`,
                    data: {
                        room: roomId,
                        start: event.start.unix(),
                        end: event.end.unix(),
                    },
                    success: response => toast(
                        response.success
                            ? 'Success! Your reservation was edited.'
                            : `Failed to edit your reservation: ${response.error}.`
                    ),
                    error: () => toast('Failed to edit your reservation.'),
                    complete: () => $(`.calendar[data-room-id="${event.room}"]`).fullCalendar('refetchEvents'),
                });
            },
            eventResize: (event) => {
                startLoading(calendar);
                $.post({
                    url: `reservation/${event.id}/edit`,
                    data: {
                        room: roomId,
                        start: event.start.unix(),
                        end: event.end.unix(),
                    },
                    success: response => toast(
                        response.success
                            ? 'Success! Your reservation was edited.'
                            : `Failed to edit your reservation: ${response.error}.`
                    ),
                    error: () => toast('Failed to edit your reservation.'),
                    complete: () => $(`.calendar[data-room-id="${event.room}"]`).fullCalendar('refetchEvents'),
                });
            },
            eventRender: (event, element) => {
                if (!event.cancelled && (event.user === app.userId || app.admin)) {
                    $(element).append(
                        $('<i class="material-icons tiny cancel-reservation-icon">delete</i>')
                            .css('background-color', $(element).css('background-color'))
                    );
                    $(element).attr('title', 'Click to cancel your reservation.');
                    $(element).css('cursor', 'pointer');
                }
            },
            eventAfterAllRender: () => endLoading(calendar),
            viewRender: () => {
                $('button', calendar).addClass('btn waves-effect waves-light red darken-4');
                if ($('.fc-center #help-text', calendar).length === 0) {
                    $('.fc-center', calendar).append(
                        $(`<div id="help-text">
                            Click and drag to create your reservation. Edit a reservation by resizing or dragging and dropping it.
                           </div>`)
                    );
                }
            },
        });

        $('.fc-widget-content', calendar).hover(() => {
            const row = $(event.currentTarget);
            if (!row.html()) {
                $('.fc-day', calendar).each((i, day) => {
                    row.append($(`<td class="temp-cell" style="width: ${$(day).width() + 1}px"></td>`));
                });
            }
        }, (event) => {
            $(event.currentTarget).children('.temp-cell').remove();
        });
    });
}

$(document).ready(() => {
    init();
});
