# Обработка геометрии мультиполигонов

Сервис предоставляет возможность производить следующую обработку геометрий мультиполигонов:
  * объединение мультиполигонов
  * упрощение геометрии мультиполигонов
    * уменьшение количества вершин
    * уменьшение количества полигонов

Используется библиотека shapely 1.8.2

Доступ к обработке мультиполигонов предоставляется с помощью http-запросов.

---

## Объединение мультиполигонов

Возвращает мультиполигон, представляющий из себя объединение исходных мультиполигонов.


### Структура запроса

**http-method**: POST  
**url**: 'http://127.0.0.1:5000/CombineMultiPolygons'  

**Content-type** : application/json  


#### Формат тела запроса

{
  "wkts": \[...\],  
  "options": {...}
}

**wkts** - список геометрий мультиполигонов  
**options** - параметры объединения  


##### Параметры объединения:

**hole_area** - минимальный размер отверстия, которое может возникнуть между внешними границами полигонов в результате их объединения


#### Пример запроса:

    { 
		"wkts": ["Multipolygon(((1 1, 1 3, 3 3, 3 1, 1 1)))",
				 "MultiPolygon(((2 2, 2 4, 4 4, 4 2, 3 3, 2 2)))",
				 "MultiPolygon(((2 2, 3 1, 4 2, 4 0, 2 0, 2 2)))"],
		"options": {hole_area = 2}
    }

---

## Уменьшение количества вершин

Возвращает мультиполигон с количеством вершин, меньших заданного.

*На основе заданного количества вершин и параметров мультиполигона вычисляется значение радуиса для построения буфера и его дальнейшего упрощения. Буффер с уменьшенным числом вершин возвращается как результат обработки геометрии.*

### Структура запроса

**http-method**: POST  
**url**: 'http://127.0.0.1:5000/SimplifyWithBuffer'  

**Content-type** : application/json  


#### Формат тела запроса

{
  "wkt": "...",
  "vertexes": m
}

**wkt** - геометрия мультиполигона 
**vertexes** - предельное количество вершин


#### Пример запроса:

    { 
        "wkts": "",
        "vertexes": 10
    }


### Ответ:

response=wkt, status_code=200

**wkt** - геометрия полученного мультиполигона


#### Пример ответа:

	{"simplified_wkt":  Polygon((0.0000000000000003 -4.502391698009549, -5.796230004744379 -0.1769132139195197, -1.1769132139195198 4.796230004744379, 4.796230004744379 1.1769132139195198, 4.395222950169494 -2.1450298836814956, 0.0000000000000003 -4.502391698009549))}  

---

## Уменьшение количества полигонов

Возвращает мультиполигон, который покрывает исходный мультиполигон.  
Количество полигонов в полученном мультиполигоне равно заданному значению, которое меньше количества вершин в исходном мультиполигоне.  
Количество вершин в исходном и полученном полигонах совпадает.

*Количество полигонов уменьшается путем объединения исходных полигонов с добавленными четырехугольниками. Две противоположных стороны каждого добавленного четырехугольника являются сторонами исходных полигонов. Четырехугольники лежат вне исходной геометрии.*

### Структура запроса

**http-method**: POST  
**url**: 'http://127.0.0.1:5000/BuildBridges'  

**Content-type** : application/json  


#### Формат тела запроса

{
  "wkt": "...",
  "polygons": m
}

**wkt** - геометрия мультиполигона 
**polygons** - нужное количество полигонов  


#### Пример запроса:

    { 
        "wkt": ""MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)))"",
        "polygons": 2
    }


### Ответ:

response=wkt, status_code=200

**wkt** - геометрия полученного полигона


#### Пример ответа:

	{"bridged_wkt": "Polygon((0 1, 0 2, 0 3, 1 3, 1 0, 0 0, 0 1))"}  

---

## Если что-то пошло не так:

response=ValueError, status=400 - невозможно выполнить обработку геометрии по исходным данным
response=KeyError, status=400 - отсутствует ключ к компоненту тела запроса  
status_code=500 - ошибка сервера
