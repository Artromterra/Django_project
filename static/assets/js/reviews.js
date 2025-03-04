$(document).ready(function (product_id) {
    let productId = $("#reviews").data("product-id");
    productId = parseInt(productId, 10);
    console.log("Product id:", productId)
    let list_reviews_url = $("#reviews").data("list-reviews-url")
    console.log("List reviews url:", list_reviews_url)
    let create_review_url = $("#reviews").data("create-review-url")
    console.log("New review url:", create_review_url)
    let init_limit = 5
    let limit = init_limit;
    let delta = 5;

    function loadReviews() {
        // отправляем с помощью AJAX запрос на сервер для получения списка отзывов
        $.ajax({
            url: list_reviews_url,
            type: "GET",
            data: { limit: limit, product_id: productId },
            dataType: "html",
            success: function (response) {
                // Создаем временный контейнер для разбора HTML
                let tempDiv = document.createElement("div");
                tempDiv.innerHTML = response; // Вставляем HTML в контейнер

                // Находим все элементы списка отзывов
                let reviews = tempDiv.querySelectorAll("#review-list-ul li");
                console.log("Number of reviews:", reviews.length);

                console.log("Limit:", limit)
                let reviewsList = $("#reviews-list-container");

                // заменяем html на полученный от сервера
                reviewsList.html(response);

                // если количество отзывов меньше limit - загружены все отзывы, => убираем кнопку Показать еще
                if (reviews.length < limit) {
                    $("#load-reviews").hide();
                }

                // Увеличиваем limit при каждом вызове функции, чтобы каждый раз загружать больше отзывов
                limit += delta;
            },
            error: function (xhr, status, error) {
                console.error("Server response:", xhr.responseText);
                console.error("Ошибка запроса:", status, error);
            }
        });
        // Отправляем ajax для получения формы для создания отзыва
        $.ajax({
            url: create_review_url,
            type: "GET",
            dataType: "html",
            success: function (response) {
                let reviewForm = $("#reviews-new-container");

                // перед этим заменили на список отзывов, теперь нужно просто добавить форму
                reviewForm.html(response);
            },
            error: function (xhr, status, error) {
                console.error("Server response:", xhr.responseText);
                console.error("Ошибка запроса:", status, error);
            }
        });
    };

    function createReview(event) {
        // Предотвращаем обновление страницы при отправки формы
        event.preventDefault();

        let formData = $(this).serialize();
        formData += "&product_id=" + productId;

        // отправляем форму на сервер с помощью AJAX
        $.ajax({
            url: create_review_url,
            type: 'POST',
            data: formData,
            success: function(response) {
                // сбрасываем форму до дефолтного состояния
                $('#review-form').trigger('reset');
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
    // $("#load-reviews").click(loadReviews);
    // Привязываем обработчик события через делегирование
    $(document).on('click', '#load-reviews', function () {
        loadReviews();
    });

    // При нажатии кнопки Добавить отзыв - отправляем форму на сервер и грузим отзывы
    // Привязываем обработчик события через делегирование
    $(document).on('submit', '#review-form', function (event) {
        createReview.call(this, event);
    });
});
