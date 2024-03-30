 $(document).ready(function () {
            // Обработка нажатия на кнопку "Добавить вариант ответа"
            $('#addAnswerOption').click(function () {
                // Создаем новый элемент div для варианта ответа
                var newOptionDiv = $('<div class="form-group"></div>');

                // Первое поле с вводом текста
                var textField = $('<input type="text" class="form-control" name="answer_text[]" placeholder="Текст ответа">');

                // Второе поле - выпадающий список с выбором правильности ответа
                var correctSelect = $('<select class="form-control" name="correct_answer[]"></select>');
                var correctOptions = $('<option value="true">Правильный ответ</option><option value="false">Неправильный ответ</option>');

                // Добавляем опции в выпадающий список
                correctSelect.append(correctOptions);

                // Добавляем поля в новый элемент div
                newOptionDiv.append(textField);
                newOptionDiv.append(correctSelect);

                // Добавляем новый вариант ответа в контейнер
                $('#answerOptionsContainer').append(newOptionDiv);
            });
        });