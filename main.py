import telnetlib3
import re
import asyncio

# Регулярное выражение для извлечения MAC-адресов формата XX-XX-XX-XX-XX-XX
mac_pattern = re.compile(r"([0-9A-Fa-f]{2}[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2})")

async def get_mac_table(host, user, password, command):
    print(f"Подключаюсь к {host}:{23}")
    reader, writer = await telnetlib3.open_connection(host, port=23)
    print("Ожидаю приглашение login:")
    await reader.readuntil(b"login:")
    writer.write(user + "\n")
    print("Ввел имя пользователя\nОжидаю приглашение Password:")
    await reader.readuntil(b"Password:")
    writer.write(password + "\r\n")
    print(f"Ввел пароль\nВыполняю команду: {command}")
    output = await reader.readuntil(b"#")
    writer.write(command + "\n")
    output = ""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            break
        output += chunk
        if "--More--" in chunk:
            #print("Обнаружено --More--, отправляю пробел")
            writer.write(" \n")
        elif "#" in chunk:
            print("Обнаружен #, завершаю чтение")
            break
    writer.close()
    print("Соединение закрыто")
    mac_table = mac_pattern.findall(output)
    return mac_table

def validate_mac(mac):
    """Проверяет, соответствует ли MAC-адрес формату."""
    return bool(mac_pattern.match(mac))

def check_duplicates(mac_table):
    """Проверяет таблицу на дубликаты MAC-адресов."""
    seen = set()
    duplicates = set()
    for mac in mac_table:
        if mac in seen:
            duplicates.add(mac)
        else:
            seen.add(mac)
    return duplicates

def test_mac_table(mac_table):
    print("Проверка таблицы MAC-адресов...\n")

    print (f"Количество уникальных MAC-адресов: {len (mac_table) - len(check_duplicates(mac_table)) }\n")

    # Проверка формата
    print("Проверка формата MAC-адресов:")
    for mac in mac_table:
        if not validate_mac(mac):
            print(f"[ERROR] {mac} — некорректный MAC-адрес.\n")
    print()

    # Проверка на дубликаты
    duplicates = check_duplicates(mac_table)
    if duplicates:
        print(f"Найдены дубликаты MAC-адресов: {', '.join(duplicates)}")
    else:
        print("Дубликаты MAC-адресов не найдены.")
    print()

    # Дополнительная проверка: принадлежность к определённому производителю
    # (Пример: проверка по OUI — Organizationally Unique Identifier)
    """print("Проверка OUI (первые 3 байта MAC-адреса):")
    for mac in mac_table:
        if validate_mac(mac):
            oui = mac[:8].upper()  # Берём первые 3 байта
            print(f"MAC-адрес {mac} имеет OUI: {oui}")
    print()"""

# Пример таблицы MAC-адресов
async def main():
    HOST = '10.45.30.5'#input("Введите IP-адрес хоста (например, 192.168.0.1): ")  # IP-адрес устройства
    USER = 'admin'#input("Введите логин (например, admin): ")  # Имя пользователя
    PASSWORD = 'admin'#input("Введите пароль (например, admin): ")  # Пароль
    COMMAND = "show mac-address-table"

    mac_table = await get_mac_table(HOST, USER, PASSWORD, COMMAND)
    test_mac_table(mac_table)

if __name__ == "__main__":
    asyncio.run(main())