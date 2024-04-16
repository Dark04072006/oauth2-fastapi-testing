## Проект-пример тестирования Oauth2 по кукам в fastapi

### установка
``` bash
pip install -e .[lint,testing]
```

### запуск
``` bash
uvicorn app.main.web:create_app --factory
```

### запуск тестов
``` bash
pytest .
```
