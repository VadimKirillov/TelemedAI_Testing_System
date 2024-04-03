$(document).ready(function () {
    // Обработка нажатия на кнопку "Добавить вариант ответа"
    $('#addAnswerOption').click(function () {
        // Проверяем, есть ли уже 5 вариантов ответа
        if ($('#answerOptionsContainer').children().length >= 6) {
            $('#limitExceededModal').modal('show');
            return;
        }

        // Создаем новый элемент div для варианта ответа
        var newOptionDiv = $('<div class="form-group"></div>');

        // Первое поле с вводом текста
        var textField = $('<input type="text" class="form-control" name="answer_text[]" placeholder="Текст ответа">');

        // Второе поле - выпадающий список с выбором правильности ответа
        var correctSelect = $('<select class="form-control" name="correct_answer[]"></select>');
        var correctOptions = $('<option value="true">Правильный ответ</option><option value="false">Неправильный ответ</option>');

        // Добавляем опции в выпадающий список
        correctSelect.append(correctOptions);

        // Создаем кнопку для удаления
        var deleteButton = $('<button type="button" class="btn btn-danger deleteOption">Удалить</button>');

        // Добавляем поля и кнопку в новый элемент div
        newOptionDiv.append(textField);
        newOptionDiv.append(correctSelect);
        newOptionDiv.append(deleteButton);

        // Добавляем новый вариант ответа в контейнер
        $('#answerOptionsContainer').append(newOptionDiv);
    });

    // Обработка нажатия на кнопку "Удалить"
    $(document).on('click', '.deleteOption', function () {
        $(this).closest('.form-group').remove(); // Удаляем ближайший родительский элемент с классом .form-group
    });

    // Обработка отправки формы
    $('#questionForm').submit(function (event) {
        // Проверяем количество вариантов ответа
        if ($('#answerOptionsContainer').children().length < 3) {
            $('#minOptionsModal').modal('show');
            event.preventDefault(); // Отменяем отправку формы
        }
        // Проверяем количество вариантов ответа
        else if ($('#answerOptionsContainer').children().length > 5) {
            $('#maxOptionsModal').modal('show');
            event.preventDefault(); // Отменяем отправку формы
        }
    });
});
