document.getElementById('appointment-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch('/api/appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        alert('Agendamento realizado com sucesso!');
        e.target.reset();
    } else {
        alert('Erro ao agendar. Tente novamente.');
    }
});
