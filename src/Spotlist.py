import sys, os, spotipy, webbrowser, ctypes, base64
import spotipy.util as util
from winsound import MessageBeep
from win32api import MessageBox
from win32con import MB_ICONEXCLAMATION, MB_ICONERROR
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from gui import Ui_MainWindow
from random import shuffle
from notifypy import Notify
from datetime import datetime


class Spotify(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/icon.ico'))
        self.help_btn.setIcon(QIcon('img/help.png'))
        self.navegador_btn.setIcon(QIcon('img/browser.png'))
        self.arts_btn.setIcon(QIcon('img/add.png'))
        if '.data' in os.listdir():
            with open('.data', 'r') as file:
                credentials = file.readlines()
                self.client_id.setText(credentials[0].strip("\n"))
                self.secret_id.setText(credentials[1].strip("\n"))
                self.username.setText(credentials[2])
        self.arts_btn.clicked.connect(self.verify)
        self.start_btn.clicked.connect(self.run)
        self.navegador_btn.clicked.connect(lambda : webbrowser.open('https://developer.spotify.com/dashboard/login'))
        self.help_btn.clicked.connect(lambda : os.system('start ./public/index.html'))

    def verify(self):

        if self.client_id.text() != '' and self.secret_id.text() != '' and self.username.text() != '' and self.playlist_uri.text() != '':
            open('lista.txt', 'w')
            os.system('start lista.txt')
            self.start_btn.setEnabled(True)

        else:
            MessageBeep()
            MessageBox(0, 'Preencha os campos necessários!', 'Aviso', MB_ICONEXCLAMATION)


    def run(self):

        # as credenciais do spotify contem 32 caracteres, logo esse if tem com objetivo impedir que possa
        # ocorrer algum erro com relação a isso durante a execução do código. 

        if len(self.client_id.text()) < 32 or len(self.secret_id.text()) < 32:
            MessageBeep() 
            MessageBox(0, 'As informações inseridas estão incorretas!\nVerifique e tente novamente.', 'Aviso', MB_ICONEXCLAMATION)
            return

        file = True if 'lista.txt' in os.listdir() else False 
        
        if file:
            size = os.stat("lista.txt")
        
            if size.st_size == 0:
                MessageBeep()
                MessageBox(0, 'A lista não pode estar vazia, tente novamente!', 'Aviso', MB_ICONEXCLAMATION)
                return
        else:
            MessageBeep()    
            MessageBox(0, 'Você deve criar uma lista com os nomes desejados antes de iniciar o processo!', 'Aviso', MB_ICONEXCLAMATION)
            return

        cli_id = self.client_id.text()
        secret_id = self.secret_id.text()
        user = self.username.text()
        uri = self.playlist_uri.text()[17:]
        scope = 'playlist-modify-public playlist-modify-private'

        self.artistas = []

        try:
            with open('lista.txt', 'r') as file:
                for i in file:
                    i = i.replace('\n', '')
                    self.artistas.append(i)
        except FileNotFoundError:
            MessageBeep()
            MessageBox(0, 'Arquivo não encontrado', 'Aviso', MB_ICONEXCLAMATION)
        else:
            self.add_musicas(user, scope, cli_id, secret_id, uri)

    def add_musicas(self, username, scope, client_id, secret_id, uri):
        try:
            token = util.prompt_for_user_token(username=username,
                                            scope=scope, 
                                            client_id= client_id, 
                                            client_secret= secret_id,
                                            redirect_uri='http://localhost:8080/callback',
                                            cache_path='cache',
                                            show_dialog=True)
        except spotipy.oauth2.SpotifyOauthError:
            MessageBeep()
            MessageBox(0, "Erro durante a validação das credenciais. Verifique se os dados inseridos estão corretos e tente novamente!", 'Aviso', MB_ICONERROR)
            return
        else:
            musicas = {}
            tracks = []

            if token:
                sp = spotipy.Spotify(auth=token)
                sp.trace = False

                self.verify_Log()
                
                for artista in range(0, len(self.artistas)):
                    result = sp.search(self.artistas[artista], limit=int(self.number_of_music.text()))
                    for i, j in enumerate(result['tracks']['items']):
                        if j["name"] not in musicas.values():
                            musicas[j["id"]] = j["name"]
                            with open('logs/log-spotlist.txt', 'a+') as file:
                                file.write(f' {j["name"]} de {j["artists"][0]["name"]} foi adicionada a playlist\n')
                
                
                [tracks.append(k.strip('"')) for k in musicas.keys()]
                
                if self.aleatorio.isChecked():
                    shuffle(tracks)
                            
                while tracks:
                    try:
                        result = sp.user_playlist_add_tracks(username, uri, tracks[:1])
                    except Exception as erro:
                        print('erro')
                    tracks = tracks[1:]

                self.sendNotification(title='Processo concluído', msg='A playlist foi criada, o aplicativo já pode ser encerrado!')
    
    def sendNotification(self, title=str, msg=str):
        notification = Notify(default_notification_application_name="                SpotList")
        notification.title = title
        notification.message = msg
        notification.icon = 'img/icon.ico'
        notification.send()

    def verify_Log(self):
        path = 'logs/log-spotlist.txt'
        date = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        with open(path, 'a+') as file:
            file.write(48 * '-' + '\n')
            file.write('\t[LOG CRIADO EM {}]\n'.format(date))
            file.write(48 * '-' + '\n\n')
        

    

if __name__ == '__main__':
    if sys.platform == 'win32':
        import win32com.shell.shell as shell
        ASADMIN = 'asadmin'
        if sys.argv[-1] != ASADMIN:
            try:
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
                shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
            except:
                sys.exit()
            else:
                path = os.path.dirname(os.path.realpath(__file__))
                qt = QApplication(sys.argv)
                spotify = Spotify()
                spotify.show()
                qt.exec_()
                os.remove('lista.txt') if 'lista.txt' in os.listdir(path) else ...
                os.remove('cache') if 'cache' in os.listdir(path) else ...
                if spotify.save_Credentials.isChecked() and len(spotify.client_id.text()) == len(spotify.secret_id.text()) == 32 :
                    with open('.data', 'w') as file:
                        file.write(spotify.client_id.text() + "\n")
                        file.write(spotify.secret_id.text() + "\n") 
                        if spotify.username.text() != '':
                            file.write(spotify.username.text())
                    
