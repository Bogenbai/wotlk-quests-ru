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

- Windows и видеокарта NVIDIA. Проверено на RTX 4060 Ti, там полная сборка заняла около 37 часов.
- [Python 3.12](https://www.python.org/downloads/). При установке поставьте галочку **Add python.exe to PATH**.
- [Git](https://git-scm.com/download/win).
- Клиент WoW 3.3.5a с установленными в `Interface\AddOns`:
  - `AI_VoiceOver` версии 1.4.5;
  - английским пакетом `AI_VoiceOverData_Wrath`. Он обязателен: с его записей клонируются голоса NPC.
- Свободное место: около 8 ГБ на диске C (библиотеки и модель) и около 1,5 ГБ в папке игры (озвучка).

### 2. Скачайте репозиторий в папку игры

1. Откройте папку игры (ту, где лежит `Wow.exe`).
2. Кликните в адресную строку Проводника, введите `powershell` и нажмите Enter. Откроется окно PowerShell в этой папке.
3. Выполните:

```powershell
git clone https://github.com/Bogenbai/wotlk-quests-ru.git
cd wotlk-quests-ru
```

Рядом с `Wow.exe` появится папка `wotlk-quests-ru`. Все следующие команды выполняйте в том же окне PowerShell.

### 3. Установите библиотеки

Займёт 10–20 минут в зависимости от интернета, на диске C займёт около 5,6 ГБ.

```powershell
python -m venv $HOME\VoiceTTS\venv_xtts
$py = "$HOME\VoiceTTS\venv_xtts\Scripts\python.exe"
& $py -m pip install -r requirements.txt
& $py -m pip install transformers==4.55.4
```

Последняя команда выведет красное предупреждение о конфликте версий `coqui-tts` и `transformers`. Так и должно быть: с другой версией модель не запускается.

Если вы закрыли окно PowerShell, перед следующими шагами откройте его заново в папке `wotlk-quests-ru` и снова выполните строку `$py = ...`.

### 4. Скачайте русские тексты квестов

```powershell
& $py tools\download_sql.py sql
```

Появится папка `sql` с 10 файлами, примерно 75 МБ.

### 5. Отберите квесты

```powershell
& $py tools\select_quests.py sql work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua
```

В конце должна появиться строка вида `ruRU quests 9456 selected 5825`.

### 6. Запустите генерацию

Дважды кликните `start_voice.bat`.

- При первом запуске скачается модель XTTS-v2, около 1,8 ГБ. Запуская генерацию, вы принимаете её [лицензию](LICENSES/CPML-1.0.txt).
- Генерация идёт в фоне. Окно можно закрыть, компьютером можно пользоваться и играть.
- Посмотреть прогресс: `Get-Content work\voice.log -Tail 5`. Там видно, сколько файлов готово и сколько часов осталось.
- Озвучка пишется прямо в `Interface\AddOns\AI_VoiceOverData_Russian`. Перезапустите клиент один раз, а дальше новые квесты подхватываются командой `/reload`.

### 7. Остановка и продолжение

- `stop_voice.bat` — остановить.
- `start_voice.bat` — продолжить. Готовые файлы не переделываются.

### 8. Таблица прогресса и архивы для релиза

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
