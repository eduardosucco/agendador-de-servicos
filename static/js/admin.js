document.addEventListener('DOMContentLoaded', async function() {
    const response = await fetch('/api/appointments');
    const appointments = await response.json();
    const tbody = document.querySelector('#appointments-table tbody');

    appointments.forEach(app => {
        const tr = document.createElement('tr');

        const idTd = document.createElement('td');
        idTd.textContent = app.id;
        tr.appendChild(idTd);

        const clientTd = document.createElement('td');
        clientTd.textContent = app.clients.name;
        tr.appendChild(clientTd);

        const serviceTd = document.createElement('td');
        serviceTd.textContent = app.service;
        tr.appendChild(serviceTd);

        const timeTd = document.createElement('td');
        const appointmentDate = new Date(app.appointment_time);
        timeTd.textContent = appointmentDate.toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
        tr.appendChild(timeTd);

        tbody.appendChild(tr);
    });
});
