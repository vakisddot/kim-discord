import sqlite3

dbName = "KimDB.db"
db = sqlite3.connect(dbName)

sensPunctuations = ['.', ',', '-', '_', '<', '>', ':', ';', '"', "'", '|', '[', ']', '(', ')', '{', '}', '^', '*', ' ', '#', '%', '&']
sensDictionary = {
    # Special characters
    '!' : 'i',
    '1' : 'i',
    '@' : 'a',
    '4' : 'a',
    '0' : 'o',
    '3' : 'e',
    '€' : 'e',
    '5' : 's',
    '$' : 's',
    '9' : 'g',
    'æ' : 'a',
    'ø' : 'o',
    '⁏' : ';'
}
cyrillicDictionary = {
    '\u0430' : 'a',
    '\u0431' : 'b',
    '\u0432' : 'v',
    '\u0433' : 'g',
    '\u0434' : 'd',
    '\u0435' : 'e',
    '\u0436' : 'j',
    '\u0437' : 'z',
    '\u0438' : 'i',
    '\u0439' : 'i',
    '\u045D' : 'i',
    '\u043A' : 'k',
    '\u043B' : 'l',
    '\u043C' : 'm',
    '\u043D' : 'n',
    '\u043E' : 'o',
    '\u043F' : 'p',
    '\u0440' : 'r',
    '\u0441' : 's',
    '\u0442' : 't',
    '\u0443' : 'u',
    '\u0444' : 'f',
    '\u0445' : 'h',
    '\u0446' : 'c',
    '\u0447' : 'ch',
    '\u0448' : 'sh',
    '\u0449' : 'sht',
    '\u044A' : 'u',
    '\u044B' : 'y',
    '\u044C' : 'y',
    '\u044D' : 'e',
    '\u044E' : 'yu',
    '\u044F' : 'q'
}


# Mini-function that helps with organizing fetched data from SQL
def fetchStrings(cursor, strip=0):
    strings = [str(string) for string in cursor.fetchall()]
    return [string[2-strip:len(string)-3+strip] for string in strings]


def addNewServer(id, name, memberIds):
    # First checks if server is already in database
    curs = db.cursor()
    curs.execute("SELECT id FROM servers;")
    allServerIds = fetchStrings(curs, 1)

    if str(id) in allServerIds:
        print(f"Server is already in database ({id})")
        return
    
    # Inserts some default parameters into the database
    curs.execute("INSERT INTO servers (id, name) VALUES (?, ?);", (id, name))
    
    db.commit()
    curs.execute("INSERT INTO phrases (serverId, phrase) VALUES (?, ?);", (id, "$!%&"))
    
    db.commit()
    curs.execute("INSERT INTO descriptions (serverId, description) VALUES (?, ?)", (id, "just said"))
    
    db.commit()

    for memberId in memberIds:
        curs.execute("INSERT INTO users (id, serverId) VALUES (?, ?);", (memberId, id))
        db.commit()
    curs.close()