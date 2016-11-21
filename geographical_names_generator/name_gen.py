import json
import random

jsonFile = open('syllables.json')
jsonData = json.load(jsonFile)
lastSyllable = ""


def get_syllable(cat):
    global lastSyllable
    newRandSyllable = jsonData[cat][random.randint(0, len(jsonData[cat])-1)]
    while newRandSyllable == lastSyllable:
        newRandSyllable = jsonData[cat][random.randint(0, len(jsonData[cat])-1)]
    lastSyllable = newRandSyllable
    return newRandSyllable


def generate_name():
    cat = ""
    gen = ""
    # Generate first syllable
    catIndex = random.randint(0, 5)
    if catIndex == 0:
        cat = "anyfixes"
        gen = gen + get_syllable(cat)
    else:
        cat = "prefixes"
        gen = gen + get_syllable(cat)

    syllableNumber = random.randint(1, 3)
    for i in range(0, syllableNumber):
        gen += get_syllable("anyfixes")

    return gen

for i in range(10):
    print(generate_name())
