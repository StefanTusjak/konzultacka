import mysql.connector
import pytest

# 🔗 Připojení k databázi
def get_connection():
    """
    Vytvoří spojení s MySQL databází.
    """
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="test_db"
    )
    return connection

# 🗄️ Vytvoření tabulky
def create_table(connection, test_mode=False):
    """
    Vytvoří tabulku uživatelů. Pokud `test_mode=True`, vytvoří testovací tabulku `users_test`.
    """
    table_name = "users_test" if test_mode else "users"
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            jmeno VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
    """)
    connection.commit()
    cursor.close()

# ➕ Přidání uživatele
def add_user(connection, jmeno, email, test_mode=False):
    """
    Přidá uživatele do databáze.
    Pokud `test_mode=True`, pracuje s `users_test`.
    """
    table_name = "users_test" if test_mode else "users"
    cursor = connection.cursor()
    try:
        cursor.execute(f"INSERT INTO {table_name} (jmeno, email) VALUES (%s, %s)", (jmeno, email))
        connection.commit()
        print(f"✅ Uživatel {jmeno} přidán do tabulky `{table_name}`.")
    except mysql.connector.Error as e:
        print(f"⚠️ Chyba: {e}")
    cursor.close()

# 🔍 Načtení uživatele podle ID
def get_user(connection, user_id, test_mode=False):
    """
    Načte uživatele z databáze podle ID.
    """
    table_name = "users_test" if test_mode else "users"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

# 📋 Získání všech uživatelů
def get_all_users(connection, test_mode=False):
    """
    Získá všechny uživatele z databáze.
    """
    table_name = "users_test" if test_mode else "users"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    users = cursor.fetchall()
    cursor.close()
    return users

# 🗑️ Smazání uživatele podle ID
def delete_user(connection, user_id, test_mode=False):
    """
    Smaže uživatele z databáze podle ID.
    """
    table_name = "users_test" if test_mode else "users"
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (user_id,))
    connection.commit()
    cursor.close()
    print(f"🗑️ Uživatel s ID {user_id} smazán z `{table_name}`.")

# 🧪 Pytest fixture pro testovací databázi
@pytest.fixture(scope="module")
def connection():
    """
    Fixture pro testovací databázové spojení.
    Používá testovací tabulku `users_test`, aby testy neovlivnily `users`.
    """
    connection = get_connection()
    create_table(connection, test_mode=True)
    yield connection

    # ✅ Po testech odstraníme pouze `users_test`
    cursor = connection.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS users_test")
        connection.commit()
    except mysql.connector.Error as e:
        print(f"⚠️ Chyba při mazání testovací tabulky: {e}")
    cursor.close()
    connection.close()

# 🧪 Testy Pytestem
def test_add_user(connection):
    """ Test přidání uživatele (test_mode=True) """
    add_user(connection, "Test User", "test@example.com", test_mode=True)
    user = get_user(connection, 1, test_mode=True)
    print("\n📋 Data v testovací databázi po přidání uživatele:")
    print(f"👤 ID: {user['id']}, Jméno: {user['jmeno']}, Email: {user['email']}")
    assert user["jmeno"] == "Test User"
    assert user["email"] == "test@example.com"

def test_get_non_existent_user(connection):
    """ Test načtení neexistujícího uživatele (test_mode=True) """
    user = get_user(connection, 99999, test_mode=True)
    print("\n🔍 Pokus o načtení neexistujícího uživatele:")
    print(f"Výsledek: {user}")
    assert user is None

def test_delete_user(connection):
    """ Test smazání uživatele (test_mode=True) """
    add_user(connection, "Delete User", "delete@example.com", test_mode=True)
    delete_user(connection, 2, test_mode=True)
    user_after_delete = get_user(connection, 2, test_mode=True)
    assert user_after_delete is None

def test_unique_email_constraint(connection):
    """ Test unikátnosti e-mailu (test_mode=True) """
    add_user(connection, "User A", "unique@example.com", test_mode=True)
    try:
        add_user(connection, "User B", "unique@example.com", test_mode=True)
    except mysql.connector.Error as e:
        assert "Duplicate entry" in str(e)

def test_list_all_users(connection):
    """ Test zobrazení všech uživatelů v testovací databázi """
    users = get_all_users(connection, test_mode=True)
    print("\n📋 Všichni uživatelé v testovací databázi:")
    for user in users:
        print(f"👤 ID: {user['id']}, Jméno: {user['jmeno']}, Email: {user['email']}")
    assert len(users) > 0

# 📌 Možnosti testů pro výběr v konzoli
TESTS = {
    "1": "test_add_user",
    "2": "test_get_non_existent_user",
    "3": "test_delete_user",
    "4": "test_unique_email_constraint",
    "5": "test_list_all_users",
    "6": "Spustit všechny testy"
}

# 🏃 Manuální testování v konzoli
if __name__ == "__main__":
    conn = get_connection()
    create_table(conn)

    while True:
        print("\n📋 Menu:")
        print("1️⃣ Přidat uživatele")
        print("2️⃣ Zobrazit uživatele podle ID")
        print("3️⃣ Zobrazit všechny uživatele")
        print("4️⃣ Smazat uživatele")
        print("5️⃣ Spustit testy")
        print("6️⃣ Konec")

        choice = input("Vyber možnost: ")

        if choice == "1":
            jmeno = input("Zadej jméno: ")
            email = input("Zadej e-mail: ")
            add_user(conn, jmeno, email)

        elif choice == "2":
            user_id = input("Zadej ID uživatele: ")
            user = get_user(conn, int(user_id))
            if user:
                print(f"👤 Uživatel: {user['jmeno']} | Email: {user['email']}")
            else:
                print("❌ Uživatel nenalezen.")

        elif choice == "3":
            users = get_all_users(conn)
            for user in users:
                print(f"👤 ID: {user['id']}, Jméno: {user['jmeno']}, Email: {user['email']}")

        elif choice == "4":
            user_id = input("Zadej ID uživatele k odstranění: ")
            delete_user(conn, int(user_id))

        elif choice == "5":
            print("\n📌 Možnosti testů:")
            for key, value in TESTS.items():
                print(f"{key}️⃣ {value}")
            test_choice = input("Vyber test k provedení: ")
            if test_choice in TESTS:
                pytest.main(["-s", "-v", __file__, "-k", TESTS[test_choice]])
                input("\n✅ Test dokončen. Stiskni Enter pro návrat do menu.")

        elif choice == "6":
            print("👋 Ukončuji program.")
            conn.close()
            break
