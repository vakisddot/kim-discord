import unicodedata
from random import randint
import config


def createCharacterMap(MSG, WORDS):
    # A character map takes a string input, checks whether certain words are in the string and returns a list of indexes
    # that show exactly where the letters of the words are
    characterMap = []
    strippedMsg = ""

    a = sensitive(MSG, returnIndexes=True)
    strippedMsg = a[0]
    strippedIndexes = a[1]

    for i, letter in enumerate(MSG):
        if i in strippedIndexes:
            characterMap.append("SKIP")
        else:
            characterMap.append(False)

    # These are the indexes of the letters in the stripped MSG that have been detected to be bad
    badIndexes = []
    for word in WORDS:
        for i in range(len(strippedMsg) - 1):
                if strippedMsg[i: i + len(word)] == word:
                    for j in range(len(word)):
                        badIndexes.append(i + j)

    currentIndexInStrippedSentence = 0
    previousLetterWasBad = False
    
    for i in range(len(characterMap)):
        if characterMap[i] == "SKIP":
            if previousLetterWasBad:
                characterMap[i] = True
            continue

        if currentIndexInStrippedSentence in badIndexes:
            characterMap[i] = True
            previousLetterWasBad = True

        else:
            previousLetterWasBad = False

        currentIndexInStrippedSentence += 1

    return characterMap
        

def createDesc(AUTHOR, DESC):
    dSplit = DESC.split()
    hasA = False
    authorName = "**" + str(AUTHOR) + "**"

    for i, word in enumerate(dSplit):
        if '@' in word:
            dSplit[i] = word.replace('@', authorName)
            hasA = True
        if i == len(dSplit) - 1:
            if not hasA:
                dSplit.insert(0, authorName)
            return ' '.join(dSplit) + ":\n"


def createBotMessage(MESSAGE, INDEXMAP):
    newMessage = ""
    isCensored = False

    for i in range(len(MESSAGE)):
        if config.spoilerMode == 1:
            if INDEXMAP[i] == True and not isCensored:
                newMessage += "||"
                isCensored = True
            elif (INDEXMAP[i] == False or INDEXMAP[i] == "SKIP") and isCensored:
                newMessage += "||"
                isCensored = False
            newMessage += MESSAGE[i]
            if i == len(MESSAGE) - 1 and isCensored:
                newMessage += "||"
                isCensored = False
        else:
            if INDEXMAP[i] == True and not isCensored:
                newMessage += "__" + config.phrases[randint(0, len(config.phrases) - 1)] + "__"
                isCensored = True
            elif (INDEXMAP[i] == False or INDEXMAP[i] == "SKIP") and isCensored:
                isCensored = False
            elif not isCensored:
                newMessage += MESSAGE[i]
            if i == len(MESSAGE) - 1 and isCensored:
                isCensored = False

    return newMessage


def cyrillicToLatin(WORD):
    newWord = ""
    for i in WORD:
        if i in config.cyrillicDictionary:
            newWord += config.cyrillicDictionary[i]
        elif i in config.sensDictionary:
            newWord += config.sensDictionary[i]
        else:
            newWord += i
    return newWord


def sensitive(WORD, returnIndexes=False):
    # This method converts words from "L33T" speech to regular. For instance (ex.: H3Ll0 -> hello)
    newWord = []

    # This list contains the indexes of all letters that were stripped
    strippedList = []

    previousLetter = ''
    letters1 = cyrillicToLatin(WORD.lower())
    letters = list(unicodedata.normalize('NFKD', letters1).encode('ascii', 'ignore').decode('ascii'))

    for i, letter in enumerate(letters):
        # This checks if the letter is a punctuation
        if letter in config.sensPunctuations:
            strippedList.append(i)
            continue

        if letter in config.sensDictionary:
            letter = config.sensDictionary[letter]

        newWord.append(letter)

        # This checks if the current letter is the same as the previous one and removes it to prevent letter spamming
        if len(newWord) > 0:
            if newWord[-1] == previousLetter:
                newWord.pop(-1)
                strippedList.append(i)
            else:
                previousLetter = newWord[-1]

    if returnIndexes:
        return ''.join(newWord), strippedList
    else:
        return ''.join(newWord)
