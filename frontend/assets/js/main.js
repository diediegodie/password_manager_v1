// main.js - Handles frontend logic for register.html and other pages

document.addEventListener('DOMContentLoaded', function () {
    // Registration handler (register.html)
    const registerForm = document.querySelector('.auth-form');
    if (registerForm && window.location.pathname.includes('register')) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const submitBtn = registerForm.querySelector('.auth-submit');
            submitBtn.disabled = true;

            // Remove previous messages
            let oldMsg = document.querySelector('.auth-message');
            if (oldMsg) oldMsg.remove();

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });
                const data = await response.json();
                let msg = document.createElement('div');
                msg.className = 'auth-message';
                if (response.status === 201) {
                    msg.textContent = 'Registration successful! You can now log in.';
                    msg.style.color = 'green';
                    registerForm.reset();
                } else {
                    msg.textContent = data.message || 'Registration failed.';
                    msg.style.color = 'red';
                }
                registerForm.appendChild(msg);
            } catch (err) {
                let msg = document.createElement('div');
                msg.className = 'auth-message';
                msg.textContent = 'Network error. Please try again.';
                msg.style.color = 'red';
                registerForm.appendChild(msg);
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // Login handler (login.html)
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const submitBtn = loginForm.querySelector('.auth-submit');
            submitBtn.disabled = true;

            // Remove previous messages
            let oldMsg = document.querySelector('.auth-message');
            if (oldMsg) oldMsg.remove();

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();
                let msg = document.createElement('div');
                msg.className = 'auth-message';
                if (response.ok && data.access_token) {
                    msg.textContent = 'Login successful! Redirecting...';
                    msg.style.color = 'green';
                    // Optionally store token in localStorage/sessionStorage
                    // localStorage.setItem('access_token', data.access_token);
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1200);
                } else {
                    msg.textContent = data.error || data.message || 'Login failed.';
                    msg.style.color = 'red';
                }
                loginForm.appendChild(msg);
            } catch (err) {
                let msg = document.createElement('div');
                msg.className = 'auth-message';
                msg.textContent = 'Network error. Please try again.';
                msg.style.color = 'red';
                loginForm.appendChild(msg);
            } finally {
                submitBtn.disabled = false;
            }
        });
    }
    // Vault dashboard logic (index.html)
    if (window.location.pathname.includes('index.html')) {
        const vaultEntries = document.getElementById('vaultEntries');
        const addEntryBtn = document.getElementById('addEntryBtn');
        const entryFormModal = document.getElementById('entryFormModal');
        const closeModal = document.getElementById('closeModal');
        const entryForm = document.getElementById('entryForm');
        const logoutBtn = document.getElementById('logoutBtn');

        // Helper: get token
        function getToken() {
            return localStorage.getItem('access_token');
        }

        // Fetch and render vault entries
        async function loadEntries() {
            vaultEntries.innerHTML = '<div>Loading...</div>';
            try {
                const resp = await fetch('/api/vault/', {
                    headers: { 'Authorization': 'Bearer ' + getToken() }
                });
                if (!resp.ok) throw new Error('Failed to load entries');
                const data = await resp.json();
                if (!Array.isArray(data.entries)) throw new Error('Malformed response');
                if (data.entries.length === 0) {
                    vaultEntries.innerHTML = '<div class="empty">No entries yet.</div>';
                } else {
                    vaultEntries.innerHTML = '';
                    data.entries.forEach(entry => {
                        const card = document.createElement('div');
                        card.className = 'vault-card';
                        card.innerHTML = `
                            <div class="vault-service">${entry.service}</div>
                            <div class="vault-username">${entry.username}</div>
                            <div class="vault-password">${entry.password ? '••••••••' : ''}</div>
                            <button class="app-btn app-btn--small edit-entry" data-id="${entry.id}">Edit</button>
                            <button class="app-btn app-btn--small delete-entry" data-id="${entry.id}">Delete</button>
                        `;
                        vaultEntries.appendChild(card);
                    });
                }
            } catch (err) {
                vaultEntries.innerHTML = '<div class="error">Failed to load entries.</div>';
            }
        }

        // Show modal
        function showModal(editing = false, entry = null) {
            entryForm.reset();
            entryForm.dataset.editing = editing ? '1' : '';
            entryForm.dataset.entryId = editing && entry ? entry.id : '';
            if (editing && entry) {
                entryForm.service.value = entry.service;
                entryForm.username.value = entry.username;
                entryForm.password.value = entry.password;
            }
            entryFormModal.style.display = 'block';
        }
        function hideModal() {
            entryFormModal.style.display = 'none';
        }

        // Add entry
        addEntryBtn && addEntryBtn.addEventListener('click', () => showModal(false));
        closeModal && closeModal.addEventListener('click', hideModal);

        // Save entry (add or edit)
        entryForm && entryForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const service = entryForm.service.value.trim();
            const username = entryForm.username.value.trim();
            const password = entryForm.password.value;
            const editing = entryForm.dataset.editing === '1';
            const entryId = entryForm.dataset.entryId;
            let url = '/api/vault/';
            let method = 'POST';
            if (editing && entryId) {
                url += entryId;
                method = 'PUT';
            }
            try {
                const resp = await fetch(url, {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + getToken()
                    },
                    body: JSON.stringify({ service, username, password })
                });
                if (!resp.ok) throw new Error('Failed to save entry');
                hideModal();
                loadEntries();
            } catch (err) {
                alert('Failed to save entry.');
            }
        });

        // Edit/delete handlers
        vaultEntries && vaultEntries.addEventListener('click', async function (e) {
            if (e.target.classList.contains('edit-entry')) {
                const id = e.target.dataset.id;
                // Fetch entry details (or reuse from loaded data if available)
                try {
                    const resp = await fetch('/api/vault/' + id, {
                        headers: { 'Authorization': 'Bearer ' + getToken() }
                    });
                    if (!resp.ok) throw new Error();
                    const entry = await resp.json();
                    showModal(true, entry);
                } catch {
                    alert('Failed to load entry.');
                }
            } else if (e.target.classList.contains('delete-entry')) {
                const id = e.target.dataset.id;
                if (confirm('Delete this entry?')) {
                    try {
                        const resp = await fetch('/api/vault/' + id, {
                            method: 'DELETE',
                            headers: { 'Authorization': 'Bearer ' + getToken() }
                        });
                        if (!resp.ok) throw new Error();
                        loadEntries();
                    } catch {
                        alert('Failed to delete entry.');
                    }
                }
            }
        });

        // Logout
        logoutBtn && logoutBtn.addEventListener('click', function () {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
        });

        // Modal close on outside click
        window.onclick = function (event) {
            if (event.target === entryFormModal) hideModal();
        };

        // On load, check auth and load entries
        if (!getToken()) {
            window.location.href = 'login.html';
        } else {
            loadEntries();
        }
    }
});
