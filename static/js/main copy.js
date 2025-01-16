// Validación del formulario de preferencias
document.querySelector('form#user-profile-form').addEventListener('submit', function (event) {
    const preferencia = document.getElementById('preferencia').value.trim();
    const categoria = document.getElementById('categoria').value;

    if (!preferencia) {
        alert('Por favor, ingresa una preferencia.');
        event.preventDefault();
    } else if (!categoria) {
        alert('Por favor, selecciona un tipo de preferencia.');
        event.preventDefault();
    }
});

// Confirmación al eliminar preferencias
document.querySelectorAll('.btn-danger:not(#logout-button)').forEach(button => {
    button.addEventListener('click', function (event) {
        const confirmed = confirm('¿Estás seguro de que deseas eliminar esta preferencia?');
        if (!confirmed) {
            event.preventDefault();
        }
    });
});

// Confirmación al cerrar sesión
document.getElementById('logout-button').addEventListener('click', function (event) {
    const confirmed = confirm('¿Estás seguro de que deseas cerrar sesión?');
    if (!confirmed) {
        event.preventDefault();
    }
});

// Feedback visual tras guardar o eliminar
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.style.position = 'fixed';
    toast.style.top = '10px';
    toast.style.right = '10px';
    toast.style.zIndex = '1050';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    document.body.appendChild(toast);

    const bootstrapToast = new bootstrap.Toast(toast);
    bootstrapToast.show();

    setTimeout(() => {
        bootstrapToast.hide();
        document.body.removeChild(toast);
    }, 3000);
}






