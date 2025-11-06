import socket
import json
from system_info import get_system_info

def start_server():
    """Запуск сервера для сбора системной информации"""
    host = 'localhost'
    port = 12345
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"✅ Сервер запущен на {host}:{port}")
            print("Ожидание подключений...")
            
            while True:
                conn, addr = server_socket.accept()
                print(f"🔗 Подключение от {addr}")
                
                try:
                    # Получаем системную информацию
                    system_data = get_system_info()
                    # Отправляем данные в формате JSON
                    conn.send(json.dumps(system_data).encode('utf-8'))
                    print("📊 Данные отправлены клиенту")
                except Exception as e:
                    error_data = {"error": str(e)}
                    conn.send(json.dumps(error_data).encode('utf-8'))
                    print(f"❌ Ошибка при отправке данных: {e}")
                finally:
                    conn.close()
                    
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")

if __name__ == "__main__":
    start_server()
