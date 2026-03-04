function runOptOut() {
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    const progressBar = document.getElementById('optoutProgress');
    const statusText = document.getElementById('optoutStatus');

    // Gather selected brokers from checkboxes (empty = all)
    const checked = [...document.querySelectorAll('.broker-check:checked')].map(el => el.value);

    modal.show();
    progressBar.style.width = '5%';
    progressBar.classList.remove('bg-danger');
    statusText.textContent = 'Starting opt-out process…';

    fetch('/run_optout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brokers: checked.length ? checked : [] })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'already_running') {
            statusText.textContent = 'A batch is already running — check back soon.';
            return;
        }

        // Poll /api/status every second until done
        const poll = setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(s => {
                    const pct = s.total > 0 ? Math.round((s.processed / s.total) * 100) : 10;
                    progressBar.style.width = pct + '%';
                    progressBar.setAttribute('aria-valuenow', pct);

                    if (s.running && s.current_broker) {
                        statusText.innerHTML =
                            `Processing <strong>${s.current_broker}</strong> &nbsp;` +
                            `(${s.processed} / ${s.total})`;
                    } else if (!s.running) {
                        clearInterval(poll);
                        progressBar.style.width = '100%';
                        statusText.innerHTML =
                            `Done — ${s.successful} succeeded, ` +
                            `${s.partial} partial, ${s.failed} failed.`;
                        setTimeout(() => { modal.hide(); location.reload(); }, 3000);
                    }
                })
                .catch(() => { /* ignore transient fetch errors during polling */ });
        }, 1000);
    })
    .catch(err => {
        statusText.textContent = 'Error starting opt-out: ' + err.message;
        progressBar.style.width = '0%';
        progressBar.classList.add('bg-danger');
    });
}

function handleConfigSubmit(e) {
    e.preventDefault();
    const form = e.target;
    
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => {
        if (response.ok) {
            showToast('Configuration saved successfully!', 'success');
        } else {
            throw new Error('Server error');
        }
    })
    .catch(error => {
        showToast('Error saving configuration', 'danger');
    });
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    new bootstrap.Toast(toast).show();
    setTimeout(() => toast.remove(), 5000);
}
