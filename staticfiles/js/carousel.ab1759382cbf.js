$(document).ready(function() {
    setInterval(function() {
        $('.carousel').carousel('next');
    }, 5000);
});

document.addEventListener('DOMContentLoaded', function () {
    const headers = document.querySelectorAll('.toggle-header');
    headers.forEach(header => {
        const contentId = header.getAttribute('data-target');
        const contentElement = document.getElementById(contentId);

        // Agregar evento de clic al header
        header.addEventListener('click', function () {
            if (header.classList.contains('collapsed')) {
                // Mostrar contenido
                contentElement.style.display = 'block';
                header.classList.remove('collapsed');
                header.classList.add('expanded');
            } else {
                // Ocultar contenido
                contentElement.style.display = 'none';
                header.classList.remove('expanded');
                header.classList.add('collapsed');
            }
        });

        // Inicialmente ocultar el contenido
        contentElement.style.display = 'none';
        header.classList.add('collapsed'); // Marcar como colapsado inicialmente
    });
});