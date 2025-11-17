import threading
import time
import random

class Filosofo(threading.Thread):
    
    # Añadimos id_tenedor_izq y id_tenedor_der para guardar los NÚMEROS
    def __init__(self, id_filosofo, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, numero_filosofos): # <-- CAMBIO
        super().__init__()
        self.id = id_filosofo
        self.tenedor_izq = tenedor_izq
        self.tenedor_der = tenedor_der
        
        # Guardamos los IDs de los tenedores aquí
        self.id_tenedor_izq = id_tenedor_izq # <-- CAMBIO
        self.id_tenedor_der = id_tenedor_der # <-- CAMBIO
        
        self.es_el_ultimo_filosofo = (id_filosofo == numero_filosofos - 1)

    def run(self):
        while True:
            self.pensar()
            self.comer()

    def pensar(self):
        print(f"Filósofo {self.id} está pensando.")
        time.sleep(random.uniform(1, 3))

    def comer(self):
        print(f"Filósofo {self.id} tiene hambre y quiere comer.")

        if self.es_el_ultimo_filosofo:
            # ¡Solución Asimétrica! El último filósofo toma el tenedor DERECHO primero.
            # Usamos el ID guardado en el filósofo, no en el tenedor
            print(f"Filósofo {self.id} (el último) intenta tomar tenedor DERECHO {self.id_tenedor_der}.") # <-- CAMBIO
            self.tenedor_der.acquire()
            print(f"Filósofo {self.id} (el último) intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.") # <-- CAMBIO
            self.tenedor_izq.acquire()
        else:
            # Todos los demás filósofos toman el tenedor IZQUIERDO primero.
            print(f"Filósofo {self.id} intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.") # <-- CAMBIO
            self.tenedor_izq.acquire()
            print(f"Filósofo {self.id} intenta tomar tenedor DERECHO {self.id_tenedor_der}.") # <-- CAMBIO
            self.tenedor_der.acquire()

        # Si el código llega aquí, el filósofo tiene ambos tenedores
        print(f"--- Filósofo {self.id} está COMIENDO. ---")
        time.sleep(random.uniform(1, 4))
        print(f"--- Filósofo {self.id} terminó de comer y suelta los tenedores. ---")

        # Libera los tenedores
        self.tenedor_izq.release()
        self.tenedor_der.release()

# --- Configuración de la simulación ---

NUM_FILOSOFOS = 5
tenedores = []

# Crear los tenedores (Locks)
for i in range(NUM_FILOSOFOS):
    tenedor = threading.Lock()
    # tenedor._ident = i  <-- ELIMINAMOS ESTA LÍNEA ERRÓNEA
    tenedores.append(tenedor)

filosofos = []

# Crear e iniciar los filósofos (Threads)
for i in range(NUM_FILOSOFOS):
    # Definimos los IDs de los tenedores aquí
    id_tenedor_izq = i # <-- CAMBIO
    id_tenedor_der = (i + 1) % NUM_FILOSOFOS # <-- CAMBIO
    
    # Obtenemos los objetos Lock
    tenedor_izq = tenedores[id_tenedor_izq]
    tenedor_der = tenedores[id_tenedor_der]
    
    # Pasamos los objetos Lock Y sus IDs al constructor
    filosofo = Filosofo(i, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, NUM_FILOSOFOS) # <-- CAMBIO
    filosofos.append(filosofo)
    filosofo.start() # Inicia el hilo

# Esperar a que todos los hilos terminen
for filosofo in filosofos:
    filosofo.join()