## VK DONATION COVER

Для работы понадобится:

1. [Ключ доступа к сообществу ВКонтакте](https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0).
2. Аккаунт и [API ключ donatepay](http://donatepay.ru/page/api).
3. Платформа [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction).
3. ID группы ВКонтакте.
5. Подготовленная обложка, куда будет выводится сообщение о донате.

Настройка ([config.py](./config.py)):

Все переменные доступны в файле config.py

Обложка хранится в images/original.png (можно изменить все в том же config.py)

Установка:
1. Склонировать проект
```
    git clone git@github.com:khoben/vk-donation-cover.git
```
2. Создать в Heroku CLI новое приложение
```
    heroku create {ваше название}
```
3. Добавить репозиторий Heroku
```
    heroku git:remote -a {ваше название}
```
4. Изменить токены и ид группы
```
    heroku config:set TOKEN_DONATIONPAY={XXX} TOKEN_VK={XXX} GROUP_ID={XXX}
```
{XXX} - соответсвующее значения

4. Загрузить проект на heroku.com
```
    git push heroku master
```
6. Запустить приложение и отключить веб интерфейс
```
    heroku ps:scale clock=1
    heroku ps:scale web=0
```

