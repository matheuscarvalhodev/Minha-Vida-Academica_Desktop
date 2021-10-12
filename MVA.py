from PyQt5 import QtWidgets
from src.utilities.util import Token
from src.infra.conexao import login
from PyQt5.QtCore import QEventLoop, QTimer
import sys_qr_code
from PyQt5.uic import loadUi
import sys

app = QtWidgets.QApplication(sys.argv)
tela_login = loadUi("src/design/login.ui")

# FUNÇÃO QUE CHAMA A CLASSE DE LEITURA DE QR_CODE


def main():
    window = sys_qr_code.sis_qr_code()
    window.showMaximized()


# FUNÇÃO DA TELA DE LOGIN
def tela_cam():
    tela_login.aviso.setText("")
    tela_login.senha.setEchoMode(QtWidgets.QLineEdit.Password)
    usuario = tela_login.usuario.text()
    sys_qr_code.USER = usuario
    senha = tela_login.senha.text()
    token, res = login(usuario, senha)
    if res == "valido":
        Token(token)
        # tipo = verifica_tipo(token)
        # Tipo(tipo)
        tela_login.hide()
        tela_login.usuario.clear()
        tela_login.senha.clear()
        main()
    elif res == "invalido":
        tela_login.aviso.setText("Usuário ou senha incorretos")
        loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()
        tela_login.aviso.setText("")
    elif res == "nao conectou":
        tela_login.aviso.setText(
            "Não é possivel se conectar\nVerifique a conexão com a internet"
        )
        loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()
        tela_login.aviso.setText("")


def confirma(cond):
    if cond is True:
        tela_login.enviar.clicked.connect(tela_cam)
        tela_login.show()
    else:
        print("Não deu")


if __name__ == "__main__":
    tela_login.enviar.clicked.connect(tela_cam)
    tela_login.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Acabou! Acabou o programa!")
