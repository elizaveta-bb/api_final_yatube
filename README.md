
# API для социальной сети Yatube

REST API для блоговой платформы Yatube, позволяющее:
-   Создавать посты, комментарии
-   Подписываться на авторов
-   Получать данные через GET-запросы
-   Аутентифицироваться через JWT-токены
   
[GitHub](https://github.com/elizaveta-bb/api_final_yatube)
# УСТАНОВКА
1.  Клонируйте репозиторий:  
	```bash
	git clone https://github.com/elizaveta-bb/api_final_yatube.git
	cd api_final_yatube
	```
2.  Создайте виртуальное окружение:  
	```bash
	python -m venv venv  
	source venv/bin/activate #(Linux/macOS)  
	venv\Scripts\activate #(Windows)
	```
3.  Установите зависимости:
	```bash
	pip install -r requirements.txt
	```
4.  Примените миграции:  
	```bash
	python manage.py migrate
	```
5.  Запустите сервер:  
	```bash
	python manage.py runserver
	```
