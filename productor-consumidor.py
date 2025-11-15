import threading,random,time,os,msvcrt
from threading import Semaphore

N=15
buf=['_']*N
in_idx=out_idx=0
mutex=Semaphore(1)
space=Semaphore(N)
items=Semaphore(0)
stop=False

def show(p,c,msg=''):
    os.system("cls")
    print("Contenedor:")
    print('  ' +''.join(f"{c:3}" for c in buf))
    print(''.join(f"{i+1:3}" for i in range(N)))
    print(f"\nProductor: {p}   Consumidor: {c}")
    if msg: print(msg)
    print("\nESC para salir.")

def producer():
    global in_idx,stop
    while not stop:
        time.sleep(random.uniform(0.3,1))
        want=random.randint(1,4)
        show(f"quiere {want}",'dormido')
        for _ in range(want): space.acquire()
        mutex.acquire()
        for _ in range(want):
            buf[in_idx]='*'
            in_idx=(in_idx+1)%N
            show("produciendo",'dormido')
            time.sleep(0.08)
        mutex.release()
        for _ in range(want): items.release()
        show("salió",'dormido',f"Produjo {want}")

def consumer():
    global out_idx,stop
    while not stop:
        time.sleep(random.uniform(0.3,1))
        want=random.randint(1,4)
        show('dormido',f"quiere {want}")
        for _ in range(want): items.acquire()
        mutex.acquire()
        for _ in range(want):
            buf[out_idx]='_'
            out_idx=(out_idx+1)%N
            show('dormido',"consumiendo")
            time.sleep(0.08)
        mutex.release()
        for _ in range(want): space.release()
        show('dormido',"salió",f"Consumió {want}")

def esc_listener():
    global stop
    while not stop:
        if msvcrt.kbhit() and ord(msvcrt.getch())==27:
            stop=True
        time.sleep(0.05)

if __name__=="__main__":
    show("iniciado","iniciado")
    threading.Thread(target=producer,daemon=True).start()
    threading.Thread(target=consumer,daemon=True).start()
    threading.Thread(target=esc_listener,daemon=True).start()
    while not stop: time.sleep(0.1)
    show("fin","fin","Programa terminado.")
