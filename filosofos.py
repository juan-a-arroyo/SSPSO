import threading
import time
import random

LIMITE_COMIDAS = 6

class Filosofo(threading.Thread):
    
    def __init__(self, id_filosofo, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, numero_filosofos):
        super().__init__()
        self.id = id_filosofo  # El ID interno sigue siendo 0-4 para la lógica
        self.tenedor_izq = tenedor_izq
        self.tenedor_der = tenedor_der
        self.id_tenedor_izq = id_tenedor_izq
        self.id_tenedor_der = id_tenedor_der
        self.es_el_ultimo_filosofo = (id_filosofo == numero_filosofos - 1)
        self.veces_comidas = 0

    def run(self):
        while self.veces_comidas < LIMITE_COMIDAS:
            self.pensar()
            self.comer()
        
        # --- CAMBIO: Se muestra self.id + 1 ---
        print(f"Filósofo {self.id + 1} terminó su ciclo (comió {self.veces_comidas} veces).")

    def pensar(self):
        # --- CAMBIO: Se muestra self.id + 1 ---
        print(f"Filósofo {self.id + 1} está pensando.")
        time.sleep(random.uniform(1, 3))

    def comer(self):
        # --- CAMBIO: Se muestra self.id + 1 ---
        print(f"Filósofo {self.id + 1} tiene hambre y quiere comer (intento {self.veces_comidas + 1}).")

        if self.es_el_ultimo_filosofo:
            # --- CAMBIO: Se muestra self.id + 1 ---
            print(f"Filósofo {self.id + 1} (el último) intenta tomar tenedor DERECHO {self.id_tenedor_der}.")
            self.tenedor_der.acquire()
            # --- CAMBIO: Se muestra self.id + 1 ---
            print(f"Filósofo {self.id + 1} (el último) intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.")
            self.tenedor_izq.acquire()
        else:
            # --- CAMBIO: Se muestra self.id + 1 ---
            print(f"Filósofo {self.id + 1} intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.")
            self.tenedor_izq.acquire()
            # --- CAMBIO: Se muestra self.id + 1 ---
            print(f"Filósofo {self.id + 1} intenta tomar tenedor DERECHO {self.id_tenedor_der}.")
            self.tenedor_der.acquire()

        self.veces_comidas += 1
        
        # --- CAMBIO: Se muestra self.id + 1 ---
        print(f"--- Filósofo {self.id + 1} está COMIENDO (vez {self.veces_comidas}). ---")
        time.sleep(random.uniform(1, 4))
        # --- CAMBIO: Se muestra self.id + 1 ---
        print(f"--- Filósofo {self.id + 1} terminó de comer (vez {self.veces_comidas}) y suelta los tenedores. ---")

        self.tenedor_izq.release()
        self.tenedor_der.release()

# --- El resto del código no cambia ---

NUM_FILOSOFOS = 5
tenedores = []
for i in range(NUM_FILOSOFOS):
    tenedor = threading.Lock()
    tenedores.append(tenedor)

filosofos = []

print(f"Iniciando simulación: {NUM_FILOSOFOS} filósofos, deben comer {LIMITE_COMIDAS} veces cada uno.")

# El bucle principal sigue pasando 'i' (0-4) al constructor
# Esto es crucial para que la lógica de los tenedores funcione
for i in range(NUM_FILOSOFOS):
    id_tenedor_izq = i
    id_tenedor_der = (i + 1) % NUM_FILOSOFOS
    
    tenedor_izq = tenedores[id_tenedor_izq]
    tenedor_der = tenedores[id_tenedor_der]
    
    # Pasamos 'i' (0, 1, 2, 3, 4) como id_filosofo
    filosofo = Filosofo(i, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, NUM_FILOSOFOS)
    filosofos.append(filosofo)
    filosofo.start()

for filosofo in filosofos:
    filosofo.join()

print("\n-----------------------------------------------------")
print(f"Todos los filósofos han comido {LIMITE_COMIDAS} veces.")
print("La simulación ha terminado.")
print("-----------------------------------------------------")