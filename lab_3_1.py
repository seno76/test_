import hashlib
import string
import random

# Генерация хэша по строке
def hash_function(value):
    return hashlib.md5(value.encode()).hexdigest()

# Генерация случайной последовательности для секретного ключа пользователя
def generate_random_key(min_length=10, max_length=20):
    length = random.randint(min_length, max_length)
    letters_and_digits = string.ascii_letters + string.digits
    random_key = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return random_key

# Применение хэш функции к строке N раз
def gen_hash(secret, N):
    for _ in range(N):
        secret = hash_function(secret)
    return secret

# Инициализация паролей сервером 
def initialize_passwords(N, filename):
    K = generate_random_key(min_length=16, max_length=32)
    W_list = [K]
    for _ in range(N):
        W_list.append(hash_function(W_list[-1]))
    W_list = W_list[::-1]
    with open(filename, 'w') as f:
        for W in W_list:
            f.write(W + '\n')
    print(f"Инициализация завершена. Список паролей сохранен в '{filename}'")
    return W_list[-1], W_list[0]

# Считывание паролей из файла
def read_passwords(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

# Запись измененной последовательности паролей
def update_password_file(filename, W_list):
    with open(filename, 'w') as f:
        for W in W_list:
            f.write(W + '\n')

# Проверка аутентификации на сервере
def authenticate_server(W_N, W_N_plus_1):
    print(f"Проверка пароля на сервере...")
    if hash_function(W_N) == W_N_plus_1:
        print(f"Аутентификация успешна: h(h(N) = {hash_function(W_N)} совпадает с W(N+1).")
        return True
    else:
        print(f"Аутентификация не удалась: W(N+1) не совпадает.")
        return False

# Высчитывание новых хэшей пользователем
def user_compute_password(N, file_secret):
    with open(file_secret, "r", encoding="UTF-8") as f:
        secret = f.readline()
    new_hash = gen_hash(secret, N - 1)
    return new_hash

# Удаление паролей из файла на сервере после его использования
def remove_used_password(filename):
    passwords = read_passwords(filename)
    updated_passwords = passwords[1:]
    update_password_file(filename, updated_passwords)
    return updated_passwords

# Вывод содержимого файла с паролями на экран
def print_current_passwords(filename):
    passwords = read_passwords(filename)
    print(f"Текущие одноразовые пароли в файле '{filename}':")
    for i, password in enumerate(passwords):
        print(f"W{len(passwords) - i}: {password}")

if __name__ == "__main__":

    filename = "passwords.txt"
    with open("last_hash.txt", "r", encoding="UTF-8") as f:
        W_last = f.readline()

    while True:
        print("\nМеню:")
        print("1. Инициализация одноразовых паролей")
        print("2. Просмотреть текущие одноразовые пароли")
        print("3. Создание хэша пользователя")
        print("4. Аутентификация пользователя")
        print("5. Выйти из программы")
        choice = input("Выберите действие (1-4): ")
        if choice == '1':
            
            N = int(input("Введите количество одноразовых паролей: ").strip())
            secret_key, W_last = initialize_passwords(N, filename)

            with open("last_hash.txt", "w", encoding="UTF-8") as f:
                f.write(str(W_last))
            print("Последний хэш записан на сервере в файле last_hash.txt")

            with open("number_passwords.txt", "w", encoding="UTF-8") as f:
                f.write(str(N))
            print("Номер текущего пароля сохранен в файл number_passwords.txr")

            with open("secret_key.txt", "w", encoding="UTF-8") as f:
                f.write(str(secret_key))
            print("Секретный ключ пользователя сохранен в файл secret_key.txt")
        
        elif choice == '2':
            # Показать текущие пароли
            print_current_passwords(filename)
        
        elif choice == '3':
            with open("number_passwords.txt", "r", encoding="UTF-8") as f:
                    N = int(f.readline())
            
            if N == 0:
                print("Необходимо сгенерировать новые временные пароли!!! (Шаг 1)")
            else:
                
                W_user = user_compute_password(N, "secret_key.txt")
                with open("hash_user.txt", "w", encoding="UTF-8") as f:
                    f.write(W_user)
                
                print(f"\nПользователь создал хэш: {W_user}")
                
        elif choice == "4":
                with open("hash_user.txt", "r", encoding="UTF-8") as f:
                    W_user = f.readline()
                
                print(f"\nПользователь отправил одноразовый пароль: {W_user}")
                
                if authenticate_server(W_user, W_last):
                    
                    print(f"Обновление последнего хэша: = {W_user}")
                    W_last = W_user
                    with open("last_hash.txt", "w", encoding="UTF-8") as f:
                        f.write(str(W_last))
                    
                    with open("number_passwords.txt", "w", encoding="UTF-8") as f:
                        f.write(str(N - 1))
                    
                    print("Последний хэш записан на сервере в файле last_hash.txt")
                    remove_used_password(filename)
                else:
                    print("Ошибка аутентификации.")
        elif choice == '5':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")