# Хазиева Эльвира, 11-901
## Задание 2. Обработка фотографий с лицами людей

## Объекты:
### Бакеты
- itis-2022-2023-vvot20-photos
- itis-2022-2023-vvot20-faces
### БД
- vvot20-db-photo-face
### Очереди
- vvot20-tasks
### Триггеры
- vvot20-photo-trigger(сервисный аккаунт: run-face-detection-fun)
- vvot20-task-trigger(сервисный аккаунт: send-to-face-cut-container)
### Функции
- vvot20-face-detection(сервисный аккаунт: face-detection-fun, код: functions/PhotoFunction.py)
- boot-fun(сервисный аккаунт: boot-fun, код: functions/BootFunction.py)
### Контейнер
- vvot20-face-cut(сервисный аккаунт: vvot20-face-cut-container, код: container)  
### API-шлюз
- mr-gateway(сервисный аккаунт: vvot20-api-gateway)

## Cервисные аккаунты с их ролями:
**face-detection-fun**:  
- ai.vision.user
- ymq.writer
- storage.viewer  

**run-face-detection-fun**:
- serverless.function.invoker  

**vvot20-face-cut-container**:
- storage.viewer
- storage.uploader
- ydb.editor
- container-registry.images.puller  

**send-to-face-cut-container**:
- ymq.reader
- serverless.containers.invoker

**vvot20-api-gateway**:  
- storage.viewer  

**boot-fun**:
- ydb.viewer
- ydb.editor

