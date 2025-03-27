import mysql.connector

# připojení databáze
def pripojeni_db():
    try:
        spojeni = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="20180109",
            database = "ukoly_db"
        )
        if spojeni.is_connected():
            print('Připojení k databázi bylo úspěšné')
            return spojeni
    except mysql.connector.Error as err:
        print(f"Chyba : {err}")
        return None
    spojeni.close

pripojeni_db()


# vytvoření tabulky
def vytvoreni_tabulky():
     spojeni = pripojeni_db()
     if spojeni:
          cursor = spojeni.cursor()
     try:
        cursor.execute ("""
                        CREATE TABLE IF NOT EXISTS ukoly(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nazev VARCHAR (50) NOT NULL,
                        popis VARCHAR (100) NOT NULL,
                        stav ENUM('Nezahajeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
                        datum_vytvoreni DATETIME DEFAULT NOW()
                        );
""")
        
        print("Tabulka ukoly vytvořena, (pokud neexistovala).")
     except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}")
     finally:
         cursor.close()
         spojeni.close()

vytvoreni_tabulky()
          


# ověření tabulky
def overeni_tabulky():
        spojeni=pripojeni_db()
        if spojeni:
            cursor = spojeni.cursor()
            cursor.execute ("SHOW TABLES;")
            tabulky=cursor.fetchall()
            print('Seznam tabulek v databázi:')
            for tabulka in tabulky:
                print (tabulka [0])
                cursor.close()
                spojeni.close()
                
overeni_tabulky()


#1. přidat úkol
def pridat_ukol():
    spojeni = pripojeni_db()
    if not spojeni:
        return
    
    cursor = spojeni.cursor()
    print("--- Přidání nového úkolu ---")

    #název a popis úkolu
    nazev= input(" Zadejte název úkolu :").strip()
    while not nazev:
        print(" Název nesmí být prázdný!")
        nazev = input("Zadejte název úkolu :").strip()
    
    popis= input(" Zadejte popis úkolu :").strip()
    while not popis:
        print(" Popis nesmí být prázdný!")
        popis = input("Zadejte popis úkolu :").strip()

    # výchozí stav úkolu
    stav = "Nezahajeno"

    # vložení úkolu do databáze
    sql= """INSERT INTO ukoly (nazev, popis, stav, datum_vytvoreni) VALUES (%s, %s, %s, NOW())"""
    cursor.execute(sql, (nazev,popis, stav))
    spojeni.commit()
    
    print( f"Úkol '{nazev}' byl přidán.")

    # zavřít spojení
    cursor.close()
    spojeni.close()



#2. zobrazení úkolů
from datetime import datetime

def zobrazit_ukol():
    spojeni = pripojeni_db()
    if not spojeni:
          print('Nepodařilo se připojit k databázi.')
          return
    
    try:
        cursor = spojeni.cursor()
        sql= "SELECT id, nazev, popis, datum_vytvoreni FROM ukoly WHERE stav in (%s, %s) "
        values= ('Nezahajeno', 'Probíhá')
        cursor.execute(sql, values)

        vysledky = cursor.fetchall()

        if not vysledky:
            print('Žádné úkoly nebyly nalezeny.')
        else:
            for row in vysledky:
                id_ukolu, nazev, popis, datum_vytvoreni =row
                datum_format= datum_vytvoreni.strftime("%d.%m.%Y %H:%M:%S")if isinstance(datum_vytvoreni, datetime) else datum_vytvoreni
                print(f"{id_ukolu}: {nazev}- {popis} (vytvořeno: {datum_format})")

    except Exception as e:
        print(f"Chyba při načítání úkolů: {e}")

    finally:
        cursor.close()
        spojeni.close()

    
    

#3. aktualizace úkolů
def aktualizovat_ukol():
    spojeni = pripojeni_db()
    if not spojeni:
        return
    
    cursor = spojeni.cursor()

    # Zobrazení seznamu úkolů
    cursor.execute("SELECT id, nazev, stav FROM ukoly")
    ukoly = cursor.fetchall()

    if not ukoly:
        print("Nejsou žádné úkoly k aktualizaci.")
        cursor.close()
        spojeni.close()
        return
    
    print("\n--- Seznam úkolů ---")
    for ukol in ukoly:
        print(f"{ukol[0]}: {ukol[1]} (Stav: {ukol[2]})")

    # Výběr ID úkolu k aktualizaci
    while True:
        try:
            id_ukolu = int(input("\nZadejte ID úkolu, který chcete aktualizovat: "))
            cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
            if cursor.fetchone():
                break
            else:
                print("Chyba: Úkol s tímto ID neexistuje, zkuste to znovu.")
        except ValueError:
            print("Chyba: Zadejte platné číslo.")

    # Výběr nového stavu
    moznosti_stavu = ["Probíhá", "Hotovo"]
    while True:
        print("\nMožnosti stavu:")
        for i, stav in enumerate(moznosti_stavu, 1):
            print(f"{i}. {stav}")
        
        volba = input("Vyberte nový stav (1-2): ").strip()
        if volba in ["1", "2"]:
            novy_stav = moznosti_stavu[int(volba) - 1]
            break
        else:
            print("Neplatná volba, zkuste to znovu.")

    # Aktualizace úkolu v databázi
    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
    spojeni.commit()
    
    print(f"Úkol ID {id_ukolu} byl aktualizován na stav: {novy_stav}")

    cursor.close()
    spojeni.close()


#4. odstranění úkolu
def odstranit_ukol():
    spojeni = pripojeni_db()
    if not spojeni:
        return
    
    cursor = spojeni.cursor()

    # Zobrazení seznamu úkolů
    cursor.execute("SELECT id, nazev FROM ukoly")
    ukoly = cursor.fetchall()

    if not ukoly:
        print("Nejsou žádné úkoly k odstranění.")
        cursor.close()
        spojeni.close()
        return

    print("\n--- Seznam úkolů ---")
    for ukol in ukoly:
        print(f"{ukol[0]}: {ukol[1]}")

    # Výběr ID úkolu k odstranění
    while True:
        try:
            id_ukolu = int(input("\nZadejte ID úkolu, který chcete odstranit: "))
            cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
            if cursor.fetchone():
                break
            else:
                print("Chyba: Úkol s tímto ID neexistuje, zkuste to znovu.")
        except ValueError:
            print("Chyba: Zadejte platné číslo.")

    # Potvrzení odstranění
    potvrzeni = input(f"Opravdu chcete odstranit úkol ID {id_ukolu}? (ano/ne): ").strip().lower()
    if potvrzeni == "ano":
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        spojeni.commit()
        print(f"Úkol ID {id_ukolu} byl odstraněn.")
    else:
        print("Odstranění zrušeno.")

    cursor.close()


# hlavní menu
def hlavni_menu():
    while True:
        print("--- Hlavní nabídka ---")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("Vyberte možnost (1-5):")

        if volba == "1":
            pridat_ukol()

        elif volba == "2":
            zobrazit_ukol()

        elif volba == "3":
            aktualizovat_ukol()

        elif volba == "4":
            odstranit_ukol()

        elif volba == "5":
            print("Ukončuji program...")
            break
        else:
            print("neplatná volba, zkuste to znovu.")


if __name__== "__main__":
    hlavni_menu()
