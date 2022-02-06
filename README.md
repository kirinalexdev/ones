**Выполнение команд платформы 1С**  
Библиотека позволяет выполнять запуск 1С в одном из трех режимов:
- 1С:Предприятие
- Конфигуратор
- Создание информационной базы  

Реализовано в модуле ones.py

**Параметры запуска**  
Получение параметров запуска 1С автоматизировано через чтение ini-файлов   
Реализовано в модуле params.py

**Логирование**  
Есть удобное логирование, в том числе через декораторы.  
Реализовано в модуле logger_.py

**Тестирование**  
Модульные тесты реализованы под pytest, с небольшим использованием unittest.  
Реализовано в модулях:    
test_logger_.py  
test_ones.py  
test_params.py

Интеграционные тесты выполнялись на платформе 1С версии 8.3.10.2753.

**Примеры**  
Приложено три примера создания информационной базы.  
Примеры сделаны по нарастанию сложности и возможностей.

Реализовано в модулях:  
example1.py  
example2.py  
example3.py
