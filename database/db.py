"""
Database modul - SQLite konekcija i upiti.
Faza 2: puna funkcionalnost.

Tabele:
- prodavnice (id, naziv)
- proizvodi (id, naziv, jedinica_mere, zadnja_cena, prodavnica_id)
- liste (id, datum, prodavnica_id, ukupno, zatvorena)
- lista_stavke (id, lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici, total)
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_db_path():
    """
    U pravom instaliranom APK-u (napravljenom preko Buildozer-a), fajlovi
    aplikacije su u read-only delu, pa bazu treba cuvati u privatnom,
    upisivom direktorijumu aplikacije (android.storage).
    U Pydroid-u i na racunaru taj modul ne postoji, pa se koristi folder
    pored skripte (BASE_DIR) - to je vec provereno da radi.
    """
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "shopping.db")
    except ImportError:
        return os.path.join(BASE_DIR, "shopping.db")


DB_PATH = _get_db_path()

# Početnih 19 artikala kojima se puni baza pri prvom pokretanju
SEED_PROIZVODI = [
    ("Hleb", "kom", 80.00),
    ("Mleko", "l", 110.00),
    ("Jaja (10kom)", "kom", 250.00),
    ("Brasno", "kg", 95.00),
    ("Secer", "kg", 115.00),
    ("Ulje jestivo", "l", 220.00),
    ("Pirinac", "kg", 180.00),
    ("Testenina", "kom", 90.00),
    ("Sir", "kg", 850.00),
    ("Kajmak", "kg", 900.00),
    ("Piletina (belo meso)", "kg", 650.00),
    ("Krompir", "kg", 70.00),
    ("Luk crni", "kg", 90.00),
    ("Paradajz", "kg", 160.00),
    ("Jogurt", "kom", 75.00),
    ("Kafa", "kg", 1200.00),
    ("Cokolada", "kom", 180.00),
    ("Deterdzent za sudove", "kom", 280.00),
    ("Toalet papir", "kom", 350.00),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS prodavnice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT UNIQUE NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS proizvodi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT UNIQUE NOT NULL,
        jedinica_mere TEXT NOT NULL,
        zadnja_cena REAL DEFAULT 0,
        prodavnica_id INTEGER,
        FOREIGN KEY (prodavnica_id) REFERENCES prodavnice(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS liste (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        prodavnica_id INTEGER,
        ukupno REAL DEFAULT 0,
        zatvorena INTEGER DEFAULT 0,
        FOREIGN KEY (prodavnica_id) REFERENCES prodavnice(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS lista_stavke (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lista_id INTEGER NOT NULL,
        proizvod_id INTEGER NOT NULL,
        naziv TEXT NOT NULL,
        kolicina REAL NOT NULL,
        cena_po_jedinici REAL NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (lista_id) REFERENCES liste(id),
        FOREIGN KEY (proizvod_id) REFERENCES proizvodi(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS podesavanja (
        kljuc TEXT PRIMARY KEY,
        vrednost TEXT
    )""")
    conn.commit()

    c.execute("SELECT COUNT(*) FROM proizvodi")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO proizvodi (naziv, jedinica_mere, zadnja_cena, prodavnica_id) "
            "VALUES (?, ?, ?, NULL)",
            SEED_PROIZVODI,
        )
        conn.commit()
    conn.close()


# ---------- Prodavnice ----------

def get_prodavnice():
    conn = get_connection()
    rows = conn.execute("SELECT id, naziv FROM prodavnice ORDER BY naziv").fetchall()
    conn.close()
    return rows


def add_prodavnica(naziv):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM prodavnice WHERE LOWER(naziv) = LOWER(?)", (naziv,))
    row = c.fetchone()
    if row:
        conn.close()
        return row[0]
    c.execute("INSERT INTO prodavnice (naziv) VALUES (?)", (naziv,))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


# ---------- Proizvodi ----------

def search_proizvodi(query, limit=8):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, naziv, jedinica_mere, zadnja_cena FROM proizvodi "
        "WHERE LOWER(naziv) LIKE ? ORDER BY naziv LIMIT ?",
        (f"%{query.lower()}%", limit),
    ).fetchall()
    conn.close()
    return rows


def get_proizvodi_sa_prodavnicom():
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.id, p.naziv, p.jedinica_mere, p.zadnja_cena,
                  COALESCE(pr.naziv, '-')
           FROM proizvodi p
           LEFT JOIN prodavnice pr ON p.prodavnica_id = pr.id
           ORDER BY p.naziv"""
    ).fetchall()
    conn.close()
    return rows


def add_or_update_proizvod(naziv, jedinica_mere, cena, prodavnica_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM proizvodi WHERE LOWER(naziv) = LOWER(?)", (naziv,))
    row = c.fetchone()
    if row:
        pid = row[0]
        c.execute(
            "UPDATE proizvodi SET zadnja_cena = ?, jedinica_mere = ?, "
            "prodavnica_id = COALESCE(?, prodavnica_id) WHERE id = ?",
            (cena, jedinica_mere, prodavnica_id, pid),
        )
    else:
        c.execute(
            "INSERT INTO proizvodi (naziv, jedinica_mere, zadnja_cena, prodavnica_id) "
            "VALUES (?, ?, ?, ?)",
            (naziv, jedinica_mere, cena, prodavnica_id),
        )
        pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def update_proizvod(proizvod_id, naziv, jedinica_mere, cena):
    """Rucna izmena naziva/jedinice/cene proizvoda iz ekrana Baze (trajno)."""
    conn = get_connection()
    c = conn.cursor()
    # Provera da novo ime ne kosi sa nekim DRUGIM proizvodom (case-insensitive)
    c.execute(
        "SELECT id FROM proizvodi WHERE LOWER(naziv) = LOWER(?) AND id != ?",
        (naziv, proizvod_id),
    )
    if c.fetchone():
        conn.close()
        return False
    c.execute(
        "UPDATE proizvodi SET naziv = ?, jedinica_mere = ?, zadnja_cena = ? WHERE id = ?",
        (naziv, jedinica_mere, cena, proizvod_id),
    )
    conn.commit()
    conn.close()
    return True


def delete_proizvod(proizvod_id):
    """
    Brise proizvod iz baze trajno. Vraca True ako je uspelo, False ako je
    proizvod koriscen u nekoj (i zatvorenoj i otvorenoj) listi - u tom
    slucaju se ne brise, da se ne pokvari istorija prethodnih kupovina.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM lista_stavke WHERE proizvod_id = ?", (proizvod_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return False
    c.execute("DELETE FROM proizvodi WHERE id = ?", (proizvod_id,))
    conn.commit()
    conn.close()
    return True


# ---------- Liste za kupovinu ----------

def create_lista(prodavnica_id):
    conn = get_connection()
    c = conn.cursor()
    datum = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute(
        "INSERT INTO liste (datum, prodavnica_id, ukupno, zatvorena) VALUES (?, ?, 0, 0)",
        (datum, prodavnica_id),
    )
    conn.commit()
    lista_id = c.lastrowid
    conn.close()
    return lista_id


def add_stavka(lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici):
    total = kolicina * cena_po_jedinici
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO lista_stavke (lista_id, proizvod_id, naziv, kolicina, "
        "cena_po_jedinici, total) VALUES (?, ?, ?, ?, ?, ?)",
        (lista_id, proizvod_id, naziv, kolicina, cena_po_jedinici, total),
    )
    conn.commit()
    conn.close()
    return total


def close_lista(lista_id, ukupno):
    conn = get_connection()
    conn.execute(
        "UPDATE liste SET ukupno = ?, zatvorena = 1 WHERE id = ?",
        (ukupno, lista_id),
    )
    conn.commit()
    conn.close()


def get_istorija():
    conn = get_connection()
    rows = conn.execute(
        """SELECT l.datum, COALESCE(pr.naziv, 'Bez prodavnice'), l.ukupno
           FROM liste l
           LEFT JOIN prodavnice pr ON l.prodavnica_id = pr.id
           WHERE l.zatvorena = 1
           ORDER BY l.id DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_prodavnice_sa_istorijom():
    """Prodavnice koje imaju bar jednu zatvorenu listu, sa ukupnim brojem racuna."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT pr.id, pr.naziv, COUNT(l.id)
           FROM liste l
           JOIN prodavnice pr ON l.prodavnica_id = pr.id
           WHERE l.zatvorena = 1
           GROUP BY pr.id, pr.naziv
           ORDER BY pr.naziv"""
    ).fetchall()
    conn.close()
    return rows


def get_liste_za_prodavnicu(prodavnica_id):
    """Svi zatvoreni racuni za jednu prodavnicu, najnoviji prvo."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, datum, ukupno FROM liste
           WHERE prodavnica_id = ? AND zatvorena = 1
           ORDER BY id DESC""",
        (prodavnica_id,),
    ).fetchall()
    conn.close()
    return rows


def get_lista_stavke(lista_id):
    """Stavke (namirnice) jednog konkretnog racuna."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT naziv, kolicina, cena_po_jedinici, total
           FROM lista_stavke WHERE lista_id = ? ORDER BY id""",
        (lista_id,),
    ).fetchall()
    conn.close()
    return rows


def delete_lista(lista_id):
    """Trajno brise jedan racun (i njegove stavke) iz istorije."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM lista_stavke WHERE lista_id = ?", (lista_id,))
    c.execute("DELETE FROM liste WHERE id = ?", (lista_id,))
    conn.commit()
    conn.close()


# ---------- Podesavanja ----------

def get_setting(kljuc, default=None):
    conn = get_connection()
    row = conn.execute(
        "SELECT vrednost FROM podesavanja WHERE kljuc = ?", (kljuc,)
    ).fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(kljuc, vrednost):
    conn = get_connection()
    conn.execute(
        "INSERT INTO podesavanja (kljuc, vrednost) VALUES (?, ?) "
        "ON CONFLICT(kljuc) DO UPDATE SET vrednost = excluded.vrednost",
        (kljuc, vrednost),
    )
    conn.commit()
    conn.close()
