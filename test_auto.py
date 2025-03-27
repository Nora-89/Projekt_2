import pytest
import mysql.connector

@pytest.fixture(scope="module")
def db_spojeni():
    spojeni = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="20180109",
        database="test_ukoly_db"
    )
    
    cursor = spojeni.cursor()

    # Vytvoření testovací tabulky
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(50) NOT NULL,
            popis VARCHAR(100) NOT NULL,
            stav ENUM('Nezahajeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahajeno',
            datum_vytvoreni DATETIME DEFAULT NOW()
        );
    """)
    spojeni.commit()

    # Smazání testovacích dat
    cursor.execute("DELETE FROM test_ukoly;")
    spojeni.commit()

    yield spojeni  

    spojeni.close()  


@pytest.fixture
def db_cursor(db_spojeni):
    cursor = db_spojeni.cursor()
    yield cursor  
    db_spojeni.rollback()  
    cursor.close()


# Pozitivní test přidání úkolu
def test_pridat_ukol(db_cursor):
    db_cursor.execute(
        "INSERT INTO test_ukoly (nazev, popis, stav) VALUES (%s, %s, %s);",
        ('uklidit', 'dětský pokoj', 'Nezahajeno')
    )

    # Ověření, zda úkol existuje
    db_cursor.execute("SELECT * FROM test_ukoly WHERE nazev = %s;", ('uklidit',))
    vysledek = db_cursor.fetchone()

    assert vysledek is not None, "Úkol nebyl přidán správně!"

# Negativní test přidání úkolu
def test_chybny_ukol(db_cursor):
    """Ověří, že nelze vložit úkol s prázdným názvem nebo popisem."""
    with pytest.raises(mysql.connector.Error):
        db_cursor.execute(
            "INSERT INTO test_ukoly (nazev, popis, stav) VALUES (%s, %s, %s);",
            (None, "Uklidit kuchyni", "Nezahajeno")  # Prázdný název (NULL)
        )
    
    with pytest.raises(mysql.connector.Error):
        db_cursor.execute(
            "INSERT INTO test_ukoly (nazev, popis, stav) VALUES (%s, %s, %s);",
        ("Úklid kuchyň", None, "Nezahajeno")  # Prázdný popis (NULL)
        )

# Pozitivní test aktualizace úkolu
def test_aktualizovat_ukol(db_cursor):
    db_cursor.execute(
        "INSERT INTO test_ukoly (nazev, popis, stav) VALUES (%s, %s, %s);",
        ("Uklidit koupelnu", "umyvadlo a sprcha", "Nezahajeno")
    )

    db_cursor.execute("SELECT id FROM test_ukoly WHERE nazev = %s;", ("Uklidit koupelnu",))
    id_ukolu = db_cursor.fetchone()[0]

    
    db_cursor.execute("UPDATE test_ukoly SET stav = %s WHERE id = %s;", ("Hotovo", id_ukolu))

    
    db_cursor.execute("SELECT stav FROM test_ukoly WHERE id = %s;", (id_ukolu,))
    vysledek = db_cursor.fetchone()[0]

    assert vysledek == "Hotovo", "Stav úkolu se neaktualizoval správně!"

    
    # Negativní test aktualizace úkolu
def test_aktualizovat_neexistujici_ukol(db_cursor):
    db_cursor.execute("UPDATE test_ukoly SET stav = %s WHERE id = %s;", ("Hotovo", 9999))


    assert db_cursor.rowcount == 0, "Neexistující úkol by neměl být aktualizován!"



# Pozitivní test odstranění úkolu
def test_odstranit_ukol(db_cursor):
    db_cursor.execute(
        "INSERT INTO test_ukoly (nazev, popis, stav) VALUES (%s, %s, %s);",
        ("Umýt wc", "celé WC", "Nezahajeno")
    )

    db_cursor.execute("SELECT id FROM test_ukoly WHERE nazev = %s;", ("Umýt WC",))
    id_ukolu = db_cursor.fetchone()[0]

    db_cursor.execute("DELETE FROM test_ukoly WHERE id = %s;", (id_ukolu,))

    db_cursor.execute("SELECT * FROM test_ukoly WHERE id = %s;", (id_ukolu,))
    vysledek = db_cursor.fetchone()

    assert vysledek is None, "Úkol nebyl odstraněn správně!"


# negativní test odstranění úkolu
def test_odstranit_neexistujici_ukol(db_cursor):
    db_cursor.execute("DELETE FROM test_ukoly WHERE id = %s;", (9999,))

    assert db_cursor.rowcount == 0, "Neexistující úkol by neměl být odstraněn!"
