import requests

# Задаем параметры для доступа к сервису
recommendation_service_url = "http://127.0.0.1:4601"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def post_request(url, headers, params):
    """
    Выполняет POST-запрос к указанному URL с заданными заголовками и параметрами.
    
    Args:
        url (str): URL, к которому будет выполнен запрос.
        headers (dict): Заголовки запроса.
        params (dict): Параметры запроса.

    Returns:
        dict or None: Возвращает JSON-ответ от сервера в виде словаря. 
                       В случае ошибки возвращает None.
    
    Raises:
        requests.exceptions.HTTPError: Если сервер возвращает ошибочный статус-код (4xx, 5xx).
        requests.exceptions.ConnectionError: Если возникает ошибка соединения.
        requests.exceptions.Timeout: Если запрос превышает время ожидания.
        requests.exceptions.RequestException: Для всех других ошибок, связанных с запросом.
    """
    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()  # Вызывает исключение для ответа с ошибкой (4xx или 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

# Рекомендации для холодных пользователей без онлайн активности
cold_user_params = {"user_id": 1234567890, 'k': 3}
print('***********************************************')
print(f"Cold user {cold_user_params['user_id']} recommendation:")
print(f"requests code: {cold_user_params}")
cold_recs = post_request(recommendation_service_url + "/recommendations_offline", headers, cold_user_params)
if cold_recs is None:
    cold_recs = []
print(f"recommendation: {cold_recs}")

# Рекомендации для холодных пользователей по последнему выбранному товару
last_item_params = {"item_id": "ind_reca_fin_ult1"}
print('***********************************************')
print(f"Cold user with item {last_item_params['item_id']} recommendation:")
print(f"requests code: {last_item_params}")
similar_items = post_request(recommendation_service_url + "/similar_items", headers, last_item_params)
if similar_items is None:
    similar_items = {}

print(f"recommendation: {similar_items.get('item_id_2', 'No similar items found')}")

# Рекомендации для пользователя с персональными рекомендациями, но без онлайн-истории
personal_user_params = {"user_id": 500729, 'k': 10}
print('***********************************************')
print(f"User {personal_user_params['user_id']} personal recommendation:")
print(f"requests code: {personal_user_params}")
personal_recs = post_request(recommendation_service_url + "/recommendations_offline", headers, personal_user_params)
if personal_recs is None:
    personal_recs = []
print(f"recommendation: {personal_recs}")

# Рекомендации для пользователя с персональными рекомендациями и онлайн-историей
print('***********************************************')
print(f"User {personal_user_params['user_id']} with online activity personal recommendation:")
user_id = 500729
event_item_ids = ["ind_recibo_ult1", "ind_valo_fin_ult1", "ind_reca_fin_ult1", "ind_plan_fin_ult1"]

# Формируем онлайн-историю
for event_item_id in event_item_ids:
    post_request(recommendation_service_url + "/put",
                 headers,
                 {"user_id": user_id, "item_id": event_item_id})

# Получаем рекомендации с учетом онлайн-истории
blended_recommendation_params = {"user_id": user_id, 'k': 3}
print(f"requests code: {blended_recommendation_params}")

blended_recs = post_request(recommendation_service_url + "/recommendations", headers, blended_recommendation_params)
if blended_recs is None:
    blended_recs = []

print(f"Blended recommendation: {blended_recs}")



