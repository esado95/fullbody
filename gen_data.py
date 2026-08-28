# -*- coding: utf-8 -*-
"""Генерирует data.js из программ Full Body и Сплит.

Если рядом лежит personal.json (не коммитится), дополнительно собирает
starter-fullbody.json — файл с личными весами для загрузки в приложение.
"""
import json
import math
import os

# упражнение: [группа, оборудование, шаг веса кг, минимальный вес кг]
CATALOG = {
    "Приседания со штангой":                      ["Ноги",    "Штанга",    2.5, 20],
    "Становая тяга":                              ["Спина",   "Штанга",    2.5, 20],
    "Жим штанги лежа":                            ["Грудь",   "Штанга",    2.5, 20],
    "Жим штанги лежа узким хватом":               ["Трицепс", "Штанга",    2.5, 20],
    "Жим под углом 45 градусов":                  ["Грудь",   "Штанга",    2.5, 20],
    "Жим штанги стоя":                            ["Плечи",   "Штанга",    2.5, 20],
    "Жим штанги сидя":                            ["Плечи",   "Штанга",    2.5, 20],
    "Жим гантелей лежа":                          ["Грудь",   "Гантели",   2,   2],
    "Жим гантелей стоя":                          ["Плечи",   "Гантели",   2,   2],
    "Жим Арнольда":                               ["Плечи",   "Гантели",   2,   2],
    "Разведение гантелей лежа":                   ["Грудь",   "Гантели",   2,   2],
    "Разведение рук с гантелями стоя":            ["Плечи",   "Гантели",   1,   1],
    "Подъем гантелей через стороны":              ["Плечи",   "Гантели",   1,   1],
    "Разведение рук в наклоне на заднюю дельту":   ["Плечи",   "Гантели",   1,   1],
    "Сведения в тренажере бабочка":               ["Грудь",   "Тренажёр",  5,   5],
    "Тяга вертикального блока (на широчайшие)":   ["Спина",   "Блок",      5,   5],
    "Тяга горизонтального блока":                 ["Спина",   "Блок",      5,   5],
    "Тяга гантели в наклоне":                      ["Спина",   "Гантели",   2,   2],
    "Румынская тяга":                             ["Ноги",    "Штанга",    2.5, 20],
    "Жим ногами":                                 ["Ноги",    "Тренажёр",  5,   5],
    "Сгибание ног в тренажере":                   ["Ноги",    "Тренажёр",  5,   5],
    "Выпады с гантелями":                          ["Ноги",    "Гантели",   2,   2],
    "Подъемы на носки стоя":                      ["Икры",    "Тренажёр",  5,   5],
    "Жим к низу в блочном тренажере":             ["Трицепс", "Блок",      5,   5],
    "Французский жим штанги лежа":                ["Трицепс", "EZ-штанга", 2.5, 10],
    "Французский жим штанги стоя":                ["Трицепс", "EZ-штанга", 2.5, 10],
    "Подъем штанги на бицепс стоя":               ["Бицепс",  "Штанга",    2.5, 20],
    "Подъем EZ-штанги на бицепс в скамье Скотта": ["Бицепс",  "EZ-штанга", 2.5, 10],
    "Подъем гантелей на бицепс стоя":             ["Бицепс",  "Гантели",   2,   2],
    "Подъем гантелей на бицепс сидя":             ["Бицепс",  "Гантели",   2,   2],
    "Подъем гантелей на бицепс в скамье Скотта":  ["Бицепс",  "Гантели",   2,   2],
    "Молоток":                                    ["Бицепс",  "Гантели",   2,   2],
    "Отжимания от брусьев":                       ["Трицепс", "Свой вес",  1.25, 0],
    "Подтягивания на перекладине":                ["Спина",   "Свой вес",  1.25, 0],
    "Скручивания на пресс":                       ["Пресс",   "Свой вес",  1.25, 0],
    "Подъем согнутых ног в висе":                 ["Пресс",   "Свой вес",  1.25, 0],
    "Подъем прямых ног в висе":                   ["Пресс",   "Свой вес",  1.25, 0],
}
BASE_LIFTS = ["Приседания со штангой", "Становая тяга", "Жим штанги лежа"]

program = json.load(open("source/program.json", encoding="utf-8"))
split_source = json.load(open("source/split.json", encoding="utf-8"))
technique = json.load(open("source/technique.json", encoding="utf-8"))

# Дни сплита описаны один раз, волна 5/3/1 подставляется по номеру недели.
# Главные движения идут блоками: три рабочих подхода с разным весом,
# проценты в блоках отсчитываются от рабочего максимума (90% разового), а не от разового.
TM = split_source.get("trainingMax", 0.90)
waves = split_source["waves"]
assert len(waves) == split_source["weeks"], "волн меньше, чем недель"

split = []
for week in range(1, split_source["weeks"] + 1):
    for day in split_source["days"]:
        for exercise in day["exercises"]:
            item = {"w": week, "d": day["d"], "n": exercise["n"]}
            if exercise.get("main"):
                blocks = waves[week - 1]
                top = max(b["p"] for b in blocks)
                # pmin/pmax остаются долей разового максимума: их читают гид,
                # расчёт отдыха и признак работы по процентам.
                item.update({"s": len(blocks), "r": blocks[-1]["r"], "b": blocks,
                             "tm": TM, "inc": split_source["increment"][exercise["n"]],
                             "pmin": round(TM * top, 4), "pmax": round(TM * top, 4)})
            else:
                item.update({k: v for k, v in exercise.items() if k != "n"})
                item.setdefault("pmin", None)
                item.setdefault("pmax", None)
                if week == split_source.get("deloadWeek"):
                    item["s"] = max(1, math.ceil(item["s"] / 2))
            split.append(item)

missing = sorted({p["n"] for p in program + split} - set(CATALOG))
assert not missing, "нет в справочнике: " + str(missing)
no_tech = sorted(set(CATALOG) - set(technique))
assert not no_tech, "нет описания техники: " + str(no_tech)

catalog = {n: {"grp": c[0], "eq": c[1], "step": c[2], "min": c[3]} for n, c in CATALOG.items()}

with open("data.js", "w", encoding="utf-8") as f:
    f.write("// Сгенерировано gen_data.py — не править вручную\n")
    f.write("const PROGRAMS = " + json.dumps({"fullbody": program, "split": split}, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("const PROGRAM_META = " + json.dumps({
        "fullbody": {"name": "Full Body", "short": "Full Body"},
        "split": {"name": "Сплит 5/3/1", "short": "5/3/1 · 3 дня"},
    }, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("const CATALOG = " + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("const INFO = " + json.dumps(technique, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("const BASE_LIFTS = " + json.dumps(BASE_LIFTS, ensure_ascii=False) + ";\n")
    f.write('let PROGRAM = PROGRAMS.fullbody;\n')
    f.write('let DAYS = ["Понедельник","Среда","Пятница"];\n')

print("упражнений Full Body:", len(program), "| Сплит:", len(split), "| в справочнике:", len(catalog),
      "| с описанием техники:", len(technique))

if os.path.exists("personal.json"):
    p = json.load(open("personal.json", encoding="utf-8"))
    starter = {
        "maxes": p.get("maxes", {}),
        "lastWeights": p.get("lastWeights", {}),
        "deload": p.get("deload", 0.20),
        "steps": {}, "log": {}, "cur": None,
    }
    json.dump(starter, open("starter-fullbody.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("стартовый файл собран:", len(starter["lastWeights"]), "прежних весов")
