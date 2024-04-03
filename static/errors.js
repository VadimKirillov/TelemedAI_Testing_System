// Обработка отправки формы
$('#questionForm').submit(function (event) {
    // Предотвращаем стандартное поведение формы
    event.preventDefault();

    // Создаем объект FormData для передачи данных формы
    var formData = new FormData(this);

    // Отправляем данные формы на сервер
    $.ajax({
        type: 'POST',
        url: '/create_question',
        data: formData,
        processData: false,  // Отключаем обработку данных перед отправкой
        contentType: false,  // Отключаем установку Content-Type заголовка
        success: function (response) {
            // Перенаправляем на страницу с вопросами после успешного сохранения
            window.location.href = "/question";
        },
        error: function (xhr, status, error) {
            // Обработка ошибок при сохранении данных
            console.error(xhr.responseText);
            $('#errorModal').modal('show');
        }
    });
});
