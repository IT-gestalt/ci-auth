# Кибериммунный подход к разработке (проект Python-only)

В рамках изучения кибериммунного подхода к разработке программного обеспечения ([GitHub-репозиторий "Кибериммунитет"](https://github.com/sergey-sobolev/cyberimmune-systems/wiki/Кибериммунитет)) в качестве одного из упражнений на закрепление знаний, приобретённых на курсе ["Обучение кибериммунной разработке"](https://t.me/learning_cyberimmunity), аудитории предложена доработка [примера](https://datalore.jetbrains.com/notebook/03eLGJdIpU4hXmR1ojbvzD/colMMBzGG25Q6NHzjdXluU/) получения данных одной сущностью от другой.

## Введение

Код исходного [варианта]((https://datalore.jetbrains.com/notebook/03eLGJdIpU4hXmR1ojbvzD/colMMBzGG25Q6NHzjdXluU/)) на языке программирования Python незначительно переработан в связи с необходимостью внесения конструктивных особенностей авторской реализации. Вместе с тем предложенное решение не противоречит описанию изначальной задачи и постулатам кибериммунной методологии.

## Подход к реализации сущностей

Сущности реализованы с использованием класса `manager.BaseManager` модуля `multiprocessing` и представляют собой совокупность из Сервиса, содержащего очередь событий, и Клиента, обрабатывающего данные события. Внутрисистемное взаимодействие Клиента и Сервиса инкапсулировано в соответствующих авторских классах. 

Схематично:

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
skinparam componentStyle rectangle

package Entity{

  frame [\nClient] #BDE0FF {
      port " " as c_out #FFFFFF
      port " " as c_in #000000
  }

  frame [\nService] #DCDCDC {

    component "Queue" as queue #FFFFFF {
      port " " as queue_in #FFFFFF
      port " " as queue_out #000000
    } 
    port " " as s_in #FFFFFF
    port " " as s_out #000000
  }


  s_out --> c_in : get_event()
  c_out ---> s_in :  put_event()
  s_in --> queue_in #black;line.dashed; : put()
  queue_out ---> s_out #black;line.dashed;  : get()
}
@enduml
```

</details>

![](https://www.plantuml.com/plantuml/svg/TL4zQyCm4DtrAuvuQOUKp0sKq2JUIyQs15M-kYAox5gdG0Z-xptf1jV1EO4nUX_l7Te4qZt5ngbmihxJlMx0j4tNUlHqe8j3wD6GzhL3fJfjJhf6s7koTBag1V3D2eJt3xzrbYMVKBpkzgkoXAk2F5tR4opuw03cs4Q2eimpYriFnIeFmyCau83zsHhaXDqs7SZvCDQ5nLl4YDdfD_r9qdmNOUGy8TsbSEMn4yy0wfOORdscuDI1j-Alt2wNBxBqCzH8HpoZfuT7Xet02G-2GnV_4UGsmUCUNuwVP-sinwTAXn-irYnZLU8BRJIL-3c9L67De3RegzYuFm00)


Программно архитектура основана на классах Сервиса, Клиента и их базовом Супер-классе (с целью повышения фокуса внимания читателя здесь и далее из демонстрируемого исходного кода исключены конструкции, "лишние" для изложения и понимания).

Супер-класс сущности:

```python
from multiprocessing.managers import (
    BaseManager,
)


class SuperManager:
    dispatcher = None

    def __init__(self, host, port, authkey):
        self.dispatcher = BaseManager(address=(host, port), authkey=authkey)

    def register(self, *args, **kwargs):
        self.dispatcher.register(*args, **kwargs)
```

Объект класса Сервиса сущности стартует на определённых хосте и порту с доступом по парольной фразе. Его интерфейс состоит из методов `get_event` (транслируется в метод очереди `get` - *получить элемент из очереди*) и `put_event` (транслируется в метод очереди `put` - *положить элемент в очередь*):

```python
from multiprocessing import Queue
from queue import Empty

TIMEOUT = 30


class Service(SuperManager):
    event_loop = Queue()

    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('put_event', callable=self.put_event)
        self.register('get_event', callable=self.get_event)

    def get_event(self, *args, **kwargs):
        try:
            return self.event_loop.get(*args, block=False, timeout=TIMEOUT, **kwargs)
        except Empty:
            return None

    def put_event(self, event, *args, **kwargs):
        self.event_loop.put(event, *args, timeout=TIMEOUT, **kwargs)

    def serve_forever(self):
        self.dispatcher.get_server().serve_forever()

```

Объект класса Клиента сущности подключается к Сервису сущности, реализуя алгоритм обработки очереди событий:

```python
class Client(SuperManager):
    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('put_event', self.put_event)
        self.register('get_event', self.get_event)

    def get_event(self, *args, **kwargs):
        return self.dispatcher.get_event(*args, **kwargs)._getvalue()

    def put_event(self, event, *args, **kwargs):
        self.dispatcher.put_event(event, *args, **kwargs)

    def connect(self, *args, **kwargs):
        self.dispatcher.connect()
        return self

```

### Пример использования

Так, реализованный пример тестового Сервиса:

```python
Service('localhost', 9000, b'AUTH_KEY').serve_forever()
```

предоставляет Клиенту возможность забирать и отправлять произвольные данные в очередь Сервиса:

```python
client_1 = Client('localhost', 9000, b'AUTH_KEY')
client_1.connect()
client_1.put_event(
    dict(datetime=datetime.datetime.now().isoformat())
)

client_2 = Client('localhost', 9000, b'AUTH_KEY').connect()
client_2.put_event(
    dict(datetime=datetime.datetime.now().isoformat())
)

event = Client('localhost', 9000, b'AUTH_KEY').connect().get_event()
)
```


| __Журнал работы Сервиса__                                                            | __Журнал работы Клиента__                                                        | 
|--------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| __$ python3 ./tests/example_000_1_service.py__                                       |                                                                                  |
| [Service] will be work with localhost:9000                                           |                                                                                  |
| [Service] start listening.                                                           |                                                                                  |
|                                                                                      | __$ python3 ./tests/example_000_2_client.py__                                    |
|                                                                                      | --- client_1 ---                                                                 |
|                                                                                      | [Client] will be work with localhost:9000.                                       |
|                                                                                      | [Client] connect.                                                                |
|                                                                                      | [Client] put event {'datetime': '2023-01-18T02:36:05.730509'}.                   |
| [Service] event was put to queue: {'datetime': <br/>'2023-01-18T02:36:05.730509'}.   |                                                                                  | 
| [Service] events count become: 1.                                                    |                                                                                  |
|                                                                                      | --- client_2 ---                                                                 |
|                                                                                      | [Client] will be work with localhost:9000.                                       |
|                                                                                      | [Client] connect.                                                                |
|                                                                                      | [Client] put event {'datetime': '2023-01-18T02:36:05.961736'}.                   |
| [Service] event was put to queue: {'datetime': <br/>'2023-01-18T02:36:05.961736'}.   |                                                                                  |
| [Service] events count become: 2                                                     |                                                                                  |
|                                                                                      | --- no name client ---                                                           |
|                                                                                      | [Client] will be work with localhost:9000.                                       |
|                                                                                      | [Client] connect.                                                                |
|                                                                                      | [Client] send request for event get from service.                                |
|                                                                                      | [Client] get event {'datetime': '2023-01-18T02:36:05.730509'} <br/>from service. |
| [Service] event was get from queue: {'datetime': <br/>'2023-01-18T02:36:05.730509'}. |                                                                                  |
| [Service] events count become: 1                                                     |                                                                                  |

> *Замечание*: Сервис-сущности представлен в единственном числе, тогда как количество Клиентов-сущности, реализующих обработку очереди событий, не ограничено. Данное обстоятельство можно расценивать как направленное на повышение скорости обработоки очереди событий за счет параллельного доступа нескольких Клиентов к одному Сервису.

### Взаимодействие сущностей

Взаимодействие сущностей в общем виде представляется как процесс, управляющий набором Клиентов, взаимодействующих с соотвествующими им Сервисами:

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
skinparam componentStyle rectangle

node Entity\No.1 as "Complex Logic\nEntity"{

  frame Entity_No_1_Client as "\nClient of\nEntity No.1" #BDE0FF {
      port " " as n1_c_out #FFFFFF
      port " " as n1_c_in #000000
  }
  frame Entity_No_2_Client as "\nClient of\nEntity No.2" #BDE0FF {
      port " " as n2_c_out #FFFFFF
      port " " as n2_c_in #000000
  }

  component Logic as "job\nmanagement"

}
frame [Entity\No.1\Service]  as "Service of\nEntity No.1" #DCDCDC {

  component "Queue" as n1_queue #FFFFFF {
    port " " as n1_queue_in #FFFFFF
    port " " as n1_queue_out #000000
  } 
  port " " as n1_s_in #FFFFFF
  port " " as n1_s_out #000000
  n1_queue_out -> n1_s_out #black;line.dashed;  : get()
  n1_s_in -> n1_queue_in #black;line.dashed;  : put()
}

frame [Entity\No.2\Service]  as "Service of\nEntity No.2" #DCDCDC {

  component "Queue" as n2_queue #FFFFFF {
    port " " as n2_queue_in #FFFFFF
    port " " as n2_queue_out #000000
  } 
  port " " as n2_s_in #FFFFFF
  port " " as n2_s_out #000000
  n2_queue_out -> n2_s_out #black;line.dashed;  : get()
  n2_s_in -> n2_queue_in #black;line.dashed;  : put()
}


n1_s_out --> n1_c_in : get_event()
n1_c_out --> n1_s_in :  put_event()
n2_s_out --> n2_c_in : get_event()
n2_c_out --> n2_s_in :  put_event()
Entity_No_2_Client <-- Logic 
Entity_No_1_Client <-- Logic 

@enduml
```

</details>

![](https://www.plantuml.com/plantuml/svg/ZPHFhvim4CJl-obMvD8UU7hiiQ-gekRFgOfKvLWgvC26qXYRWeaQHVdkDH0Qfv06St9sPXZ_8WFpoeZIrBc4wf2fGfGYnrZdXLQipDQS96F9iH4gbGoWTCAuKYOpft2ZNm8K5NeBAvVy6x_eD8j3rOszCm3YtiRrXcYZeo1QoCm6jxvGNJTwtxkm2VLmzdcvUbslyGpOhaAN1ZtxM9iAeZZIjS7PkbsF99d2sMkxhE8oqeKcTA4dNUXv5nfs0RmXxgYr7NxgNQXoeKJAkPru01VeIdzpa8TRBezPpD-nDLrt8moNY-R1y_thlAyrrznZ-jLi-lPMwhPt9VO4lUgnne9mZuamq5Lkpd1wdt0Vx7zo93ifuiERp1I_9ABwmSaRuWTCsRnx3zY_gBCu_STTHTsuBZ14JPDGqoJKz1mrJK1D4r7JVr7J43NzWvecegORQfgE6lx-bRvrzjUrZOtuoAgHDR-waggJs117GsuCZSQG6qEZCIFVX8--VxsPpZGOcSASLLBdyWy0)

> *Замечание по Python-реализации*: В целях недопущения возможных вариаций компановки предлагаемого исходного кода в реализуемые в будущем алгоритмические модели необходимо сделать важное замечание. Допустим, имеется соединение Клиента-X к Cервису-X. В случае реализации __непосредсвенно__ в Сервисе-X __клиентского__ соединения к Сервису-Y, например, Сервис-X по вызову из-вне динамически создает Клиента-Y для Сервиса-Y, Клиент-X безвозвратно теряет связь с Сервисом-X и начинеат "прозрачное" взаимодействие с Сервисом-Y, к которому изначально доступа не имел. Это весьма нетривиальное поведение выявлено на практике и требует перепроверки на свежих версиях Python. Данное обстоятельство\особенность\ограничение необходимо учитывать при организации вариантов динамического взаимодействия сущностей. Рассматриваемую модель это не затрагивает, так как необходимые Клиенты динамически создаются иными Клиентами.

> *Замечание*: следующий пример предлагается рассмотреть самостоятельно:
> * example_001_0_app_config.py
> * example_001_1_service.py
> * example_001_2_client_put.py
> * example_001_3_client_get.py
> * example_001_4_client_event_loop.py

## Практическое применение и артефакты киберимунного подхода

С целью ориентации упражнения на практическую область в качестве наглядного примера выбран алгоритм аутентификации пользователя в информационной системе.

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
left to right direction
skinparam actorStyle awesome
database "Worker B" as wb
actor "Worker A" as wa
skinparam componentStyle rectangle

[Manager] --> wa
wb -> [Manager]
wa -> [Manager]
[Manager] --> wb
@enduml
```

</details>

![](http://www.plantuml.com/plantuml/png/NOyzhi9038Hxdy9AdoiyvT5JKL0WYjd4X5Ns9_8QhRWz2P4YeBC_UJvhkc9GUyH0GMx6bbdzU3SUl4flFYSgaqyp597HMzQJFOCmgfGSXGOO78fmSyuwYVAXOHIkZjx7E_xVC3viVOvpJf9iCwxlaCOWH9SZ4aRHAxVjtnggZfTXnrJnlVy477MIXgNJ2m00)

Разработанный вариант функционирует с задействованием механизмов штатных модулей Python, не требуя дополнительной инфраструктуры, как то: веб-фреймворки, базы данных, контейнеризация, - "порог вхождения" не должен казаться высоким. Реализованный проект может выступать в качестве шаблона для моделирования аудиторией курса ["Обучение кибериммунной разработке"](https://t.me/learning_cyberimmunity) алгоритмических приёмов в иных сферах автоматизации. 

> *Замечание*: Приведённый вариант решения носит учебный характер. Обеспечение защиты взаимодействия сущностей данной модели от угроз "атак по-середине" выходит за рамки текущей стадии реализации.

> *Замечание*: В рамках миникурса рассматривался способ решения, приближенный к продуктовому инфраструктурному комплексу - https://github.com/sergey-sobolev/secure-update

### Домены модели на физическом уровне

Сущности модели информационной системы:
* `Пользователь` - взаимодействует с `Аутентификатором`, связанным `Базой данных` (в отдельную сущность не выделена);
* `Аутентификатор` - аутентифицирует `Пользователя` для доступа к `Базе данных`;
* `Менеджер` - промежуточное звено, отвечающее исключительно за проверку политики безопасности взаимодействия `Пользователя` и `Аутентификатора`;

### Активы

* данные `Базы данных`;

### Угрозы безопасности

* предоставление данных из `Базы данных` неаутентифицированному `Пользователю`;

### Цель безопасности

* данные из `Базы данных` предоставляются только аутентифицированному `Пользователю`;

### Предположения безопасности

* если коротко - `Пользователь` - не доверенная сторона;

### Реализация События и политики безопасности

Вышеприведенная очередь Сервиса не ограничена типом хранящихся элементов. Это могут быть как словари `dict`, так и  объекты разнородных произвольных классов.

Формализуем класс Событие исходного [примера](https://datalore.jetbrains.com/notebook/03eLGJdIpU4hXmR1ojbvzD/colMMBzGG25Q6NHzjdXluU/) с некоторым дополнительным расширением:
* поле параметров (`parameters`) - имеет словарный тип (`dict`), что добавит гибкости в передаче произвольного их набора;
* операция сравнения Событий (`__eq__`) - синтаксически упростит код проверки политики безопасности и выбора Клиентом реакции на событие.

```python
from dataclasses import dataclass, field

def empty_dict():
    return dict()

@dataclass
class Event:
    source: str  # инициатор запроса
    destination: str  # получатель запроса
    operation: str  # запрашиваемое действие
    parameters: dict = field(default_factory=empty_dict)  # параметры запрашиваемого действия
    def __eq__(self, other):
        if self.source == other.source and \
                self.destination == other.destination and \
                self.operation == other.operation:
            return True
        return False
    def get_source(self):
        return self.source
```

Таким образом политика безопасности имеет вид множества допустимых Событий:

```python
SECURITY_POLICY = Event(source="user", destination="authenticator", operation="authenticate"), \
                  Event(source="authenticator", destination="user", operation="authenticate_response"), \
                  Event(source="user", destination="authenticator", operation="check_session_token"), \
                  Event(source="authenticator", destination="user", operation="check_session_token_response"), \
                  Event(source="user", destination="authenticator", operation="get_data_from_database"), \
                  Event(source="authenticator", destination="user", operation="get_data_from_database_response")
```

А проверка События на допустимость - функцией сравнения:

```python
def check_by_policy(event):
    if event in SECURITY_POLICY:
        return True
    return False

```

### Реализация сущностей

На схеме взаимодействия сущностей стрелками указано направление прохождения События по циклу его обрабоки (маркером `NEW` указан факт возникновения нового События в результате обработки предыдущего События):

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
skinparam componentStyle rectangle

frame [ManagerService]  as "Manager\nService" #DCDCDC {
  component "Queue" as m_queue #FFFFFF {
    port " " as m_queue_in #FFFFFF
    port " " as m_queue_out #000000
  } 
  port " " as m_s_in #FFFFFF
  port " " as m_s_out #000000
  m_queue_out -> m_s_out #black;line.dashed; : get()
  m_s_in -> m_queue_in #black;line.dashed; : put()
}
frame [AuthenticatorService]  as "Authenticator\nService" #DCDCDC {
  component "Queue" as a_queue #FFFFFF {
    port " " as a_queue_in #FFFFFF
    port " " as a_queue_out #000000
  } 
  port " " as a_s_in #FFFFFF
  port " " as a_s_out #000000
  a_queue_out -> a_s_out #black;line.dashed; : get()
  a_s_in -> a_queue_in #black;line.dashed; : put()
}
node AuthenticatorComplexClient as "Authenticator Client Side\nComplex Logic"{
  frame Authenticator_Client as "Authenticator\nClient" #BDE0FF {
    port " " as a_c_out #FFFFFF
    port " " as a_c_in #000000
  }
  frame Dynamic_Manager_Client as "Dynamic\nManager\nClient" #BDE0FF {
    port " " as dm1_c_out #FFFFFF
    port " " as dm1_c_in #000000
  }
  component AuthenticatorLogic  as "process event"
  AuthenticatorLogic --> dm1_c_out : "process call\nput_event( NEW )"
  AuthenticatorLogic <-- a_c_in :"process call\nget_event()"
}
frame [UserService]  as "User\nService" #DCDCDC {
  component "Queue" as u_queue #FFFFFF {
    port " " as u_queue_in #FFFFFF
    port " " as u_queue_out #000000
  } 
  port " " as u_s_in #FFFFFF
  port " " as u_s_out #000000
  u_queue_out -> u_s_out #black;line.dashed; : get()
  u_s_in -> u_queue_in #black;line.dashed; : put()
}
node UserComplexClient as "User Client Side\nComplex Logic"{
  component UserLogic  as "process event"
  frame Dynamic_Manager_Client2 as "Dynamic\nManager\nClient" #BDE0FF {
    port " " as dm2_c_out #FFFFFF
    port " " as dm2_c_in #000000
  }
  frame User_Client as "User\nClient" #BDE0FF {
    port " " as u_c_out #FFFFFF
    port " " as u_c_in #000000
  }
  UserLogic --> dm2_c_out : "process call\nput_event( NEW )"
  UserLogic <-- u_c_in : "process call\nget_event()"
}
node ManagerClient as "Manager Client Complex Logic"{
  frame Dynamic_User_Client as "Dynamic\nUser\nClient" #BDE0FF {
    port " " as du_c_out #FFFFFF
    port " " as du_c_in #000000
  }
  frame Manager_Client as "Manager\nClient" #BDE0FF {
    port " " as m_c_out #FFFFFF
    port " " as m_c_in #000000
  }
  frame Dynamic_Authenticator_Client as "Dynamic\nAuthenticator\nClient" #BDE0FF {
    port " " as da_c_out #FFFFFF
    port " " as da_c_in #000000
  }

  component Logic as "delegate event"

  Logic <--- m_c_out: get_event()
  du_c_out <-- Logic : "process call\nput_event()"
  da_c_out <-- Logic : "process call\nput_event()"

  da_c_out -> a_s_in : put_event()
  du_c_out -> u_s_in : put_event()
  dm1_c_out --> m_s_in : put_event()
  dm2_c_out --> m_s_in : put_event()

  a_s_out --> a_c_in : get_event()
  u_s_out --> u_c_in : get_event()
  m_s_out ---> m_c_in : get_event()

}
@enduml
```

</details>

![](http://www.plantuml.com/plantuml/png/fPPHRvim4CVV-HIdvALzoDJbCPscRadtj4sQecaFouHkSAEeO1XmrQgfttt6CWOS78EMlbJs_yxdtzqVkAiRh1hEiw1-J4M95UOG5NbP21BDiNdE22gA6XH9Ha7mIsuJVF-40XEgZbGzfH7z0C0QLdhn9FJo2jQ7VVi7VmFeSyBg2nFJget9mz_j_x3-e7vA250MbLJ1K16ceXCv9GKtiBvHFwbvWS2MrUCirgOLFyowUTiBVcOOFTvcgQ1NCTOF5D_23X9ghgu3q6SelQdR4L9o6_BI4Nt7pOE4aqRO51RNuTOYkkYbYtwwE8ykNgABPtHnJ1TdqKL35-VI5KLCC0AubwGo-hFFKhbqpXVqnZ6DwIIq63uMIHgjMdwgNUECeIkNZ5SxibNl3_StZWv4wkPk_96wPK_U575u5fYdKQXzDon3Rvs4tfjJIPo_zjIY5EVLcDaROr7CG9LJLaL4TGtqrDOGm9Hm8zlQbx3hWoBCifEG3GrL-1Lylly6ruuiRpQR3jdEof1Gbq466zzzhUt7c5nPv3BskepzBkDvBkDBBkCpb_7OPJpBPMnSnejS9hbDc4kkUZtLOvLgzznu1d_x7vE_zKx-rkb3LNHeNNdEiUmvbAUEr8ICORPB3AE2ZKzO-mGk6qKrLzCSt5AjzBsrkshtoePa-ZINLkp35RExHHEFo0NpaNjEpltFQESBmt1O_EQ8qGS4p-iQkKtrIbKHKqO9DjGvJShCd6ow--zWC1a1z1sH8Ys_C8Lg06DS669Y-ky4DR8bMvKO2KzBpAj5-IPtYRO-aVuCwJGQiOs61nAUbkH6eewQq0IoNNSaOiwpVm00)

#### Менеджер

Сервис Менеджера проверяет транслируемые ему в очередь Cобытия на допустимость в соответствии с политикой безопасности. 

```python
class ManagerService(Service):

    def put_event(self, event, *args, **kwargs):
        if manager_policy.check_by_policy(event):
            super().put_event(event, *args, **kwargs)
```

> *Замечание*: проверочный блок возможно перенести и на сторону Клиента Менеджера. Это приведет к отсутсвию необходимости описания класса Сервиса Менеджера в принципе, например,
>
> ```python
> class ManagerService(Service):  # Cинтаксический сахар. Больше ничего не нужно.
>    ...
>
> ```
>
> Однако первый вариан логичнее, так как эффективнее принудительно не допускать попадание от Клиентов недопустимых Событий в очередь Сервиса, чем отслеживать данное обстоятельство по факту их обработки.

Клиент Менеджера забирает события из очереди и ретранслирует их потребителям в соответствии с условной "сигнатурой" (`event.destination`):

```python
class ManagerClient(Client):

    def process_event_loop(self):
        while True:
          
            event = self.get_event()
           
            connection_config = ENTITIES_SERVICES.get(event.destination)
            destination_service = Client(connection_config.get(HOST),
                                         connection_config.get(PORT),
                                         connection_config.get(SECRET_KEY)).connect()
            destination_service.put_event(event)
       
```

#### Аутентификатор

Сервис Аутентификатора не реализует дополнительных функций:

```python
class AuthenticatorService(Service):  # Cинтаксический сахар. 
    ...
```

Клиент Аутентификатора в зависимости от сигнатуры очередного события из очереди Сервиса Аутентификатора:
* аутентифицирует логин-парольную пару, фиксируя сессионный ключ в Базе Данных;
* проверяет сессионный ключ на валидность - аутентифицирован ли Пользователь с таким ключом или нет;
* предоставляет для аутентифицированного Пользователя сведения из Базы Данных;


```python
class AuthenticatorClient(Client):

    def process_event_loop(self):
        while True:

            event = self.get_event()

            operation = event.operation
            if operation == "authenticate":
                login = event.parameters.get("login", "")
                password = event.parameters.get("password", "")
                if login and password:
                    AuthenticatorClient.authenticate(login, password)

            elif operation == "check_session_token":
                session_token = event.parameters.get("session_token", "")
                AuthenticatorClient.check_session_token(session_token)

            elif operation == "get_data_from_database":
                session_token = event.parameters.get("session_token", "")
                AuthenticatorClient.get_data_from_database(session_token)

    @staticmethod
    def authenticate(login, password):
        # отправит пользователю:
        # - в случае успеха по логин-парольной паре присвоенный аккаунту идентификатор сессии
        # - в случае ошибки - ошибку доступа
        session_token = Database.authenticate(login, password)
        # ... см. реализацию в коде

    @staticmethod
    def check_session_token(session_token):
        # отправит Пользователю подтверждение валидности сессионного ключа
        if not Database.is_account_authenticate(session_token):  
        # ... см. реализацию в коде

    @staticmethod
    def get_data_from_database(session_token):
        # отправит аутентифицированному Пользователю данные из базы данных
        # - в случае ошибки - ошибку доступа
        if Database.is_account_authenticate(session_token):
            data=Database.get_data_from_database()
        # ... см. реализацию в коде
```

База Данных не выносилась в отдельную сущность и в примере жёстко связана с Сервисом Аутентификатора. Но применяемый шаблон взаимодействия не препятствует отделению интерфейса работы Аутентификатора с хранилищем информации в отдельную составляющую проекта.

```python
class Database:

    accounts = dict()  # (login, password) = session_token
    accounts[("user", "user")] = None
    accounts[("admin", "admin")] = None
    accounts[("root", "root")] = None

    data = list() 
    data.append(dict(value="One"))
    data.append(dict(value="Two", message=":)"))
    data.append(dict(value="Three"))

    @classmethod
    def _is_account_exists(cls, login, password):
        if (login, password) in Database.accounts:
            return True
        return False

    @classmethod
    def authenticate(cls, login, password):
        if Database._is_account_exists(login, password):
            session_token = str(uuid.uuid4())
            Database.accounts[(login, password)] = session_token
            return session_token
        return None

    @classmethod
    def is_account_authenticate(cls, session_token):
        if session_token is not None and session_token in Database.accounts.values():
            return True
        return False

    @classmethod
    def get_data_from_database(cls):
        return Database.data
    
```

#### Пользователь

Сервис Пользователя не реализует дополнительных функций:

```python
class UserService(Service):  # Cинтаксический сахар. 
    ...
```

Клиент Пользователя реализует:
* запрос аутентификации по логин-парольной паре;
* запрос проверки сессионного ключа на валидность;
* запрос данных из хранилища;

```python
class UserClient(Client):
    session_token = None

    @staticmethod
    def authenticate(login, password):
        ManagerClient(manager_app_config.HOST,
                      manager_app_config.PORT,
                      manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            Event(
                source="user",
                destination="authenticator",
                operation="authenticate",
                parameters=dict(
                    login=login,
                    password=password
                )
            )
        )

    def wait_for_authenticate(self):        
        # ... см. реализацию в коде

    def check_session_token(self):
        ManagerClient(manager_app_config.HOST,
                      manager_app_config.PORT,
                      manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            Event(
                source="user",
                destination="authenticator",
                operation="check_session_token",
                parameters=dict(
                    session_token=self.session_token
                )
            )
        )

    def wait_for_check_session_token(self):       
        # ... см. реализацию в коде

    def get_data_from_database(self):  
        # ... см. реализацию в коде

    def wait_for_get_data_from_database(self):  
        # ... см. реализацию в коде
```

> *Замечание*: необходимо повториться, приведённый вариант решения носит учебный характер. Многопользовательский доступ с использованием данной реализации не рассматривается. Для организации безопасной работы нескольких пользовательских Клиентов целесообразно рассмотреть разделение очередей Событий Пользователей в едином Сервисе Пользователя или же введение сущности реестра Сервисов Пользователей, работающих отдельно для каждого своего Клиента Пользователя. 

### Пример запуска инфраструктуры

Откройте 5 терминалов и по очереди в каждом запустите:
1. `python3 ./manager_service.py`
2. `python3 ./authenticator_service.py`
3. `python3 ./user_service.py`
4. `python3 ./manager_client.py`
5. `python3 ./authenticator_client.py`

#### Пример Клиента Пользователя
  
В шестом терминале запустите Клиента Пользователя:

6. `python3 ./user_client.py`

На демонстрационных запросах Клиента Пользователя остановимся подробнее.

```python
user = UserClient(config.HOST,
                      config.PORT,
                      config.SECRET_KEY).connect()
```

Журнал работы:

```text
2023-01-18 01:52:49,646 INFO     [UserClient] will be work with localhost:5002.
2023-01-18 01:52:49,689 INFO     [UserClient] connect.
```

##### Аутентификация

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
actor       Пользователь                         as User
participant "Менеджер\n(монитор безопасности)"   as Manager
database    "Аутентификатор\n(и база данных)"    as Database

User     -> Manager  : Запрос аутентификации:\nлогин и пароль
Manager  -> Manager  : Проверка политики\nбезопасности
Manager  -> Database : Запрос аутентификации:\nлогин и пароль
Database -> Database : Поиск аккаунта,\nвыделение сессионного ключа
Database -> Manager  : Ответ:\nсессионный ключ
Manager  -> Manager  : Проверка политики\nбезопасности
Manager  -> User     : Ответ:\nсессионный ключ
@enduml
```

</details>

![](http://www.plantuml.com/plantuml/png/jPCzJiDG48HxdsAL2YIuG0gKWfQIBiqZYL0aC55iUYVyK0GXEXf4hc02XeU3dIlCteXP6InaaG89DagUddRtcyd83ZfHxCRnwV5Hu7hnoLYgmXmbbdgDLvuBf3f5PdTPLowI_MWm3aQ43Nl3aGjZQU6UMmM_ptX1faattC0xWGKyWQKcWaTsJMD5ZGaRfKxOyfkjYhddGdT8RD_5xi150s6rSAjd72BQHlKS7ZdNIQmal65JObEXSeg2WpEz8BE2xdx2Wi0iYzNspfUKI5jmnwsL9kP6IFv9xPAdRtT3B57YYPT2J7Z5Lb9b5zJ41drk4qoLYHZAbhW0oyJOdj0riNn7rd_ZxmpNn0PzphwdZvniid9JWD7JBV8MEcFC6RcK93SJZcOwuQ_dOi6F2PQ2d2etUeMqLcf6yq2e1JEbqIQ5Ccyrux_3hP-CNvdg3C8-NwKF)

> *Замечание*: здесь и далее дуга "Проверка политики безопасности" в работе Менеджера опускается.

> *Замечание*: альтернативное ветвление в случае негативного сценария на диаграмме не приводится, если не сказано другое.

> *Замечание*: сессионный ключ - это аутентфикационный ключ доступа, назначаемый Аутнетификатором аккаунту Пользователя по логин-парольной паре.

```python
user.authenticate("user", "user")  # посылает запрос аутентификации
event = user.wait_for_authenticate()  # ожидает ответ на запрос аутентификации
if event.parameters.get("status") == "ok":
    user.session_token = event.parameters.get("session_token")  # присваивает сессионный ключ
                                                                # логин и пароль больше клиенту не нужны
```

Еще более подробная схема архитектурного решения задачи аутентификации описывает раздлеление сущностей на Клиентскую и Сервисную части (понятие "очереди" опущено):

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml

actor       "Пользователь-Клиент"                               as User_Client #BDE0FF
actor       "Пользователь-Сервис"                               as User_Service #CCC
participant "Динамический\nМенеджер-Клиент\nПользователя"       as User_Dynamic_Manager_Client #FFF

participant "Динамический\nПользователь-Клиент"                 as Dynamic_User_Client #FFF
participant "Менеджер-Сервис"                                   as Manager_Service #CCC
participant "Менеджер-Клиент"                                   as Manager_Client #BDE0FF

participant "Динамический\nАутентификатор-Клиент"               as Dynamic_Auth_Client #FFF
participant "Аутентификатор-Сервис"                             as Auth_Service #CCC
participant "Аутентификатор-Клиент"                             as Auth_Client #BDE0FF
database    "База данных"    as Database
participant "Динамический\nМенеджер-Клиент\nАутентификатора"    as Auth_Dynamic_Manager_Client #FFF

== ЗАПРОС аутентификации Пользователем ==

User_Client          -->>o   User_Dynamic_Manager_Client  : Пораждает динамического клиента\nдля запроса аутентификации\nпо логину и паролю\n(далее - ЗАПРОС)
User_Dynamic_Manager_Client      ->   Manager_Service     : Подключается и отправляет\nЗАПРОС в очередь событий \nСервиса
User_Client          ->      User_Service                 : Ожидает данные\nо сессионном ключе доступа (далее - ОТВЕТ)
activate User_Client #000

== Делегирование ЗАПРОСа ==

Manager_Client       ->      Manager_Service              : Получение элемента\nиз очереди Сервиса
Manager_Service      ->      Manager_Client               : Отдает ЗАПРОС
Manager_Client       -->>o   Dynamic_Auth_Client          : Пораждает динамического клиента,\nпередавая ему ЗАПРОС
Dynamic_Auth_Client  ->      Auth_Service                 : Подключается и отправляет\nЗАПРОС в очередь событий \nСервиса

== Отработка ЗАПРОСа - Получение ОТВЕТа ==

Auth_Client          ->      Auth_Service                 : Получение элемента\nиз очереди Сервиса
Auth_Service         ->      Auth_Client                  : Отдает ЗАПРОС
Auth_Client          ->      Database                     : Поиск аккаунта
Database             ->      Auth_Client                  : Выделение сессионного ключа доступа\n(далее - ОТВЕТ)

Auth_Client          -->>o   Auth_Dynamic_Manager_Client  : Пораждает динамического клиента,\nпередавая ему ОТВЕТ
Auth_Dynamic_Manager_Client ->  Manager_Service           : Подключается и отправляет\nОТВЕТ в очередь событий \nСервиса

== Перенаправление ОТВЕТа ==

Manager_Client       ->      Manager_Service           : Получение элемента\nиз очереди Сервиса
Manager_Service      ->      Manager_Client            : Отдает ОТВЕТ
Manager_Client       -->>o   Dynamic_User_Client       : Пораждает динамического клиента,\nпередавая ему ОТВЕТ

Dynamic_User_Client  ->      User_Service              : Подключается и отправляет\nОТВЕТ в очередь событий \nСервиса
User_Service         ->      User_Client               : Возвращает ОТВЕТ
deactivate User_Client

==  ==
@enduml
```
</details>

![](http://www.plantuml.com/plantuml/png/nLRDJXDH5DxFKzoKZIGswTgaH2soSsNSaP2nJBG95D8E9EwWzIT6L2GO4sD0U89BfJ8M65xXt3VoE_OopYcNcq7GtWG8dPdp_PpldEdTTXosufN5XI08mdgyr5B3Kw9TIkdORD0H_lP8cmxr-VyoVQ5ZIl3FgUcKbF-4RVMu7RNcQWkDg1chYVlJ3oepCqM1zgXlrl1HOjQB0ZsAMgkDUgGcQhLQi0nbZNfZEGHqYRP1-fGqdQ3UQrHUfm4--JdRfAyi1Z-7z8CHXK9STlFxK1g1ddxU31SRzRc7OJDycjCy0y65gHGotQN-71rK1BH4lYZLxx4BoUhpMEqrz8eeCZd5ZTmqNJQF4N7j1IMumdQcNZh2odihyJEFbLw4mhO2Zt4yRbvLYXzerD3vC0wVXEreE8eVIIDwMg5pcavHzArvMJgtnTvvKsFbaKMwbAFidwngLT5dsiJaVACTsbEadNLVuM-YtFE5dnDLhGP1VdYoKovFJIqfvHroTGUbXymX5kP1S0SkEhn9wJkbYWP_l20DDmvvfIWsdyvG9iMzsgi5pvnneMEko3YcgrZX6MaypohVppPl4NDXWNrL5ZvD1XuzLlYKKXUc7SUAHUa1eq3PRxbcdGM0GGgoh45JZqNnDP0LFUhnNUp86kV3R2Z8JUa0SUjmU1JkpqqGQNTdG92FtFoZ1sHtq9CatnMRRUe39mKsjmQ_4qhv0dwVg4nR7mzmEo2mo-OgwIcAxzCMVQBzINwjDLR3E9Bll4gbCapfjiqQkiKTeXxpu128nW21eoWR8WIxcY84svHtcRr5CE-6CSybBg4ZqGLkdJJT2ICvI8B2TC1OouK-jp8xPCxTQyzrX-msJqmcLhFz75YOOhgIePE4rIstjJnZcGoE5flDPUc08NX7Z4Qgx0X5BhisT2xN_S9lFdG2ni5142mQEh-owTmxy39bJ6wWK7h0zfhkK57WUBGusosie4DU2fbZZbLaWspZ99SH7Bry6xarsq7plbZ_wQ1b30CF1LZetdBN6BCC-6-7RDS-m1vavTt3TFKDFjxrxHkZJ5UnpJtwflvVQGeS13nV4SQN9HUL74_FAtKBXO-enspCculjcOzSNq0ukmg1_0K0)

Журнал работы Клиента Пользователя демонстрирует факт обработки События всей цепочкой сущностей и успешности аутентификации по логину и паролю:

```text
2023-01-18 01:52:49,690 INFO     [DynamicManagerClientInUserSide] will be work with localhost:9090.
2023-01-18 01:52:49,733 INFO     [DynamicManagerClientInUserSide] connect.
2023-01-18 01:52:49,734 INFO     [DynamicManagerClientInUserSide] put event Event(source='user', destination='authenticator', operation='authenticate', parameters={'login': 'user', 'password': 'user'}).
2023-01-18 01:52:49,909 INFO     [UserClient] send request for event get from service.
2023-01-18 01:52:50,089 INFO     [UserClient] get no event response from service. Sleep 30 seconds.
2023-01-18 01:53:20,149 INFO     [UserClient] send request for event get from service.
2023-01-18 01:53:20,334 INFO     [UserClient] get event Event(source='authenticator', destination='user', operation='authenticate_response', parameters={'status': 'ok', 'message': 'authentication is allow', 'session_token': 'e8a63f9a-1276-412f-ad3c-a5752ea91af3'}) from service.
```

Виден факт ответа:
* `operation='authenticate_response'`;
* `'session_token': 'e8a63f9a-1276-412f-ad3c-a5752ea91af3'`.

##### Запрос данных по валидному сессонному ключу

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
actor       Пользователь                         as User
participant "Менеджер\n(монитор безопасности)"   as Manager
database    "Аутентификатор\n(и база данных)"    as Database

User     -> Manager  : Запрос данных:\nсессионный ключ
Manager  -> Database : Запрос данных:\nсессионный ключ
Database -> Database : Проверка ключа на факт\nприсутствия среди\nаутентификационных\n
Database -> Manager  : Ответ:\nпредоставленные данные
Manager  -> User     : Ответ:\nпредоставленные данные
@enduml
```

</details>

![](http://www.plantuml.com/plantuml/png/fPAzJiCm58LtFuNL2GPUe0FgmCh8biMq5Qe4fch2dfOV1X2miI3w2YR2O1gIliAzRyInJIsrWgcMalZ7_ixnkH6zl52JukBiLAX-SJwHiT6SMghvdZxnhSZmZAmVo_-QokLHFfo8CM2Z_cYiT24xz89J3Pvt-Y3BPQPtw1l0XXo0BPUItiW6ZIKqfbXeUOebjzk9p4EbrGcm0rMeOvKFCGli4ry6GutVobVaQ14ijb72UQm1raWe6r0RlkDhC2Fqu1ScXBSSxE_jhwIax4fwngabbzxD6gARQRYqy3Y5Q1kdwKj2l-O7lXKh2819PYjWWcm0vnv6bK_LNpuTyDq6BwHYQC6pJ0TT1mLa5iAjC7gKw9QXCWvRp9-1tYHBS9hfv6KphTS0jJphHhM0ZOKqMAZ9HWZPT7S_M0ihLM8BNc-e1_YHVm00)


```python
    user.session_token = event.parameters.get("session_token")  # присваивает сессионный ключ
    user.get_data_from_database()  # посылает запрос данных из базы данных
    event = user.wait_for_get_data_from_database()  # ожидает ответ на запрос данных из базы данных
```

Журнал работы Клиента Пользователя:
* `operation='get_data_from_database'`;
* `parameters={'session_token': 'e8a63f9a-1276-412f-ad3c-a5752ea91af3'}`.

```text
2023-01-18 01:53:20,377 INFO     [DynamicManagerClientInUserSide] will be work with localhost:9090.
2023-01-18 01:53:20,421 INFO     [DynamicManagerClientInUserSide] connect.
2023-01-18 01:53:20,422 INFO     [DynamicManagerClientInUserSide] put event Event(source='user', destination='authenticator', operation='get_data_from_database', parameters={'session_token': 'e8a63f9a-1276-412f-ad3c-a5752ea91af3'}).
2023-01-18 01:53:20,601 INFO     [UserClient] send request for event get from service.
2023-01-18 01:53:20,778 INFO     [UserClient] get no event response from service. Sleep 30 seconds.
2023-01-18 01:53:50,849 INFO     [UserClient] send request for event get from service.
2023-01-18 01:53:51,030 INFO     [UserClient] get event Event(source='authenticator', destination='user', operation='get_data_from_database_response', parameters={'status': 'ok', 'data': [{'value': 'One'}, {'value': 'Two', 'message': ':)'}, {'value': 'Three'}]}) from service.
```

Виден факт ответа:
* `operation='get_data_from_database_response'`;
* `'data': [{'value': 'One'}, {'value': 'Two', 'message': ':)'}, {'value': 'Three'}]`.

##### Проверка заведомо ложного сессионного ключа

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
actor       Пользователь                         as User #red
participant "Менеджер\n(монитор безопасности)"   as Manager
database    "Аутентификатор\n(и база данных)"    as Database

User     -> Manager  : Запрос данных:\nложный сессионный ключ
Manager  -> Database : Запрос данных:\nложный сессионный ключ
Database -> Database : Проверка ключа на факт\nприсутствия среди\nаутентификационных\n
Database -> Manager  : Ответ:\nсообщение о невалидности\nсессионного ключа
Manager  -> User     : Ответ:\nсообщение о невалидности\nсессионного ключа
@enduml
```

</details>>

![](http://www.plantuml.com/plantuml/png/jPEzJW9158NxVOe9Dbhu0XI6mjRIZcQ4ZI7HbUokFU2FCHgrip7o2WCoEBBkyWhtlf7dpiea4Erq20DpcVdEkMVOLfRhD3y_FObq9pzBLJreJ1KLV4_l-9oIuH5PMQlVXixKOHQdQYkDkr4Vn5wdrzT9hXhqWgCbtZEQa-L1EzccJr1BSg1MF50q8Uk5bX0QKedY43-vdKODFj29FexJgAjpVQIp65LWd_Z2kofbAr-IeuNtMTKIJh06MAEWR40j-OwlmAoX-z-mAFA-PUpkhQIKQYfwngab3yJD6gBPJgY0sxaiwKF1ikKXPkUxgeimK_03tqI12FfAy-_eWRX17mkPffAtn18EoDSI4_8ojE0HnCI4WmBIzB5FiNg4BCfoPmvRp8zHNmTBiDrEWfVD75yzrF88hQ6F2gy9tmeE0Ake4aiMMmmLgCp27m3IczrZVfC3ePsrVCDD_hjgAqwwU6Q-0000)

```python
user.session_token = '0123-4567-89AB-CDEF'  # присваивает заведомо ложный сессионный ключ
user.check_session_token()  # посылает запрос проверки валидности сессионного ключа
event = user.wait_for_check_session_token()  # ожидает ответ на запрос валидности
```

Журнал работы Клиента Пользователя:
* `operation='check_session_token'`;
* `parameters={'session_token': '0123-4567-89AB-CDEF'}`.

```text
2023-01-18 01:53:51,077 INFO     [DynamicManagerClientInUserSide] will be work with localhost:9090.
2023-01-18 01:53:51,121 INFO     [DynamicManagerClientInUserSide] connect.
2023-01-18 01:53:51,122 INFO     [DynamicManagerClientInUserSide] put event Event(source='user', destination='authenticator', operation='check_session_token', parameters={'session_token': '0123-4567-89AB-CDEF'}).
2023-01-18 01:53:51,298 INFO     [UserClient] send request for event get from service.
2023-01-18 01:53:51,474 INFO     [UserClient] get no event response from service. Sleep 30 seconds.
2023-01-18 01:54:21,526 INFO     [UserClient] send request for event get from service.
2023-01-18 01:54:21,702 INFO     [UserClient] get event Event(source='authenticator', destination='user', operation='check_session_token_response', parameters={'status': 'error', 'message': 'session token is invalid'}) from service.
```

Виден факт ответа:
* `operation='check_session_token_response'`;
* `'status': 'error', 'message': 'session token is invalid'`.

##### Попытка запроса данных по заведомо ложному сессонному ключу

<details>
<summary>см. код для генерации схемы на сайте Plantuml</summary>

```text
@startuml
actor       Пользователь                         as User #red
participant "Менеджер\n(монитор безопасности)"   as Manager
database    "Аутентификатор\n(и база данных)"    as Database

User     -> Manager  : Запрос данных:\nложный сессионный ключ
Manager  -> Database : Запрос данных:\nложный сессионный ключ
Database -> Database : Проверка ключа на факт\nприсутствия среди\nаутентификационных\n
Database -> Manager  : Ответ:\nсообщение о невалидности ключа
Manager  -> User     : Ответ:\nсообщение о невалидности ключа
@enduml
```

</details>

![](http://www.plantuml.com/plantuml/png/hPEzJW9158NxVOe9Dbhu0XI6mjRIZcQ4ZI7HaUokFOi_ncZKpiR8AmmRqN5nXrUuzuqyTnSdGhHZ20jtVhvpxXdef9bEilFJaqZtihD4DOCcv6dEz_I1pu8iZsacjVflw5GTfd6YjfAu7mr17FG6GsqorQ8N7AtmVgDtcl6eQxRfYpoc7AYUHugcM1MX1OHoB7ZEiUHsMWtuG1jz72THNsVwIASnPe5zuelQLILR-P8SbRLFtqWumLfWhOAofGeRx_WAp0QwluH5KUrRnkvU8oLbMz4pJYru96vM4EskeJbvT8EIFXNdQ2l7qqbNoqag4TS3tqG_HD23vkReWRX6dmYP2ibROWa7v6k51_AoLF8OOcB2GG5frh4Ng1uXYscvCuSjzi-ehuCbsEwQu6KznrUS4YTZj8O-F5vJlXKS03D57fPG5MJHk8Da-07yihsIOxYnZT4xiUdZF_0D)

```python
user.session_token = '0123-4567-89AB-CDEF'  # присваивает заведомо ложный сессионный ключ
user.get_data_from_database() # посылает запрос данных из базы данных
event = user.wait_for_get_data_from_database()  # ожидает ответ на запрос данных из базы данных
#
```

Журнал работы Клиента Пользователя:
* `operation='get_data_from_database'`;
* `parameters={'session_token': '0123-4567-89AB-CDEF'}`.

```text
2023-01-18 01:54:21,802 INFO     [DynamicManagerClientInUserSide] put event Event(source='user', destination='authenticator', operation='get_data_from_database', parameters={'session_token': '0123-4567-89AB-CDEF'}).
2023-01-18 01:54:21,989 INFO     [UserClient] send request for event get from service.
2023-01-18 01:54:22,166 INFO     [UserClient] get no event response from service. Sleep 30 seconds.
2023-01-18 01:54:52,238 INFO     [UserClient] send request for event get from service.
2023-01-18 01:54:52,414 INFO     [UserClient] get event Event(source='authenticator', destination='user', operation='get_data_from_database_response', parameters={'status': 'error', 'message': 'session token is invalid'}) from service.
```

Виден факт ответа:
* `operation='get_data_from_database_response'`;
* `'status': 'error', 'message': 'session token is invalid'`.

## Интерактивность

В целях изучения аудиторией курса указанной модели на практике ее реализация продемонстрирована на платформе Datalore с учетом особенностей запуска клиент-сервисной архитектуры в условиях одного потока исполнения:
* https://datalore.jetbrains.com/notebook/UkXbzl6pNHmzi3r8XeCioW/Y58uLwCLBsyR2J941RZ2iP/ 

## Вывод

В данном примере на языке программирования Python продемонстрирован проект модели аутентификации пользователя с применением к разработке киберимунного подхода. Функционирующие сущности обособлены, их взаимодействие осуществляется через отдельную сущность, осуществляющую проверку политики безопасности запросов. Модель функционирует в режиме запрос-ответ, События имеют цикл обработки. 

При этом, как продемонстрировано, цель безопасности достигнута: данные из `Базы Данных` предоставлются только аутентифицированным `Пользователям`. 

  
