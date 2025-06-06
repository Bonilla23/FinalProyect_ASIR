import speech_recognition as sr
import pyttsx3
import socket
import subprocess
import os
import psutil
import platform

def inicializar_voz():
    sistema = platform.system()
    if sistema == "Windows":
        engine = pyttsx3.init('sapi5')
    elif sistema == "Linux":
        engine = pyttsx3.init('espeak')
    else:
        engine = pyttsx3.init()

    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

    voices = engine.getProperty('voices')
    for v in voices:
        if 'spanish' in v.name.lower() or 'es' in v.id.lower():
            engine.setProperty('voice', v.id)
            break

    return engine

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
        comando = ["ping", "-n", "1", direccion] if detectar_sistema() == "Windows" else ["ping", "-c", "1", direccion]
        salida = subprocess.run(comando, capture_output=True, text=True)
        return salida.returncode == 0
    except Exception:
        return False

def cerrar_puerto(puerto):
    sistema = detectar_sistema()
    if sistema == "Windows":
        comando = f'netsh advfirewall firewall add rule name="Bloquear puerto {puerto}" dir=in action=block protocol=TCP localport={puerto}'
    else:
        if os.geteuid() != 0:
            print("Este comando requiere privilegios de administrador.")
            return False
        comando = f'iptables -A INPUT -p tcp --dport {puerto} -j DROP'
    return ejecutar_comando(comando)

def abrir_puerto(puerto):
    sistema = detectar_sistema()
    if sistema == "Windows":
        comando = f'netsh advfirewall firewall delete rule name="Bloquear puerto {puerto}" protocol=TCP localport={puerto}'
    else:
        if os.geteuid() != 0:
            print("Este comando requiere privilegios de administrador.")
            return False
        comando = f'iptables -D INPUT -p tcp --dport {puerto} -j DROP'
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
    2. "puerto <número>" - Verifica si un puerto específico está abierto o cerrado.
    3. "abrir puerto <número>" - Abre un puerto.
    4. "cerrar puerto <número>" - Cierra un puerto.
    5. "abrir archivo .bat o .sh" - Abre un archivo por voz según el sistema operativo.
    6. "conexión a Google" - Verifica si tienes acceso a Internet.
    7. "conexión a la otra máquina" - Comprueba conexión con una IP local.
    8. "salir" - Finaliza el asistente.
    """
    print(ayuda_texto)
    return ayuda_texto

def reconocer_voz():
    recognizer = sr.Recognizer()
    engine = inicializar_voz()

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

            elif "ayuda" in texto.lower():
                mostrar_ayuda()
                engine.say("Los comandos disponibles han sido mostrados.")
                engine.runAndWait()

            elif "conexión a google" in texto.lower():
                if hacer_ping("google.com"):
                    engine.say("La conexión a Internet funciona correctamente.")
                else:
                    engine.say("No hay conexión a Internet.")
                engine.runAndWait()

            elif "conexión a la otra máquina" in texto.lower():
                ip_objetivo = "8.8.8.8"  # Puedes modificar esta IP si lo necesitas
                if hacer_ping(ip_objetivo):
                    engine.say(f"La máquina con IP {ip_objetivo} está disponible.")
                else:
                    engine.say(f"No se pudo contactar con la máquina {ip_objetivo}.")
                engine.runAndWait()

            elif "abrir archivo" in texto.lower() and (".bat" in texto.lower() or ".sh" in texto.lower()):
                sistema = detectar_sistema()
                if sistema == "Windows":
                    extension = ".bat"
                    carpeta = "C:\\Admin\\ArchivosImportantes" # Cambiar ruta
                else:
                    extension = ".sh"
                    carpeta = "/home/usuario/ArchivosImportantes"  # Cambiar ruta

                engine.say(f"Por favor, dime el nombre del archivo {extension} sin la ruta.")
                engine.runAndWait()

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Escuchando el nombre del archivo...")
                    audio = recognizer.listen(source)

                try:
                    nombre_archivo = recognizer.recognize_google(audio, language="es-ES")
                    print(f"Nombre reconocido: {nombre_archivo}")
                    nombre_archivo = nombre_archivo.strip().replace(" ", "")
                    if not nombre_archivo.lower().endswith(extension):
                        nombre_archivo += extension

                    ruta_archivo = os.path.join(carpeta, nombre_archivo)

                    if os.path.isfile(ruta_archivo):
                        if sistema == "Windows":
                            os.startfile(ruta_archivo)
                            engine.say(f"El archivo {nombre_archivo} se ha abierto correctamente.")
                        else:
                            subprocess.run(["chmod", "+x", ruta_archivo])
                            subprocess.Popen(["bash", ruta_archivo])
                            engine.say(f"El archivo {nombre_archivo} ha sido ejecutado.")
                    else:
                        engine.say("No se encontró el archivo en la carpeta especificada.")
                    engine.runAndWait()

                except sr.UnknownValueError:
                    engine.say("No entendí el nombre del archivo. Inténtalo nuevamente.")
                    engine.runAndWait()
                except Exception as e:
                    print("Error al abrir archivo:", e)
                    engine.say("Ocurrió un error al intentar abrir el archivo.")
                    engine.runAndWait()

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

            for i, palabra in enumerate(palabras):
                if palabra == "puerto" and i + 1 < len(palabras):
                    try:
                        puerto = int(palabras[i + 1])
                        if verificar_puerto(puerto):
                            engine.say(f"El puerto {puerto} está abierto.")
                        else:
                            engine.say(f"El puerto {puerto} está cerrado.")
                        engine.runAndWait()
                        break
                    except ValueError:
                        continue

                elif palabra == "cerrar" and i + 2 < len(palabras) and palabras[i + 1] == "puerto":
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
        except sr.RequestError:
            engine.say("Hubo un error al intentar conectarme al servicio.")
            engine.runAndWait()

if __name__ == "__main__":
    reconocer_voz()
