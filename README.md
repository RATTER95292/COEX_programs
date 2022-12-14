## Быстрая настройка для автономного полета
Далее будет выжимка из различных источников для произведения быстрой настройке для автономных полетов:

## Установка и подключение Raspberry Pi на квадрокоптере

Установить Raspberry, таким образом, чтобы все основные разъемы у raspberry были со стороны хвоста, а камеру крепить у носа.

<img src = "https://893838923-files.gitbook.io/~/files/v0/b/gitbook-legacy-files/o/assets%2F-MdqITQbWJUL8n4CbfRn%2F-MdqXBIBYKITI3e6xCyA%2F-MdqZbAqed5Dh4-lsgJn%2FrnrFliNjKto.jpg?alt=media&token=faa67e6d-e18e-4edb-91cb-936dee8dfc27" />

Подключить к Raspberry питание 5 V и сигнальный провод от светодиодной ленты.

<img src = "https://893838923-files.gitbook.io/~/files/v0/b/gitbook-legacy-files/o/assets%2F-MdqITQbWJUL8n4CbfRn%2F-MdqXBIBYKITI3e6xCyA%2F-MdqZkJ2NSWCEa2ChEA3%2FNCePNk-NsFk.jpg?alt=media&token=20d26fab-a417-418c-b596-98e61a3772f5" />

Подробная установка raspberry pi на квадрокоптер можно посмотреть по ссылке:

https://clover.coex.tech/ru/assemble_4_2_ws.html

## Образ для Raspberry Pi

Образ RPi для Клевера включает в себя все необходимое ПО для удобной работы с Клевером и <a href = "https://clover.coex.tech/ru/simple_offboard.html"> программирования автономных полетов </a>. Платформа Клевера основана на операционной системе Raspbian и популярном робототехническом фреймворке ROS. Исходный код сборщика образа и всех дополнительных пакетов доступен  <a href = "https://github.com/CopterExpress/clover"> на GitHub </a>.

### Использование

Начиная с версии v0.22, образ основан на ROS Noetic и использует Python 3. Если вы хотите использовать ROS Melodic и Python 2, используйте версию v0.21.2.

<ol>
<li> Скачайте последний стабильный релиз образа — <a href = "https://github.com/CopterExpress/clover/releases/download/v0.22/clover_v0.22.img.zip"> v0.22.</a> </li>
<li> Скачайте и установите <a href = "https://github.com/CopterExpress/clover/releases/download/v0.22/clover_v0.22.img.zip"> программу для записи образов Etcher </a> (доступна для Windows/Linux/macOS). </li>
<li> Установите MicroSD-карту в компьютер (используйте адаптер при необходимости). </li>
<li> Запишите скачанный образ на карту, используя Etcher. </li>
<li> Установите карту в Raspberry Pi. </li>
</ol>

<img src = "https://clover.coex.tech/assets/etcher.png"/>

После записи образа на SD-карту, вы можете подключаться к <a href = "https://clover.coex.tech/ru/wifi.html" >Клеверу по Wi-Fi </a>, использовать <a href ="https://clover.coex.tech/ru/gcs_bridge.html">беспроводное соединение в QGroundControl</a>, получать доступ по SSH и использовать остальные функции. При необходимости узнать версию записанного на карту образа используйте <a href = "https://clover.coex.tech/ru/selfcheck.html" > утилиту selfcheck.py</a>.


Инструкции по работе с квадракоптерам компании COEX:
1. https://lahmeneffa.gitbook.io/docs-tkuik/
2. https://clover.coex.tech/ru/
