# wotlk-quests-ru

Русская нейросетевая озвучка квестов для WoW 3.3.5a с русским клиентом. Работает как пакет данных для [AI VoiceOver](https://github.com/mrthinger/wow-voiceover). Голоса NPC склонированы моделью XTTS-v2 с английского пакета `AI_VoiceOverData_Wrath`.

## Прогресс

<!-- progress:start -->
_Обновлено 16.10.2026._

| Квесты Альянса и нейтральные | Готово | Прогресс | Статус |
|---|---|---|---|
| Уровни 1–10 | 353 / 353 | `██████████` 100% | ✅ готово |
| Уровни 11–20 | 32 / 368 | `█░░░░░░░░░` 8% | 🔄 в работе |
| Уровни 21–30 | 0 / 303 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 31–40 | 0 / 372 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 41–50 | 0 / 324 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 51–60 | 0 / 1352 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 61–70 | 0 / 1086 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Уровни 71–80 | 0 / 1322 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| Праздничные события | 0 / 345 | `░░░░░░░░░░` 0% | ⏳ в очереди |
| **Всего** | **385 / 5825** | `█░░░░░░░░░` **7%** | |

| Ещё не озвучено | Статус |
|---|---|
| Квесты Орды | ❌ не начато |
| Реплики NPC вне квестов | ❌ не начато |
| Тексты для женских персонажей | ❌ не начато |
<!-- progress:end -->

## Установка

1. Установите [AI VoiceOver 1.4.5](https://github.com/mrthinger/wow-voiceover) и, по желанию, английский пакет `AI_VoiceOverData_Wrath` — он озвучит то, чего нет в русском.
2. Распакуйте в `Interface\AddOns` с заменой файлов оба архива из [Releases](../../releases):
   - `AI_VoiceOver-ruRU-fix.zip` — исправления аддона для русского клиента;
   - `AI_VoiceOverData_Russian.zip` — озвучка.
3. Перезапустите клиент.

Проверка: `/run local s={event=1,questID=783} print(VoiceOver.DataModules:PrepareSound(s), s.filePath)` должна вывести `true` и путь в `AI_VoiceOverData_Russian`.

## Сборка своими руками

### 1. Что понадобится

- Видеокарта NVIDIA. На RTX 4060 Ti полная сборка занимает около 37 часов.
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

### 5. Генерация

Запустите `start_voice.bat`, остановите `stop_voice.bat`. Повторный запуск продолжает с места остановки.

- Первый запуск скачивает модель XTTS-v2 (1,8 ГБ).
- Генерация идёт в фоне, можно играть.
- Прогресс и оставшееся время: `Get-Content work\voice.log -Tail 5`.
- Озвучка пишется прямо в `Interface\AddOns\AI_VoiceOverData_Russian`. После первого перезапуска клиента новые квесты подхватываются по `/reload`.

### 6. Таблица прогресса и архивы для релиза

Обновить таблицу в этом README:

```powershell
& $py tools\progress_table.py work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Russian README.md
```

Собрать архивы для Releases (появятся в папке `dist`):

```powershell
& $py tools\package_release.py . ..\Interface\AddOns\AI_VoiceOverData_Russian dist
```

## Лицензии

- Код — MIT.
- Озвучка — [Coqui Public Model License](LICENSES/CPML-1.0.txt), только некоммерческое использование.
- `addon/AI_VoiceOver` основан на [AI VoiceOver](https://github.com/mrthinger/wow-voiceover) (Unlicense).
- Тексты квестов — из [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk) (GPL-2.0), исходно Blizzard Entertainment.
- Голоса NPC — с пакета `AI_VoiceOverData_Wrath` от WrkX.
