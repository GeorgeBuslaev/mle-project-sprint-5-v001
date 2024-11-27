import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import logging as logger
import pandas as pd
import json

logger = logging.getLogger("uvicorn.error")

class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded")

    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []
        return recs

    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")

class EventStore:

    def __init__(self, max_events_per_user=10):
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, item_id):
        """
        Сохраняет событие
        """
        try:
            user_events = self.events[user_id]
        except:
            user_events = []
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        user_events = self.events[user_id][:k]

        return user_events
    
class SimilarItems:

    def __init__(self):
        self._similar_items = None

    def load(self, path, columns, **kwargs):
        """
        Загружаем данные из файла
        """

        logger.info(f"Loading data, type: {type}")
        self._similar_items = pd.read_parquet(path, **kwargs)
        self._similar_items = self._similar_items[columns]
        logger.info(f"Loaded")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items[self._similar_items['item_id_1']==item_id]
        
            i2i = i2i.loc[:, ("item_id_2", "score")].to_dict(orient='list')
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id_2": [], "score": {}}
        
        return i2i

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")

    # предзагрузим рекомендации
    rec_store.load(
        "personal",
        './data/recommendations_u.parquet',
        columns=["user_id", "item_id", "rank"]
        )
        
    # предзагрузим свмые популярные треки
    rec_store.load(
        "default",
        './data/top_recs.parquet',
        columns=["item_id", "rank"]
        )
    
    # предзагрузим данные о похожих треках
    sim_items_store.load(
        "./data/similar.parquet",
        columns=["item_id_1", "item_id_2", "score"]
        )
       
    yield
    # этот код выполнится только один раз при остановке сервиса
    rec_store.stats()
    logger.info("Stopping")

events_store = EventStore()

rec_store = Recommendations()

sim_items_store = SimilarItems()

# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

# инициализируем и запускаем экпортёр метрик
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """

    events_store.put(user_id, item_id)

    return {"result": "ok"}

@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """

    events = events_store.get(user_id, k)

    return {"events": events}

@app.post("/recommendations_offline/")
async def recommendations_offline(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
    recs = rec_store.get(user_id=user_id, k=k)

    return {"recs": recs}

@app.post("/similar_items")
async def recommendations(item_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """
    i2i = sim_items_store.get(item_id, k)

    return i2i

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    #resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = events_store.get(user_id, k)
    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        # для каждого item_id получаем список похожих в item_similar_items
        item_similar_items = sim_items_store.get(item_id, k)
        items += item_similar_items["item_id_2"]
        scores += item_similar_items["score"]
    # сортируем похожие объекты по scores в убывающем порядке
    # для старта это приемлемый подход
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]

    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)
    return {"recs": recs} 

@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]
    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_offline[i])
        recs_blended.append(recs_online[i])
    # добавляем оставшиеся элементы в конец
    if len(recs_offline) > min_length:
        recs_blended.extend(recs_offline[min_length:])
    elif len(recs_online) > min_length:
        recs_blended.extend(recs_online[min_length:])

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)
    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]
    return {"recs": recs_blended} 

