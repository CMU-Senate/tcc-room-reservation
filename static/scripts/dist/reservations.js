'use strict';$(document).ready(function(){$('#calendar').fullCalendar({defaultView:'agendaWeek',allDaySlot:!1,selectable:!0,eventOverlap:!1,header:{left:'today',center:'',right:'prev, next'},validRange:function validRange(a){return{start:a,end:a.clone().add(10,'days')}}})});
//# sourceMappingURL=reservations.js.map
