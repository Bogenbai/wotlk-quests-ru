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

Без исправлений озвучка на русском клиенте не работает: в 3.3.5a нет `GetQuestID`, и аддон ищет квест по английскому названию.

Проверка: `/run local s={event=1,questID=783} print(VoiceOver.DataModules:PrepareSound(s), s.filePath)` должна вывести `true` и путь в `AI_VoiceOverData_Russian`.

## Сборка

Нужны Windows, NVIDIA GPU и Python 3.12. Репозиторий клонируется в папку игры.

```powershell
python -m venv $HOME\VoiceTTS\venv_xtts
$py = "$HOME\VoiceTTS\venv_xtts\Scripts\python.exe"
& $py -m pip install -r requirements.txt
& $py -m pip install transformers==4.55.4
& $py tools\download_sql.py sql
& $py tools\select_quests.py sql work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua
.\start_voice.bat
```

`transformers` ставится отдельно: `coqui-tts` требует 4.57+, но с PyTorch 2.7.1 работает только 4.55.4.

- `start_voice.bat` / `stop_voice.bat` — запуск и остановка, генерация продолжается с места остановки. Лог — `work\voice.log`.
- `& $py tools\progress_table.py work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Russian README.md` — обновить таблицу прогресса.
- `& $py tools\package_release.py . ..\Interface\AddOns\AI_VoiceOverData_Russian dist` — собрать архивы для релиза.

## Лицензии

- Код — MIT.
- Озвучка — [Coqui Public Model License](LICENSES/CPML-1.0.txt), только некоммерческое использование.
- `addon/AI_VoiceOver` основан на [AI VoiceOver](https://github.com/mrthinger/wow-voiceover) (Unlicense).
- Тексты квестов — из [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk) (GPL-2.0), исходно Blizzard Entertainment.
- Голоса NPC — с пакета `AI_VoiceOverData_Wrath` от WrkX.
