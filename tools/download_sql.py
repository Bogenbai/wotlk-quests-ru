import os
import sys
import urllib.request

AZEROTHCORE_COMMIT = "01339ccfab9cd5d3d28546f79f38ad74d394b148"
BASE_URL = f"https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/{AZEROTHCORE_COMMIT}/data/sql/base/db_world"
TABLES = [
    "quest_template",
    "quest_template_locale",
    "quest_offer_reward_locale",
    "creature_template",
    "creature_template_locale",
    "creature_template_model",
    "creature_model_info",
    "creature_queststarter",
    "creature_questender",
    "factiontemplate_dbc",
    "broadcast_text",
    "broadcast_text_locale",
    "quest_greeting",
    "quest_greeting_locale",
    "creature_text",
]

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)
for table in TABLES:
    path = os.path.join(out_dir, table + ".sql")
    print(f"{table}...", flush=True)
    urllib.request.urlretrieve(f"{BASE_URL}/{table}.sql", path)
print("done")
