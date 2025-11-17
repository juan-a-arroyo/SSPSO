import threading      # Importa el módulo para trabajar con hilos (threads)
import time           # Para usar pausas con sleep()
import random         # Para generar tiempos aleatorios

LIMITE_COMIDAS = 6    # Número de veces que cada filósofo debe comer antes de terminar

# Clase que representa a cada filósofo, derivada de threading.Thread
class Filosofo(threading.Thread):
    
    # Constructor del filósofo
    def __init__(self, id_filosofo, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, numero_filosofos):
        super().__init__()                  # Inicializa la clase base Thread
        self.id = id_filosofo              # Número identificador del filósofo
        self.tenedor_izq = tenedor_izq     # Semáforo/lock del tenedor izquierdo
        self.tenedor_der = tenedor_der     # Semáforo/lock del tenedor derecho
        self.id_tenedor_izq = id_tenedor_izq   # ID numérico del tenedor izquierdo (solo para mostrar)
        self.id_tenedor_der = id_tenedor_der   # ID numérico del tenedor derecho (solo para mostrar)

        # Truco para evitar interbloqueo: el último filósofo toma los tenedores al revés
        self.es_el_ultimo_filosofo = (id_filosofo == numero_filosofos - 1)

        self.veces_comidas = 0             # Contador de cuántas veces ha comido

    # Método que ejecuta el hilo del filósofo
    def run(self):
        # Mientras no haya comido el límite establecido...
        while self.veces_comidas < LIMITE_COMIDAS:
            self.pensar()   # Primero piensa
            self.comer()    # Luego intenta comer

        # Cuando termina su ciclo, muestra un mensaje
        print(f"Filósofo {self.id} terminó su ciclo (comió {self.veces_comidas} veces).")

    # Simula la acción de pensar
    def pensar(self):
        print(f"Filósofo {self.id} está pensando.")
        time.sleep(random.uniform(1, 3))   # Pausa de 1 a 3 segundos

    # Simula la acción de comer
    def comer(self):
        print(f"Filósofo {self.id} tiene hambre y quiere comer (intento {self.veces_comidas + 1}).")

        # Si es el último filósofo, toma los tenedores en orden inverso
        if self.es_el_ultimo_filosofo:
            print(f"Filósofo {self.id} (el último) intenta tomar tenedor DERECHO {self.id_tenedor_der}.")
            self.tenedor_der.acquire()      # Intenta bloquear el tenedor derecho

            print(f"Filósofo {self.id} (el último) intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.")
            self.tenedor_izq.acquire()      # Luego el tenedor izquierdo
        else:
            # Los demás filósofos toman el izquierdo primero
            print(f"Filósofo {self.id} intenta tomar tenedor IZQUIERDO {self.id_tenedor_izq}.")
            self.tenedor_izq.acquire()      # Bloquea el tenedor izquierdo

            print(f"Filósofo {self.id} intenta tomar tenedor DERECHO {self.id_tenedor_der}.")
            self.tenedor_der.acquire()      # Bloquea el tenedor derecho

        # Ya tiene ambos tenedores, incrementa el contador
        self.veces_comidas += 1

        print(f"--- Filósofo {self.id} está COMIENDO (vez {self.veces_comidas}). ---")
        time.sleep(random.uniform(1, 4))    # Simula el tiempo comiendo

        # Suelta los tenedores cuando termina
        print(f"--- Filósofo {self.id} terminó de comer (vez {self.veces_comidas}) y suelta los tenedores. ---")
        self.tenedor_izq.release()          # Libera tenedor izquierdo
        self.tenedor_der.release()          # Libera tenedor derecho

# Número total de filósofos
NUM_FILOSOFOS = 5

# Lista donde se guardarán los locks (tenedores)
tenedores = []
for i in range(NUM_FILOSOFOS):
    tenedor = threading.Lock()   # Cada tenedor es simplemente un Lock
    tenedores.append(tenedor)    # Se añade al arreglo

# Lista donde se guardarán los objetos filósofo
filosofos = []

print(f"Iniciando simulación: {NUM_FILOSOFOS} filósofos, deben comer {LIMITE_COMIDAS} veces cada uno.")

# Crear y lanzar los filósofos
for i in range(NUM_FILOSOFOS):
    id_tenedor_izq = i                      # ID del tenedor izquierdo es i
    id_tenedor_der = (i + 1) % NUM_FILOSOFOS  # El derecho es (i+1 mod N)

    tenedor_izq = tenedores[id_tenedor_izq]   # Referencia al objeto Lock izquierdo
    tenedor_der = tenedores[id_tenedor_der]   # Referencia al Lock derecho

    # Crear objeto filósofo con sus tenedores asignados
    filosofo = Filosofo(i, tenedor_izq, id_tenedor_izq, tenedor_der, id_tenedor_der, NUM_FILOSOFOS)

    filosofos.append(filosofo)  # Añadir a la lista general
    filosofo.start()            # Lanzar hilo del filósofo

# Esperar a que todos los filósofos terminen
for filosofo in filosofos:
    filosofo.join()

# Mensaje final
print("\n-----------------------------------------------------")
print(f"Todos los filósofos han comido {LIMITE_COMIDAS} veces.")
print("La simulación ha terminado.")
print("-----------------------------------------------------")
