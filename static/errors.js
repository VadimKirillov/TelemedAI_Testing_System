$(document).ready(function () {
            // Обработка отправки формы
            $('#questionForm').submit(function (event) {
                // Предотвращаем стандартное поведение формы
                event.preventDefault();

                // Отправляем данные формы на сервер
                $.ajax({
                    type: 'POST',
                    url: '/create_question',
                    data: $('#questionForm').serialize(), // Сериализуем данные формы
                    success: function (response) {
                        // Перенаправляем на страницу с вопросами после успешного сохранения
                        window.location.href = "/question";
                    },
                    error: function (xhr, status, error) {
                        // Обработка ошибок при сохранении данных
                        console.error(xhr.responseText);
                        alert('Произошла ошибка при сохранении данных.');
                    }
                });
            });
        });