🎙️ Voice Network Assistant

A cross-platform voice-controlled assistant that allows you to monitor and manage network ports, test connectivity, and execute local scripts using voice commands.
It supports both Windows and Linux systems, using SpeechRecognition and pyttsx3 for voice input/output.
___________________________________________________________________________________
✨ Features

🖥️ Detects the operating system (Windows / Linux)
🗣️ Voice feedback using text-to-speech
🇪🇸 Recognizes voice commands in Spanish
📡 Check if specific ports are open or closed
📋 List all open ports (LISTEN state)
🔐 Open or close ports through firewall rules
🌐 Test network connectivity (ping) to:
      -  Google (internet connection)
      -  A configurable target machine (local or remote)
⚡ Execute .bat (Windows) or .sh (Linux) files by voice
❓ Displays a help menu listing all available commands
___________________________________________________________________________________
🧩 Requirements

Make sure you have Python 3.7+ installed and then install the dependencies:
pip install speechrecognition pyttsx3 psutil pyaudio


Note (Linux):
You may need to install PortAudio development libraries before installing pyaudio:
sudo apt install portaudio19-dev
___________________________________________________________________________________
⚙️ Usage

Clone this repository and run the assistant:

git clone https://github.com/Bonilla23/FinalProyect_ASIR.git
cd FinalProyect_ASIR
python TrabajoFinal.py

Then simply speak one of the supported commands when prompted. 🎤
___________________________________________________________________________________
🎧 Voice Commands
Command (Spanish)	Description
puertos abiertos	Lists all currently listening ports
puerto <número>	Checks if the specific port is open/closed
abrir puerto <número>	Removes firewall rule blocking the port
cerrar puerto <número>	Adds firewall rule to block the port
abrir archivo .bat / .sh	Runs a script from a predefined folder
conexión a Google	Checks internet connectivity
conexión a la otra máquina	Pings a configurable IP address
ayuda	Shows the list of available commands
salir	Exits the assistant
___________________________________________________________________________________
⚠️ Permissions

On Linux, opening or closing ports requires root privileges because it uses iptables.
Make sure to adjust the script folder path (ArchivosImportantes) to your local directory structure.
___________________________________________________________________________________
📄 License

This project is licensed under the MIT License.
