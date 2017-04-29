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

function allowedEvent(info) {
    const startsInFuture = info.start.isAfter($.fullCalendar.moment().stripZone()),
        validDuration = info.end.diff(info.start, 'hours') <= app.MAXIMUM_DURATION_HOURS;

    return startsInFuture && (validDuration || app.admin);
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
    if (event.editable && !event.cancelled && (event.user === app.userId || app.admin)) {
        $('#cancel-reservation-modal').modal('open');
        $('#cancel-reservation-modal').find('#cancel-reservation').data('reservation', event);
    }
}

function prepareEvent(event) {
    event.color = OTHER_RESERVATION_COLOR;

    const now = $.fullCalendar.moment().stripZone(),
        start = $.fullCalendar.moment(event.start).utc().stripZone();

    event.editable = !event.cancelled && start.isAfter(now) && (app.admin || event.user === app.userId);

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
            eventOverlap: stillEvent => stillEvent.cancelled,
            selectOverlap: event => event.cancelled,
            eventOrder: '-cancelled',
            timeFormat: 'hh:mm A',
            contentHeight: 'auto',
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
                start: app.admin ? now.clone().startOf('week') : now.clone().startOf('day'),
                end: now.clone().add(app.CALENDAR_DAYS_INTO_FUTURE, 'days'),
            }),
            selectAllow: allowedEvent,
            eventAllow: allowedEvent,
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
                if (event.editable) {
                    $(element).addClass('editable');

                    if (!event.cancelled && (event.user === app.userId || app.admin)) {
                        $(element).append(
                            $('<i class="material-icons tiny cancel-reservation-icon">delete</i>')
                                .css('background-color', $(element).css('background-color'))
                        );
                        $(element).attr('title', 'Click to cancel your reservation.');
                    }
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

        $(calendar).on({
            mouseenter: (event) => {
                const row = $(event.currentTarget);
                if (!row.html()) {
                    $('.fc-day', calendar).each((i, day) => {
                        let date = null;
                        if ($(day).data('date')) {
                            date = $.fullCalendar.moment(`${$(day).data('date')}T${row.parent('tr').data('time')}`).stripZone();
                        }

                        const cell = $('<td class="temp-cell"></td>').css({
                            width: $(day).width() + 1,
                            height: $(row).height(),
                        });
                        row.append(cell);
                        cell.hover(() => {
                            if (date !== null) {
                                const inFuture = date.isAfter($.fullCalendar.moment().stripZone()),
                                    overlappingEvents = $(calendar).fullCalendar(
                                      'clientEvents',
                                      x => !x.cancelled && date.isSameOrAfter(x.start) && date.isBefore(x.end)
                                    );

                                if (inFuture && !overlappingEvents.length) {
                                    cell.addClass('highlighted');
                                }
                            }
                        }, () => cell.removeClass('highlighted'));
                    });
                }
            },
            mouseleave: event => $(event.currentTarget).children('.temp-cell').remove(),
        }, '.fc-widget-content:not(.fc-axis)');
    });
}

$(document).ready(() => {
    init();
});
