# Объединение мультиполигонов

Сервис предоставляет возможность объединять мультиполигоны с помощью методов библиотеки shapely.
Для этого нужно выполнить запрос со следующими параметрами.

## Структура запроса

**http-method**: POST
**url**: 'http://127.0.0.1:5000/CombineMultiPolygons'

**Content-type** : application/json


### Формат тела запроса

{
  "wkts": \[...\],
  "options": {...}
}

**wkts** - список геометрий мультиполигонов
**options** - параметры объединения


#### Параметры объединения:

**hole_area** - минимальный размер отверстия, которое может возникнуть между внешнеми границами полигонов в результате их объединения


### Пример запроса:

    { 
		"wkts": \["Multipolygon(((1 1, 1 3, 3 3, 3 1, 1 1)))",
				 "MultiPolygon(((2 2, 2 4, 4 4, 4 2, 3 3, 2 2)))",
				 "MultiPolygon(((2 2, 3 1, 4 2, 4 0, 2 0, 2 2)))"\],
		"options": {hole_area = 2}
    }


## Ответ:

response=wkt, status_code=200

**wkt** - геометрия полученных мультиполигонов

### Пример ответа:

	("MultiPolygon(((4 0, 2 0, 2 1, 1 1, 1 3, 2 3, 2 4, 4 4, 4 2, 4 0)))", 200)


## Если что-то пошло не так:

response=ValueError, status_code=400 - невозможно получить мультиполигоны из геометрий
response=KeyError, status_code=400 - отсутствует ключ к компоненту тела запроса
status_code=500 - ошибка сервера







