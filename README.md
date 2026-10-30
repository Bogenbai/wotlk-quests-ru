# wotlk-quests-ru

Русская нейросетевая озвучка квестов для WoW 3.3.5a с русским клиентом. Работает как пакет данных для [AI VoiceOver](https://github.com/mrthinger/wow-voiceover). Озвучено моделью [F5-TTS_RUSSIAN](https://huggingface.co/Misha24-10/F5-TTS_RUSSIAN), ударения расставлены [RUAccent](https://github.com/Den4ikAI/ruaccent). Голос каждого NPC взят из его записей в CatQuest, если они есть, иначе из русского клиента: из собственных реплик NPC или из общих фраз его модели.

https://github.com/user-attachments/assets/f2a37f24-1b5a-42a0-94ed-869f003e7f39

Создан для русскоязычных игроков. Язык — это не национальность, а культура — это не государство.

### Гибрид с CatQuest

Квесты 1–60 уровня по возможности звучат голосами из [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices) — озвучки автора Cathey для WoW Forever, сделанной на ElevenLabs. Она заметно живее нашей и учитывает пол персонажа. Мы перенесли её на 3.3.5a: файлы переименованы под AI VoiceOver, а реплики, текст которых на 3.3.5a заметно отличается, отброшены. Всё остальное — квесты 61–80, праздничные квесты, квесты без озвучки CatQuest и реплики NPC — озвучено у нас через F5-TTS. Записи CatQuest служат нам и образцами голоса: NPC, которых озвучил CatQuest, звучат у нас тем же голосом.

Спасибо Cathey за CatQuest. Если вы играете в WoW Forever, ставьте [оригинальный аддон](https://www.curseforge.com/wow/addons/catquest).

## Прогресс

<!-- progress:start -->
_Обновлено 30.10.2026._

Вся озвучка переделана на F5-TTS: русские голоса NPC и правильные ударения.

| Квесты Альянса и нейтральные | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 353 / 353 | `██████████` 100% | ✅ готово |
| Уровни 11–20 | 368 / 368 | `██████████` 100% | ✅ готово |
| Уровни 21–30 | 303 / 303 | `██████████` 100% | ✅ готово |
| Уровни 31–40 | 372 / 372 | `██████████` 100% | ✅ готово |
| Уровни 41–50 | 324 / 324 | `██████████` 100% | ✅ готово |
| Уровни 51–60 | 1352 / 1352 | `██████████` 100% | ✅ готово |
| Уровни 61–70 | 1086 / 1086 | `██████████` 100% | ✅ готово |
| Уровни 71–80 | 1322 / 1322 | `██████████` 100% | ✅ готово |
| Праздничные события | 345 / 345 | `██████████` 100% | ✅ готово |
| **Всего** | **5825 / 5825** | `██████████` **100%** | |

| Квесты Орды | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 327 / 327 | `██████████` 100% | ✅ готово |
| Уровни 11–20 | 284 / 284 | `██████████` 100% | ✅ готово |
| Уровни 21–30 | 169 / 169 | `██████████` 100% | ✅ готово |
| Уровни 31–40 | 153 / 153 | `██████████` 100% | ✅ готово |
| Уровни 41–50 | 160 / 160 | `██████████` 100% | ✅ готово |
| Уровни 51–60 | 384 / 384 | `██████████` 100% | ✅ готово |
| Уровни 61–70 | 285 / 285 | `██████████` 100% | ✅ готово |
| Уровни 71–80 | 558 / 558 | `██████████` 100% | ✅ готово |
| Праздничные события | 184 / 184 | `██████████` 100% | ✅ готово |
| **Всего** | **2504 / 2504** | `██████████` **100%** | |

| Реплики NPC вне квестов | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 688 / 688 | `██████████` 100% | ✅ готово |
| Уровни 11–20 | 431 / 431 | `██████████` 100% | ✅ готово |
| Уровни 21–30 | 723 / 723 | `██████████` 100% | ✅ готово |
| Уровни 31–40 | 378 / 378 | `██████████` 100% | ✅ готово |
| Уровни 41–50 | 457 / 457 | `██████████` 100% | ✅ готово |
| Уровни 51–60 | 881 / 881 | `██████████` 100% | ✅ готово |
| Уровни 61–70 | 1307 / 1307 | `██████████` 100% | ✅ готово |
| Уровни 71–80 | 1996 / 1996 | `██████████` 100% | ✅ готово |
| **Всего** | **6861 / 6861** | `██████████` **100%** | |

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
- `AI_VoiceOverData_Russian-Horde.zip` — озвучка квестов Орды, 0,7 ГБ, оттуда же. Нужна только тем, кто играет за Орду.
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

- Видеокарта NVIDIA. На RTX 4060 Ti квесты Альянса озвучиваются около 33 часов, Орды — ещё около 14, реплики NPC — около 11.
- [Python 3.12](https://www.python.org/downloads/) с опцией **Add python.exe to PATH** и [Git](https://git-scm.com/download/win).
- Русский клиент: голоса NPC берутся из его архивов в `Data\ruRU`.
- В `Interface\AddOns`: `AI_VoiceOver` 1.4.5 и английский пакет `AI_VoiceOverData_Wrath` — по нему отбираются реплики NPC и квесты без NPC.
- Около 12 ГБ на диске C и 2,7 ГБ в папке игры.

### 2. Скачайте репозиторий

Откройте PowerShell в папке игры (где лежит `Wow.exe`): введите `powershell` в адресной строке Проводника. Все команды ниже выполняются в этом окне.

```powershell
git clone https://github.com/Bogenbai/wotlk-quests-ru.git
cd wotlk-quests-ru
```

### 3. Установите библиотеки

10–20 минут, около 7 ГБ на диске C.

```powershell
python -m venv $HOME\VoiceTTS\venv_f5
$py = "$HOME\VoiceTTS\venv_f5\Scripts\python.exe"
& $py -m pip install -r requirements.txt
```

`$py` живёт только в текущем окне. Если откроете PowerShell заново, сначала снова выполните `cd` в папку репозитория и строку `$py = ...`.

### 4. Скачайте тексты и отберите квесты

```powershell
& $py tools\download_sql.py sql
& $py tools\select_quests.py sql work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua
```

Вторая команда должна закончиться строкой вида `ruRU quests 9456 selected 5825`. У восьми квестов русский текст в AzerothCore так и остался английским — для них берётся наш перевод из `tools\quest_text_fixes.json`.

Чтобы озвучить и квесты Орды, отберите их тоже — генерация возьмёт их после Альянса:

```powershell
& $py tools\select_quests.py sql work\quests_horde.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua horde
```

Реплики NPC вне квестов отбираются так и озвучиваются после квестов:

```powershell
& $py tools\select_gossip.py sql ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated work\gossip.json
```

### 5. Модуль CatQuest

Необязателен, но его записи станут образцами голоса для NPC квестов 1–60, поэтому собирайте его до голосов NPC. Скачайте и распакуйте [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices) в любую папку, например `..\_catquest\CatQuest_Voices`, затем:

```powershell
& $py tools\import_catquest.py ..\_catquest\CatQuest_Voices work\quests.json ..\Interface\AddOns\AI_VoiceOverData_CatQuest
```

### 6. Голоса NPC

```powershell
& $py tools\extract_ru_voices.py .. sql $HOME\VoiceTTS\ru_voices work\ru_voices.json work\quests.json work\quests_horde.json --gossip work\gossip.json --catquest ..\Interface\AddOns\AI_VoiceOverData_CatQuest
```

Для каждого NPC берутся его записи из CatQuest, иначе его собственные реплики из русского клиента, иначе общие фразы его модели. Уберите из команды то, чего не делали: `work\quests_horde.json`, `--gossip work\gossip.json` или `--catquest ...`.

### 7. Генерация

Запустите `start_voice.bat`, остановите `stop_voice.bat`. Повторный запуск продолжает с места остановки.

- Первый запуск скачивает модели F5-TTS_RUSSIAN, Whisper и RUAccent, около 3 ГБ.
- Каждый абзац проверяется распознаванием речи. Если сказано не то, абзац озвучивается заново, до 4 попыток. В логе это `match` — доля совпавших слов.
- Генерация идёт в фоне, можно играть.
- Прогресс и оставшееся время: `Get-Content work\voice.log -Tail 5`.
- Озвучка пишется прямо в `Interface\AddOns\AI_VoiceOverData_Russian`. После первого перезапуска клиента новые квесты подхватываются по `/reload`.

Неудачные файлы можно переозвучить с большим числом попыток: удалите их имена из `$HOME\VoiceTTS\progress\redo_f5.json` и запустите `powershell -ExecutionPolicy Bypass -File run_voice.ps1 -Attempts 8`.

## Лицензии

- Код — MIT.
- Наша озвучка сделана моделью [F5-TTS_RUSSIAN](https://huggingface.co/Misha24-10/F5-TTS_RUSSIAN) под лицензией [CC BY-NC 4.0](LICENSES/CC-BY-NC-4.0.txt), поэтому её можно использовать только некоммерчески.
- Озвучка в `AI_VoiceOverData_CatQuest` — из [CatQuest Voices](https://www.curseforge.com/wow/addons/catquest-voices), автор Cathey, лицензия [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Изменения: файлы переименованы под формат AI VoiceOver, часть реплик отброшена.
- `addon/AI_VoiceOver` основан на [AI VoiceOver](https://github.com/mrthinger/wow-voiceover) (Unlicense).
- Тексты квестов — из [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk) (GPL-2.0), исходно Blizzard Entertainment.
- Образцы голосов NPC — из русского клиента WoW (Blizzard Entertainment) и из CatQuest Voices.
- Отбор квестов и реплик опирается на пакет `AI_VoiceOverData_Wrath` от WrkX.
