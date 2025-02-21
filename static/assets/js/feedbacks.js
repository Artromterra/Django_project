$(document).ready(function (product_id) {
    let productId = $("#reviews").data("product-id");
    let list_reviews_url = $("#reviews").data("list-reviews-url")
    let create_review_url = $("#reviews").data("create-review-url")
    let init_limit = 5
    let limit = init_limit;
    let delta = 5;

    function loadFeedbacks() {
        // отправляем с помощью AJAX запрос на сервер для получения списка отзывов
        $.ajax({
            url: list_reviews_url,
            type: "GET",
            data: { limit: limit, product_id: product_id },
            dataType: "json",
            success: function (response) {
                let reviewsList = $("#reviews");

                // заменяем html на полученный от сервера
                reviewsList.html(response.html);

                // если количество отзывов меньше limit - загружены все отзывы, => убираем кнопку Показать еще
                if ($(response.html).length < limit) {
                    $("#load-reviews").hide();
                }

                // Увеличиваем limit при каждом вызове функции, чтобы каждый раз загружать больше отзывов
                limit += delta;
            },
            error: function (xhr, status, error) {
                console.error("Ошибка запроса:", status, error);
            }
        });
    };

    function createFeedback() {
        // Предотвращаем обновление страницы при отправки формы
        event.preventDefault();

        var formData = $(this).serialize();

        // отправляем форму на сервер с помощью AJAX
        $.ajax({
            url: create_review_url,
            type: 'POST',
            data: formData,
            success: function(response) {
                // сбрасываем форму до дефолтного состояния
                $('#feedback-form').trigger('reset');
                //грузим дефолтное количество отзывов
                limit = init_limit;
                loadReviews();
            },
            error: function(xhr, status, error) {
                $('#response').html('Ошибка запроса: ' + error);
            }
        });
    };

    // Загружаем дефолтное количество отзывов при загрузке страницы
    loadReviews();

    // При нажатии кнопки Показать еще загружаем увеличенное количество отзывов
    $("#load-reviews").click(loadReviews);

    // При нажатии кнопки Добавить отзыв - отправляем форму на сервер и грузим отзывы
    $('#review-form').on('submit', createFeedback);
});
