import telnetlib3
import re
import asyncio

# Регулярное выражение MAC-адресов формата XX-XX-XX-XX-XX-XX
mac_pattern = re.compile(r"[0-9a-f]{2}(?:[.:-][0-9a-f]{2}){5}")#[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}")

mac_count_template = """\nMAC-address count:
Total   = {0}
Static  = {1}
Unicast = {2}
Hidden  = {3}
"""

async def get_mac_table(reader, writer): #, user, password, command):
    print("Выполняю команду: show mac-address-table\n")
    writer.write("show mac-address-table\n")
    output = ""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            break
        output += chunk
        if "--More--" in chunk:
            writer.write(" \n")
        elif "#" in chunk:
            print("Обнаружен #, завершаю чтение")
            break
    writer.close()
    print("Соединение закрыто")
    mac_table = mac_pattern.findall(output)
    return mac_table

async def get_mac_count(reader, writer):
    print("Выполняю команду: show mac-address-table count\n")
    writer.write("show mac-address-table count\n")
    output = await reader.readuntil(b"#")
    current_entries_match = re.search(
        r"Current entries have been created in the system:\s*"
        r"Total\s+Filter Entry Number is: (\d+)\s*"
        r"Static\s+Filter Entry Number is: (\d+)\s*"
        r"Unicast\s+Filter Entry Number is: (\d+)\s*"
        r"Hidden\s+Filter Entry Number is: (\d+)",
        output.decode("utf-8")
    )
    mac_count = [int(current_entries_match.group(i)) for i in range(1, 5)]
    writer.close()
    print("Соединение закрыто")
    return mac_count


def validate_mac(mac):
    return bool(mac_pattern.match(mac))

def check_duplicates(mac_table):
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
    print(f"Количество уникальных MAC-адресов: {len(mac_table) - len(check_duplicates(mac_table))}\n")
    print("Проверка формата MAC-адресов:")
    for mac in mac_table:
        if not validate_mac(mac):
            print(f"[ERROR] {mac} — некорректный MAC-адрес.\n")
    print()
    duplicates = check_duplicates(mac_table)
    if duplicates:
        print(f"Найдены дубликаты MAC-адресов: {', '.join(duplicates)}")
    else:
        print("Дубликаты MAC-адресов не найдены.")
    print()


async def main():
    HOST = input("Введите IP-адрес хоста: ") #'10.45.30.5' #
    USER = input("Введите логин: ")  #'admin' #
    PASSWORD = input("Введите пароль: ")  #'admin' #
    COMMAND = input("Выберите команду:\n1 - show mac-address-table\n2 - show mac-address-table count\nВвод: ")  #"show mac-address-table count" #
    print(f"Подключаюсь к {HOST}:{23}")
    reader, writer = await telnetlib3.open_connection(HOST, port=23)
    print("Ожидаю приглашение \"login:\"")
    await reader.readuntil(b"login:")
    writer.write(USER + "\n")
    print("Ввел имя пользователя\nОжидаю приглашение \"Password:\"")
    await reader.readuntil(b"Password:")
    writer.write(PASSWORD + "\n")
    print("Ввел пароль\nУстанавливаю terminal length 0")
    writer.write("terminal length 0\n")
    await reader.readuntil(b"#")
    if COMMAND == "1":
        mac_table = await get_mac_table(reader, writer)
        for mac in mac_table:
            print(f"MAC-адрес №{mac_table.index(mac)+1}: {mac}")
    elif COMMAND == "2":
        mac_count = await get_mac_count(reader, writer)
        print(mac_count_template.format(*mac_count))

    #test_mac_table(mac_table)

if __name__ == "__main__":
    asyncio.run(main())
