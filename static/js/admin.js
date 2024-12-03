document.addEventListener('DOMContentLoaded', async function() {
    const response = await fetch('/api/appointments');
    const appointments = await response.json();

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: appointments.map(app => ({
            title: `${app.clients.name} - ${app.service}`,
            start: app.appointment_time,
            allDay: false
        }))
    });

    calendar.render();
});
