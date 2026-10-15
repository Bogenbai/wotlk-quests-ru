import os

MODULE_NAME = "AI_VoiceOverData_Russian"
MODULE_PRIORITY = 200
HEADER = "if not VoiceOver or not VoiceOver.DataModules then return end\n"

TOC = f"""## Interface: 30300
## Title: VoiceOver Data - Russian
## Version: 0.2
## LoadOnDemand: 1
## OptionalDeps: AI_VoiceOver
## X-Part-Of: VoiceOver
## X-Child-Of: VoiceOver
## X-VoiceOver-DataModule-Version: 1
## X-VoiceOver-DataModule-Priority: {MODULE_PRIORITY}

Module.lua
generated\\quest_id_lookups.lua
generated\\sound_length_table.lua
"""

MODULE_LUA = f"""{HEADER}
{MODULE_NAME} = {{}}

function {MODULE_NAME}:GetSoundPath(fileName, event)
    setfenv(1, VoiceOver)
    if Enums.SoundEvent:IsQuestEvent(event) then
        return format([=[generated\\sounds\\quests\\%s.ogg]=], fileName)
    elseif Enums.SoundEvent:IsGossipEvent(event) then
        return format([=[generated\\sounds\\gossip\\%s.ogg]=], fileName)
    end
end

VoiceOver.DataModules:Register("{MODULE_NAME}", {MODULE_NAME})
"""


def lua_string(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "") + '"'


def lookup_key(text):
    return text.replace('"', "'")


def build_quest_id_lookup(quests):
    lookup = {"accept": {}, "complete": {}, "progress": {}}
    for source, npc_field in (("accept", "starters"), ("complete", "enders")):
        ambiguous = {}
        for quest in quests:
            key = lookup_key(quest["title"])
            if not key:
                continue
            if quest["title_unique"]:
                lookup[source][key] = quest["id"]
                continue
            names = ambiguous.setdefault(key, {})
            for npc in quest[npc_field]:
                if npc["name"]:
                    names.setdefault(lookup_key(npc["name"]), set()).add(quest["id"])
        for key, names in ambiguous.items():
            resolved = {name: next(iter(ids)) for name, ids in names.items() if len(ids) == 1}
            if resolved:
                lookup[source][key] = resolved
    return lookup


def _write_atomic(path, text):
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(temp, path)


def write_static_files(module_dir, quests):
    os.makedirs(os.path.join(module_dir, "generated", "sounds", "quests"), exist_ok=True)
    _write_atomic(os.path.join(module_dir, MODULE_NAME + ".toc"), TOC)
    _write_atomic(os.path.join(module_dir, "Module.lua"), MODULE_LUA)

    lines = [HEADER, f"{MODULE_NAME}.QuestIDLookup = {{"]
    for source, titles in build_quest_id_lookup(quests).items():
        lines.append(f"    {source} = {{")
        for title, value in sorted(titles.items()):
            if isinstance(value, dict):
                inner = ", ".join(f"[{lua_string(n)}] = {i}" for n, i in sorted(value.items()))
                lines.append(f"        [{lua_string(title)}] = {{ {inner} }},")
            else:
                lines.append(f"        [{lua_string(title)}] = {value},")
        lines.append("    },")
    lines.append("}")
    _write_atomic(os.path.join(module_dir, "generated", "quest_id_lookups.lua"), "\n".join(lines) + "\n")


def write_sound_lengths(module_dir, lengths):
    lines = [HEADER, f"{MODULE_NAME}.SoundLengthLookupByFileName = {{"]
    for name, length in sorted(lengths.items()):
        lines.append(f'    ["{name}"] = {length:.2f},')
    lines.append("}")
    _write_atomic(os.path.join(module_dir, "generated", "sound_length_table.lua"), "\n".join(lines) + "\n")
