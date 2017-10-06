## VK DONATION COVER

Для работы понадобится:

1. [Ключ доступа к сообществу ВКонтакте](https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0).
2. Аккаунт и [API ключ donatepay](http://donatepay.ru/page/api).
3. Платформа [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction).
3. ID группы ВКонтакте.
5. Подготовленная обложка, на которую будет выводится сообщение о донате.

Настройка:

Изменить токены ВК и donatepay

Все переменные доступны в файле config.py

Обложка хранится в images/original.png (можно изменить все в том же config.py)

Установка:
1. Создать в Heroku новое python приложение
2. В папке с проектом открыть консоль и выполняем действия, описанные в разделе Deploy using heroku git (открывается после п.1) до команды git push heroku master.
3. heroku config:set DISABLE_COLLECTSTATIC=1
4. выполняем git push heroku master
5. После запускаем heroku ps:scale web=1
6. Success
