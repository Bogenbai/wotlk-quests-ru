# wotlk-quests-ru

Русская нейросетевая озвучка квестов для WoW 3.3.5a с русским клиентом. Работает как пакет данных для [AI VoiceOver](https://github.com/mrthinger/wow-voiceover). Голоса NPC склонированы моделью XTTS-v2 с английского пакета `AI_VoiceOverData_Wrath`.

https://github.com/user-attachments/assets/f2a37f24-1b5a-42a0-94ed-869f003e7f39

Создан для русскоязычных игроков. Язык — это не национальность, а культура — это не государство.

### Гибрид с CatQuest

Квесты 1–60 уровня по возможности звучат голосами из [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices) — озвучки автора Cathey для WoW Forever, сделанной на ElevenLabs. Она заметно живее нашей и учитывает пол персонажа. Мы перенесли её на 3.3.5a: файлы переименованы под AI VoiceOver, а реплики, текст которых на 3.3.5a заметно отличается, отброшены. Всё остальное — квесты 61–80, праздничные квесты, квесты без озвучки CatQuest и реплики NPC — озвучено у нас через XTTS-v2.

Спасибо Cathey за CatQuest. Если вы играете в WoW Forever, ставьте [оригинальный аддон](https://www.curseforge.com/wow/addons/catquest).

## Прогресс

<!-- progress:start -->
_Обновлено 26.10.2026._

Идёт переозвучка всего на F5-TTS с русскими голосами NPC и правильными ударениями. Таблица показывает её прогресс; пока файл не переозвучен, в игре играет его прошлая версия.

| Квесты Альянса и нейтральные | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 116 / 353 | `███░░░░░░░` 34% | 🔄 в работе |
| Уровни 11–20 | 109 / 368 | `███░░░░░░░` 30% | 🔄 в работе |
| Уровни 21–30 | 38 / 303 | `█░░░░░░░░░` 12% | 🔄 в работе |
| Уровни 31–40 | 73 / 372 | `██░░░░░░░░` 17% | 🔄 в работе |
| Уровни 41–50 | 30 / 324 | `█░░░░░░░░░` 9% | 🔄 в работе |
| Уровни 51–60 | 372 / 1352 | `███░░░░░░░` 29% | 🔄 в работе |
| Уровни 61–70 | 1085 / 1086 | `██████████` 100% | 🔄 в работе |
| Уровни 71–80 | 445 / 1322 | `████░░░░░░` 36% | 🔄 в работе |
| Праздничные события | 0 / 345 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| **Всего** | **2268 / 5825** | `████░░░░░░` **40%** | |

| Квесты Орды | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 0 / 327 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 11–20 | 0 / 284 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 21–30 | 0 / 169 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 31–40 | 0 / 153 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 41–50 | 0 / 160 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 51–60 | 0 / 384 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 61–70 | 0 / 285 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 71–80 | 0 / 558 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Праздничные события | 0 / 184 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| **Всего** | **0 / 2504** | `░░░░░░░░░░` **0%** | |

| Реплики NPC вне квестов | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 0 / 688 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 11–20 | 0 / 431 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 21–30 | 0 / 723 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 31–40 | 0 / 378 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 41–50 | 0 / 457 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 51–60 | 0 / 881 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 61–70 | 0 / 1307 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 71–80 | 0 / 1996 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| **Всего** | **0 / 6861** | `░░░░░░░░░░` **0%** | |

| Ещё не озвучено | Статус |
|---|---|
| Тексты для женских персонажей | ❌ не начато |
<!-- progress:end -->

## Установка

Нужен клиент WoW 3.3.5a на русском языке. Наша часть озвучки рассчитана на мужского персонажа, часть от CatQuest — на оба пола.

### 1. Скачайте архивы

- `AI_VoiceOver-WoW_3.3.5-v1.4.5.zip` — сам аддон, со [страницы релиза AI VoiceOver 1.4.5](https://github.com/mrthinger/wow-voiceover/releases/tag/v1.4.5). Нужна именно версия 1.4.5 и именно файл для 3.3.5.
- `AI_VoiceOver-ruRU-fix.zip` — исправления для русского клиента, из [Releases](../../releases) этого репозитория.
- `AI_VoiceOverData_Russian.zip` — озвучка квестов Альянса и нейтральных и реплик NPC, 1,9 ГБ, оттуда же.
- `AI_VoiceOverData_Russian-Horde.zip` — озвучка квестов Орды, 0,6 ГБ, оттуда же. Нужна только тем, кто играет за Орду.
- `AI_VoiceOverData_CatQuest.zip` — озвучка квестов 1–60 из CatQuest, 0,9 ГБ, оттуда же. Необязательна, но с ней квесты 1–60 звучат лучше.

### 2. Распакуйте в папку аддонов

Закройте игру и откройте в папке игры (где лежит `Wow.exe`) папку `Interface\AddOns`. Если её нет, создайте.

Распакуйте туда архивы строго по порядку:

1. `AI_VoiceOver-WoW_3.3.5-v1.4.5.zip`.
2. `AI_VoiceOver-ruRU-fix.zip`. Windows спросит про замену трёх файлов — ответьте «Заменить». Без этого шага русская озвучка играть не будет.
3. `AI_VoiceOverData_Russian.zip`.
4. `AI_VoiceOverData_Russian-Horde.zip`, если играете за Орду. Он дополняет ту же папку `AI_VoiceOverData_Russian` — на вопрос о слиянии папок ответьте «Да».
5. `AI_VoiceOverData_CatQuest.zip`, если скачали.

Если у вас уже стоит прошлая версия озвучки, распакуйте новые архивы поверх с заменой файлов.

В `Interface\AddOns` должны получиться папки `AI_VoiceOver` и `AI_VoiceOverData_Russian`. Если внутри `AI_VoiceOver` лежит ещё одна `AI_VoiceOver`, перенесите внутреннюю на уровень выше.

### 3. Включите в игре

Запустите игру. На экране выбора персонажа нажмите «Модификации» и проверьте, что включены `VoiceOver`, `VoiceOver Data - Russian` и, если ставили, `VoiceOver Data - Russian (CatQuest)`.

Озвучка играет, когда открываете окно квеста у NPC — при взятии и при сдаче, — и когда заговариваете с NPC.

### Если не играет

Введите в чат:

```
/run local s={event=1,questID=783} print(VoiceOver.DataModules:PrepareSound(s), s.filePath)
```

Должно вывести `true` и путь, в котором есть `AI_VoiceOverData_Russian` или `AI_VoiceOverData_CatQuest`. Если `false` — проверьте, что второй архив распакован с заменой файлов.

Английский пакет `AI_VoiceOverData_Wrath` можно поставить вместе с русским: он озвучит по-английски то, чего ещё нет на русском.

## Сборка своими руками

### 1. Что понадобится

- Видеокарта NVIDIA. На RTX 4060 Ti квесты Альянса озвучиваются около 37 часов, Орды — ещё около 16, реплики NPC — около 12.
- [Python 3.12](https://www.python.org/downloads/) с опцией **Add python.exe to PATH** и [Git](https://git-scm.com/download/win).
- В `Interface\AddOns`: `AI_VoiceOver` 1.4.5 и английский пакет `AI_VoiceOverData_Wrath` — с его записей клонируются голоса NPC.
- Около 8 ГБ на диске C и 1,5 ГБ в папке игры.

### 2. Скачайте репозиторий

Откройте PowerShell в папке игры (где лежит `Wow.exe`): введите `powershell` в адресной строке Проводника. Все команды ниже выполняются в этом окне.

```powershell
git clone https://github.com/Bogenbai/wotlk-quests-ru.git
cd wotlk-quests-ru
```

### 3. Установите библиотеки

10–20 минут, около 5,6 ГБ на диске C.

```powershell
python -m venv $HOME\VoiceTTS\venv_xtts
$py = "$HOME\VoiceTTS\venv_xtts\Scripts\python.exe"
& $py -m pip install -r requirements.txt
& $py -m pip install transformers==4.55.4
```

Красное предупреждение о конфликте версий `coqui-tts` и `transformers` в конце — это нормально.

`$py` живёт только в текущем окне. Если откроете PowerShell заново, сначала снова выполните `cd` в папку репозитория и строку `$py = ...`.

### 4. Скачайте тексты и отберите квесты

```powershell
& $py tools\download_sql.py sql
& $py tools\select_quests.py sql work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua
```

Вторая команда должна закончиться строкой вида `ruRU quests 9456 selected 5825`.

Чтобы озвучить и квесты Орды, отберите их тоже — генерация возьмёт их после Альянса:

```powershell
& $py tools\select_quests.py sql work\quests_horde.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua horde
```

Реплики NPC вне квестов отбираются так и озвучиваются после квестов:

```powershell
& $py tools\select_gossip.py sql ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated work\gossip.json
```

### 5. Генерация

Запустите `start_voice.bat`, остановите `stop_voice.bat`. Повторный запуск продолжает с места остановки.

- Первый запуск скачивает модель XTTS-v2 (1,8 ГБ).
- Генерация идёт в фоне, можно играть.
- Прогресс и оставшееся время: `Get-Content work\voice.log -Tail 5`.
- Озвучка пишется прямо в `Interface\AddOns\AI_VoiceOverData_Russian`. После первого перезапуска клиента новые квесты подхватываются по `/reload`.

### 6. Модуль CatQuest

Скачайте и распакуйте [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices) в любую папку, например `..\_catquest\CatQuest_Voices`, затем:

```powershell
& $py tools\import_catquest.py ..\_catquest\CatQuest_Voices work\quests.json ..\Interface\AddOns\AI_VoiceOverData_CatQuest
```

## Лицензии

- Код — MIT.
- Озвучка XTTS — [Coqui Public Model License](LICENSES/CPML-1.0.txt), только некоммерческое использование.
- Озвучка в `AI_VoiceOverData_CatQuest` — из [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices), автор Cathey, лицензия [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Изменения: файлы переименованы под формат AI VoiceOver, часть реплик отброшена.
- `addon/AI_VoiceOver` основан на [AI VoiceOver](https://github.com/mrthinger/wow-voiceover) (Unlicense).
- Тексты квестов — из [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk) (GPL-2.0), исходно Blizzard Entertainment.
- Голоса NPC — с пакета `AI_VoiceOverData_Wrath` от WrkX.
