# wotlk-quests-ru

Русская нейросетевая озвучка квестов для World of Warcraft 3.3.5a (Wrath of the Lich King) с русским клиентом (`ruRU`).

Озвучка работает как пакет данных для аддона [AI VoiceOver](https://github.com/mrthinger/wow-voiceover): когда вы открываете окно квеста, NPC зачитывает его текст. Голос каждого NPC склонирован нейросетью XTTS-v2 с его голоса из английского пакета, поэтому персонаж звучит одинаково во всех своих квестах.

## Что озвучено

- Квесты Альянса и нейтральные: около 5 800 квестов, взятие и сдача.
- Тексты под мужского персонажа: обращения и формы глаголов в мужском роде.
- Ордынские квесты и реплики NPC вне квестов пока не озвучены. Для них играет английская озвучка, если стоит английский пакет.

## Установка

1. Установите [AI VoiceOver 1.4.5](https://github.com/mrthinger/wow-voiceover) в `Interface\AddOns\AI_VoiceOver`.
2. Желательно также поставить английский пакет `AI_VoiceOverData_Wrath` от WrkX: он озвучит всё, чего нет в русском пакете.
3. Скачайте из [Releases](../../releases) два архива:
   - `AI_VoiceOver-ruRU-fix.zip` — исправления аддона для русского клиента. Распакуйте в `Interface\AddOns` с заменой файлов.
   - `AI_VoiceOverData_Russian.zip` — сама озвучка. Распакуйте в `Interface\AddOns`.
4. Полностью перезапустите клиент.

### Зачем нужны исправления аддона

В клиенте 3.3.5a нет функции `GetQuestID`, поэтому AI VoiceOver определяет квест по названию и тексту. В базе пакетов названия английские, и на русском клиенте квест не находился, а вместо реплик NPC играла первая попавшаяся из его списка. Исправления:

- определяют ID квеста по журналу заданий, а если квест ещё не взят — запускают озвучку сразу после принятия;
- не подставляют чужую реплику, если текст не совпал;
- выводят в отладке, почему озвучка не нашлась.

### Проверка в игре

```
/run VoiceOver.Addon.db.profile.DebugEnabled = true
/run for _,m in VoiceOver.DataModules:GetModules() do print(m.METADATA.AddonName, m.METADATA.ModulePriority) end
/run local s={event=1,questID=783} print(VoiceOver.DataModules:PrepareSound(s), s.filePath)
```

Первая команда включает отладочные сообщения. Вторая должна показать `AI_VoiceOverData_Russian` с приоритетом 200 первым в списке. Третья должна вывести `true` и путь к файлу внутри `AI_VoiceOverData_Russian`.

## Как собрать озвучку самому

Нужны Windows, видеокарта NVIDIA и Python 3.12. Полная генерация на RTX 4060 Ti занимает около 37 часов.

```powershell
python -m venv $HOME\VoiceTTS\venv_xtts
$HOME\VoiceTTS\venv_xtts\Scripts\python.exe -m pip install -r requirements.txt
$HOME\VoiceTTS\venv_xtts\Scripts\python.exe -m pip install transformers==4.55.4
```

`coqui-tts` формально требует `transformers>=4.57`, но с PyTorch 2.7.1 работает только 4.55.4, поэтому она ставится отдельной командой. Предупреждение pip о конфликте версий можно игнорировать.

Клонируйте репозиторий в папку игры (например, `World of Warcraft\wotlk-quests-ru`) и выполните:

```powershell
$py = "$HOME\VoiceTTS\venv_xtts\Scripts\python.exe"
& $py tools\download_sql.py sql
& $py tools\select_quests.py sql work\quests.json ..\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sound_length_table.lua
.\start_voice.bat
```

- `download_sql.py` скачивает нужные таблицы из базы [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk): русские тексты квестов, квестодателей и фракции.
- `select_quests.py` отбирает квесты Альянса и нейтральные и сортирует их по уровню.
- `start_voice.bat` запускает генерацию в фоне. Озвучка пишется прямо в `Interface\AddOns\AI_VoiceOverData_Russian`, готовые квесты подхватываются в игре по `/reload`.
- `stop_voice.bat` останавливает генерацию. Повторный запуск продолжает с места остановки.
- Прогресс и оставшееся время — в `work\voice.log`.

Образцы голосов берутся из английского пакета `AI_VoiceOverData_Wrath`, он должен лежать в `Interface\AddOns`.

Архивы для релиза собираются так:

```powershell
& $py tools\package_release.py . ..\Interface\AddOns\AI_VoiceOverData_Russian dist
```

## Ограничения

- Ударения и произношение фэнтезийных имён иногда неверные.
- Текст для женских персонажей не генерируется.
- Тексты квестов на конкретном сервере могут немного отличаться от базы AzerothCore. Тогда квест определяется не при открытии окна, а после принятия.

## Лицензии и благодарности

- Код в этом репозитории распространяется под лицензией MIT, см. `LICENSE`.
- Сгенерированная озвучка создана моделью [XTTS-v2](https://huggingface.co/coqui/XTTS-v2) и распространяется по [Coqui Public Model License 1.0.0](LICENSES/CPML-1.0.txt): **только для некоммерческого использования**.
- Исправленные файлы в `addon/AI_VoiceOver` основаны на [AI VoiceOver](https://github.com/mrthinger/wow-voiceover) (Unlicense).
- Голоса NPC склонированы с английского пакета `AI_VoiceOverData_Wrath` от WrkX.
- Русские тексты квестов взяты из базы [AzerothCore](https://github.com/azerothcore/azerothcore-wotlk) (GPL-2.0).
- World of Warcraft и его тексты принадлежат Blizzard Entertainment. Это некоммерческий фанатский проект.
