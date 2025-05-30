import speech_recognition as sr
import pyttsx3
import socket
import subprocess
import os
import psutil
# Detecta el sistema operativo
def detectar_sistema():
    if os.name == "nt":
        return "Windows"
    elif os.name == "posix":
        return "Linux"
    else:
        return "Desconocido"

def verificar_puerto(puerto):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        resultado = sock.connect_ex(('127.0.0.1', puerto))
        return resultado == 0
    except socket.error:
        return False
    finally:
        sock.close()

def obtener_puertos_abiertos():
    puertos_abiertos = set()
    sistema = detectar_sistema()

    if sistema in ["Linux", "Windows"]:
        try:
            conexiones = psutil.net_connections(kind='inet')
            for conn in conexiones:
                if conn.status == psutil.CONN_LISTEN and conn.laddr:
                    puertos_abiertos.add(conn.laddr.port)
        except Exception as e:
            print("Error al obtener puertos:", e)
    return puertos_abiertos

def hacer_ping(direccion):
    try:
        if detectar_sistema() == "Windows":
            comando = ["ping", "-n", "1", direccion]
        else:
            comando = ["ping", "-c", "1", direccion]

        salida = subprocess.run(comando, capture_output=True, text=True)
        return salida.returncode == 0
    except Exception:
        return False
    
def cerrar_puerto(puerto):
    sistema = detectar_sistema()
    if sistema == "Windows":
        comando = f'netsh advfirewall firewall add rule name="Bloquear puerto {puerto}" dir=in action=block protocol=TCP localport={puerto}'
    else:
        comando = f'sudo iptables -A INPUT -p tcp --dport {puerto} -j DROP'
    return ejecutar_comando(comando)

def abrir_puerto(puerto):
    sistema = detectar_sistema()
    if sistema == "Windows":
        comando = f'netsh advfirewall firewall delete rule name="Bloquear puerto {puerto}" protocol=TCP localport={puerto}'
    else:
        comando = f'sudo iptables -D INPUT -p tcp --dport {puerto} -j DROP'
    return ejecutar_comando(comando)

def ejecutar_comando(comando):
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return resultado.returncode == 0
    except Exception as e:
        print("Error al ejecutar comando:", e)
        return False

def mostrar_ayuda():
    ayuda_texto = """
    Comandos disponibles:

    1. "puertos abiertos" - Muestra los puertos en estado LISTEN.
    2. "puerto <número>" - Verifica si un puerto específico está abierto.
    2. "abrir  puerto <número>" - Abrir un puerto.
    2. "cerrar puerto <número>" - Cerrar un puerto.
    3. "abrir archivo .bat" - Abrir un archivo .bat
    4. "conexión a Google" - Verifica si tienes acceso a Internet.
    5. "conexión a la otra máquina" - Comprueba conexión con una IP local.
    6. "salir" - Finaliza el asistente.
    """
    print(ayuda_texto)
    return ayuda_texto

def reconocer_voz():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    sistema = detectar_sistema()
    print(f"Sistema operativo detectado: {sistema}")
    engine.say(f"Estás usando {sistema}")
    engine.runAndWait()

    while True:
        with sr.Microphone() as source:
            print("¿Cuál es su siguiente comando?")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                print("Reconociendo...")
                texto = recognizer.recognize_google(audio, language="es-ES")
                print(f"Has dicho: {texto}")
                palabras = texto.lower().split()

                if "salir" in texto.lower():
                    engine.say("Hasta luego, que tengas un buen día.")
                    engine.runAndWait()
                    break
            #------------------------------------------------------------------------------------#
                elif "ayuda" in texto.lower():
                    ayuda = mostrar_ayuda()
                    engine.say("Los comandos disponibles son los siguientes.")
                    engine.runAndWait()
            #------------------------------------------------------------------------------------#   
                elif "cerrar puerto" in texto.lower():
                    if hacer_ping("google.com"):
                        engine.say("La conexión a Internet funciona correctamente.")
                    else:
                        engine.say("No hay conexión a Internet.")
                    engine.runAndWait()
            #------------------------------------------------------------------------------------#
                elif "conexión a google" in texto.lower():
                    if hacer_ping("google.com"):
                        engine.say("La conexión a Internet funciona correctamente.")
                    else:
                        engine.say("No hay conexión a Internet.")
                    engine.runAndWait()
            #------------------------------------------------------------------------------------#
                elif "conexión a la otra máquina" in texto.lower():
                    ip_objetivo = "8.8.8.8"  # Modifica según la IP de la otra maquina
                    if hacer_ping(ip_objetivo):
                        engine.say(f"La máquina con IP {ip_objetivo} está disponible.")
                    else:
                        engine.say(f"No se pudo contactar con la máquina {ip_objetivo}.")
                    engine.runAndWait()
            #------------------------------------------------------------------------------------#
                elif "abrir un archivo bat" in texto.lower():
                    engine.say("Por favor, dime la ruta completa del archivo batch.")
                    engine.runAndWait()

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source)
                        print("Escuchando la ruta del archivo...")
                        audio = recognizer.listen(source)

                    try:
                        ruta_bat = recognizer.recognize_google(audio, language="es-ES")
                        print(f"Ruta reconocida: {ruta_bat}")

                        # Limpia texto hablado
                        ruta_bat = ruta_bat.replace("comillas", "").replace("\"", "").strip()

                        # Verifica si termina en .bat
                        if not ruta_bat.lower().endswith(".bat"):
                            engine.say("Ese archivo no parece ser un archivo batch.")
                        elif os.path.isfile(ruta_bat):
                            os.startfile(ruta_bat)
                            engine.say("El archivo batch se ha abierto correctamente.")
                        else:
                            engine.say("No se encontró el archivo en la ruta especificada.")
                        engine.runAndWait()

                    except sr.UnknownValueError:
                        engine.say("No entendí la ruta. Inténtalo nuevamente.")
                        engine.runAndWait()
                    except Exception as e:
                        print("Error al abrir archivo BAT:", e)
                        engine.say("Ocurrió un error al intentar abrir el archivo.")
                        engine.runAndWait()
            #------------------------------------------------------------------------------------#
                elif "puertos abiertos" in texto.lower():
                    puertos = obtener_puertos_abiertos()
                    if puertos:
                        puertos_list = ", ".join(map(str, puertos))
                        print(f"Puertos abiertos: {puertos_list}")
                        engine.say("He impreso los puertos abiertos en la terminal.")
                    else:
                        print("No hay puertos abiertos.")
                        engine.say("No hay puertos abiertos en tu máquina.")
                    engine.runAndWait()
            #------------------------------------------------------------------------------------#
                for i, palabra in enumerate(palabras):
                    if palabra == "cerrar" and i + 2 < len(palabras) and palabras[i + 1] == "puerto":
                        try:
                            puerto = int(palabras[i + 2])
                            if cerrar_puerto(puerto):
                                engine.say(f"El puerto {puerto} ha sido bloqueado.")
                            else:
                                engine.say(f"No se pudo bloquear el puerto {puerto}.")
                            engine.runAndWait()
                            break
                        except ValueError:
                            continue
                    elif palabra == "abrir" and i + 2 < len(palabras) and palabras[i + 1] == "puerto":
                        try:
                            puerto = int(palabras[i + 2])
                            if abrir_puerto(puerto):
                                engine.say(f"El puerto {puerto} ha sido desbloqueado.")
                            else:
                                engine.say(f"No se pudo desbloquear el puerto {puerto}.")
                            engine.runAndWait()
                            break
                        except ValueError:
                            continue

            except sr.UnknownValueError:
                engine.say("No se pudo entender lo que dijiste.")
                engine.runAndWait()

            except sr.RequestError as e:
                engine.say("Hubo un error al intentar conectarme al servicio.")
                engine.runAndWait()

if __name__ == "__main__":
    reconocer_voz()
