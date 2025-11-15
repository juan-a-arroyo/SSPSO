import threading, random, time, os, msvcrt     # threading: manejo de hilos
                                               # random: generar tiempos y cantidades aleatorias
                                               # time: pausas de ejecución
                                               # os: limpiar pantalla con 'cls'
                                               # msvcrt: detectar teclas (solo Windows)

from threading import Semaphore                # Importar clase Semaphore

N = 15                                         # Tamaño del buffer circular
buf = ['_'] * N                                # Buffer inicializado con guiones bajos
in_idx = out_idx = 0                           # Índices de producción y consumo

mutex = Semaphore(1)                           # Semáforo binario (exclusión mutua)
space = Semaphore(N)                           # Semáforo con espacios disponibles
items = Semaphore(0)                           # Semáforo con items disponibles (inicia vacío)

stop = False                                   # Indica si se debe detener el programa


def show(p, c, msg=''):                        # Función para mostrar el estado en pantalla
    os.system("cls")                           # Limpia la consola
    print("Contenedor:")                       # Título del buffer
    print('  ' + ''.join(f"{c:3}" for c in buf))  # Muestra el buffer formateado
    print(''.join(f"{i+1:3}" for i in range(N)))  # Muestra índices numéricos del buffer
    print(f"\nProductor: {p}   Consumidor: {c}")  # Estados actuales
    if msg:                                     # Si se envía mensaje extra
        print(msg)                              # Lo imprime
    print("\nESC para salir.")                  # Indicador permanente de salida


def producer():                                 # Función del hilo productor
    global in_idx, stop                         # Variables globales que modificará
    while not stop:                             # Ejecutar mientras no se presione ESC
        time.sleep(random.uniform(0.3, 1))      # Dormir un tiempo aleatorio
        want = random.randint(1, 4)             # Elegir cuántos elementos producir
        show(f"quiere {want}", 'dormido')       # Mostrar intención

        for _ in range(want):                   # Esperar espacio disponible
            space.acquire()                     # space-- bloquea si no hay lugar

        mutex.acquire()                         # Entra a sección crítica
        for _ in range(want):                   # Producir 'want' unidades
            buf[in_idx] = '*'                   # Escribir en el buffer
            in_idx = (in_idx + 1) % N           # Avanzar en forma circular
            show("produciendo", 'dormido')      # Mostrar estado
            time.sleep(0.08)                    # Simulación visual
        mutex.release()                         # Salir de sección crítica

        for _ in range(want):                   # Liberar items disponibles
            items.release()                     # items++

        show("salió", 'dormido', f"Produjo {want}")  # Mostrar producción final


def consumer():                                 # Función del hilo consumidor
    global out_idx, stop                        # Variables globales que modificará
    while not stop:                             # Mientras no pidan detener
        time.sleep(random.uniform(0.3, 1))      # Tiempo aleatorio
        want = random.randint(1, 4)             # Cuántos quiere consumir
        show('dormido', f"quiere {want}")       # Mostrar intención

        for _ in range(want):                   # Esperar items disponibles
            items.acquire()                     # items-- bloquea si está vacío

        mutex.acquire()                         # Entra a sección crítica
        for _ in range(want):                   # Consumir 'want' items
            buf[out_idx] = '_'                  # Vaciar posición del buffer
            out_idx = (out_idx + 1) % N         # Avanzar circularmente
            show('dormido', "consumiendo")      # Mostrar estado
            time.sleep(0.08)                    # Simulación visual
        mutex.release()                         # Salir de sección crítica

        for _ in range(want):                   # Liberar espacio disponible
            space.release()                     # space++

        show('dormido', "salió", f"Consumió {want}")  # Reporte final


def esc_listener():                             # Hilo que escucha la tecla ESC
    global stop                                 # Modificará la variable stop
    while not stop:                             # Mientras no se haya detenido
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # Si se presiona ESC
            stop = True                         # Orden de detener programa
        time.sleep(0.05)                        # Evitar consumir CPU


if __name__ == "__main__":                      # Punto de entrada del programa
    show("iniciado", "iniciado")                # Primera vista en pantalla

    threading.Thread(target=producer, daemon=True).start()    # Inicia productor
    threading.Thread(target=consumer, daemon=True).start()    # Inicia consumidor
    threading.Thread(target=esc_listener, daemon=True).start()# Inicia escucha de teclas

    while not stop:                             # Mantener programa vivo
        time.sleep(0.1)                         # Hasta que ESC sea presionado

    show("fin", "fin", "Programa terminado.")   # Pantalla final

