import threading
import time
import random
import os
import sys

# --- Configuración e Importación para Tecla ESC ---
# Variable global para detener los hilos
running = True

try:
    # Para Windows (usará msvcrt)
    import msvcrt
    
    def get_key():
        if msvcrt.kbhit():
            # Devuelve b'\x1b' para ESC
            return msvcrt.getch()
        return None

except ImportError:
    # Para Linux/macOS (usará tty y termios)
    import tty
    import termios
    import fcntl

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        # Configurar stdin para lectura no bloqueante
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        try:
            tty.setcbreak(sys.stdin.fileno())
            # Devuelve '\x1b' para ESC
            key = sys.stdin.read(1)
            return key.encode('utf-8') if key else None
        except (IOError, TypeError):
            return None
        finally:
            # Restaurar configuración de la terminal
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)

# --- Constantes del Problema ---
BUFFER_SIZE = 15
EMPTY_CHAR = '-'  # Carácter para espacio vacío
FULL_CHAR = '*'   # Carácter para producto (Req #4, #10, #18)

# --- Recursos Compartidos ---
# El contenedor de 15 elementos (Req #2)
buffer = [EMPTY_CHAR] * BUFFER_SIZE
in_idx = 0   # Índice donde el productor inserta
out_idx = 0  # Índice de donde el consumidor saca

# Semáforo para la exclusión mutua (Req #5)
# Solo uno puede estar "dentro" a la vez
mutex = threading.Lock()

# Semáforo 'empty' cuenta los espacios vacíos (Req #6)
# Inicia en 15 (buffer lleno de espacios vacíos)
empty = threading.Semaphore(BUFFER_SIZE)

# Semáforo 'full' cuenta los espacios ocupados (Req #7)
# Inicia en 0 (buffer vacío de productos)
full = threading.Semaphore(0)

# Variables de estado para la UI (Req #8)
producer_status = "Iniciando..."
consumer_status = "Iniciando..."
last_message = ""

# --- Funciones de los Hilos ---

def productor():
    """
    Función para el hilo productor. (Req #1)
    Produce de 1 a 4 elementos en cada ciclo.
    """
    global in_idx, producer_status, running, last_message
    
    while running:
        # 1. Dormir por un tiempo aleatorio (Req #9)
        producer_status = "Durmiendo"
        time.sleep(random.uniform(0.5, 2.0))
        if not running: break

        # 2. Determinar cuántos producir (Req #11)
        num_to_produce = random.randint(1, 4)
        producer_status = f"Intentando producir {num_to_produce}..."
        last_message = "Productor intenta entrar..." # (Req #8.iii)
        
        # 3. Producir N elementos
        for i in range(num_to_produce):
            # 3a. Esperar a que haya un espacio vacío (Req #6)
            # (Se bloquea si el buffer está lleno)
            empty.acquire()
            if not running: break # Salir si se presionó ESC mientras esperaba

            # 3b. Adquirir el lock para exclusión mutua (Req #5)
            mutex.acquire()
            if not running: # Doble chequeo por si ESC se presionó
                mutex.release()
                empty.release() # Devolver el "permiso" si no se usó
                break
                
            # --- SECCIÓN CRÍTICA (DENTRO DEL CONTENEDOR) ---
            producer_status = "Trabajando" # (Req #8.i)
            last_message = "Productor TRABAJANDO"

            # Colocar producto en el buffer (Req #12)
            buffer[in_idx] = FULL_CHAR
            in_idx = (in_idx + 1) % BUFFER_SIZE  # Lógica circular (Req #3, #14)
            
            # Simular tiempo de trabajo (para visibilidad)
            time.sleep(0.1) 
            
            # 3c. Liberar el lock
            mutex.release()
            
            # 3d. Señalar que hay un nuevo producto
            full.release()
            # --- FIN SECCIÓN CRÍTICA ---
            
        if running:
            last_message = f"Productor terminó (produjo {num_to_produce})"

def consumidor():
    """
    Función para el hilo consumidor. (Req #1)
    Consume de 1 a 4 elementos en cada ciclo.
    """
    global out_idx, consumer_status, running, last_message

    while running:
        # 1. Dormir por un tiempo aleatorio (Req #9)
        consumer_status = "Durmiendo" # (Req #8.ii)
        time.sleep(random.uniform(0.5, 2.0))
        if not running: break

        # 2. Determinar cuántos consumir (Req #11)
        num_to_consume = random.randint(1, 4)
        consumer_status = f"Intentando consumir {num_to_consume}..."
        last_message = "Consumidor intenta entrar..." # (Req #8.iii)

        # 3. Consumir N elementos
        for i in range(num_to_consume):
            # 3a. Esperar a que haya un producto (Req #7)
            # (Se bloquea si el buffer está vacío)
            full.acquire()
            if not running: break # Salir si se presionó ESC mientras esperaba

            # 3b. Adquirir el lock para exclusión mutua (Req #5)
            mutex.acquire()
            if not running:
                mutex.release()
                full.release() # Devolver el "permiso" si no se usó
                break

            # --- SECCIÓN CRÍTICA (DENTRO DEL CONTENEDOR) ---
            consumer_status = "Trabajando" # (Req #8.ii)
            last_message = "Consumidor TRABAJANDO"

            # Quitar producto del buffer (Req #13)
            buffer[out_idx] = EMPTY_CHAR
            out_idx = (out_idx + 1) % BUFFER_SIZE # Lógica circular (Req #3, #14)

            # Simular tiempo de trabajo (para visibilidad)
            time.sleep(0.15) 
            
            # 3c. Liberar el lock
            mutex.release()
            
            # 3d. Señalar que hay un nuevo espacio vacío
            empty.release()
            # --- FIN SECCIÓN CRÍTICA ---

        if running:
            last_message = f"Consumidor terminó (consumió {num_to_consume})"

def keyboard_listener():
    """
    Escucha la tecla ESC para detener el programa (Req #14).
    """
    global running, last_message
    
    while running:
        key = get_key()
        if key == b'\x1b': # b'\x1b' es el código para ESC
            running = False
            last_message = "¡Tecla ESC presionada! Saliendo..."
            # Forzar a los hilos a despertar para que vean 'running = False'
            # Damos un "permiso" a cada semáforo por si estaban bloqueados
            empty.release()
            full.release()
            break
        time.sleep(0.05) # No saturar el CPU

def display():
    """
    Limpia la pantalla y redibuja el estado actual del buffer y los hilos.
    """
    clear_cmd = 'cls' if os.name == 'nt' else 'clear'
    
    while running:
        os.system(clear_cmd)
        
        print("--- Problema Productor-Consumidor (Python) ---")
        print("Presiona 'ESC' para salir.\n")
        
        # 8.a. Mostrar el contenedor
        print("Contenedor (Capacidad: 15):")
        
        # Números de las casillas (Req #8.i en el PDF [cite: 14, 38])
        header = " ".join(f"{i+1:<2}" for i in range(BUFFER_SIZE))
        print(f"[{header}]")
        
        # Contenido del buffer
        content = " ".join(f"{s:<2}" for s in buffer)
        print(f"[{content}]\n")
        
        # Punteros (para depuración y claridad)
        pointers = " " * (in_idx * 3 + 1) + "P"
        if in_idx == out_idx:
            pointers = " " * (in_idx * 3 + 1) + "P/C"
        else:
            pointers += "\n" + " " * (out_idx * 3 + 1) + "C"
        print(f"P=Productor, C=Consumidor\n{pointers}\n")

        # 8.b, 8.c, 8.d. Mostrar información de estado (Req #8)
        print("--- Estado ---")
        print(f"Productor:   {producer_status:<40}")
        print(f"Consumidor:  {consumer_status:<40}")
        print(f"\nÚltima Acción: {last_message}")
        
        # Frecuencia de actualización
        time.sleep(0.1)

# --- Programa Principal ---
if __name__ == "__main__":
    # Configurar hilos como 'daemon' para que terminen 
    # si el hilo principal (display) termina.
    p_thread = threading.Thread(target=productor, daemon=True)
    c_thread = threading.Thread(target=consumidor, daemon=True)
    k_thread = threading.Thread(target=keyboard_listener, daemon=True)

    # Iniciar hilos
    p_thread.start()
    c_thread.start()
    k_thread.start()

    # El hilo principal se encargará de dibujar la pantalla
    try:
        display()
    except KeyboardInterrupt:
        # Manejar Ctrl+C por si acaso
        running = False
        empty.release()
        full.release()
        
    print("\nPrograma finalizado.")
    # Los hilos daemon se detendrán automáticamente