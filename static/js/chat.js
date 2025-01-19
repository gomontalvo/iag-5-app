function onLoad() {
    const messageInput = document.getElementById('messageInput');
    const submitButton = document.getElementById('send-message');
    const form = document.querySelector('form');
    const logoutForm = document.getElementById('logout-form');

    // Manejador de cierre de sesión
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
                this.submit();
            }
        });
    }

    // Estado inicial del botón de envío basado en el input
    function updateSubmitButton() {
        const isEmpty = !messageInput.value.trim();
        submitButton.disabled = isEmpty;
        if (isEmpty) {
            submitButton.classList.add('disabled');
        } else {
            submitButton.classList.remove('disabled');
        }
    }

    // Actualizar estado del botón cuando cambia el input
    messageInput.addEventListener('input', updateSubmitButton);

    // Manejar envío del formulario
    form.addEventListener('submit', async (event) => {
        // Solo prevenir default y validar si no es un botón predefinido
        const submitter = event.submitter;
        if (submitter && submitter.name === 'intent' && submitter.classList.contains('btn-success')) {
            // Permitir que los botones predefinidos funcionen normalmente
            return;
        }

        event.preventDefault();

        // Verificar mensaje vacío
        const messageContent = messageInput.value.trim();
        if (!messageContent) {
            return; // No enviar si está vacío
        }

        const formData = new FormData(form);

        // Deshabilitar input y botón mientras se envía
        submitButton.disabled = true;
        messageInput.disabled = true;
        submitButton.textContent = 'Enviando...';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const message = await response.json();
            
            // Limpiar y resetear input después del envío exitoso
            messageInput.value = '';
            updateSubmitButton();

        } catch (error) {
            console.error('Error:', error);
            alert('Hubo un error al enviar el mensaje. Por favor, intenta de nuevo.');
        } finally {
            // Re-habilitar input y botón
            submitButton.disabled = false;
            messageInput.disabled = false;
            submitButton.textContent = 'Enviar';
        }
    });

    // Establecer estado inicial del botón
    updateSubmitButton();

    // Auto-scroll al último mensaje
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', onLoad);