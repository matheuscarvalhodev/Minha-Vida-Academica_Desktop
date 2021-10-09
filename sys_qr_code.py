import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QShortcut
from PyQt5.uic import loadUi
from _imagens import imagens
from src.infra.conexao import enviar_dados, ponto, verifica_vacinacao
from datetime import datetime, date
from src.utilities.util import Horario, read_barcodes, dados_aluno, sleep
from src.utilities import util
from MVA import confirma
from PyQt5.QtCore import Qt
import MVA

USER = ""
HORARIO_ATUAL = ""
HD = ""


class sis_qr_code(QMainWindow):
    global HORARIO_ATUAL, HD, USER
    HD = datetime.now()
    HORARIO_ATUAL = HD.strftime("%H:%M:%S")

    def __init__(self):

        super(sis_qr_code, self).__init__()
        self.window = loadUi("src/design/leitor_qr.ui", self)
        self.logic = 0
        self.value = 0
        # BOTÃO QUE ABRE A CÂMERA
        self.abrir_camera.clicked.connect(self.onClicked)
        # BOTÃO QUE FECHA A CÂMERA
        self.fechar_camera.clicked.connect(self.CloseCapture)
        # BOTÃO DE LOGOUT
        self.sair.clicked.connect(self.closeEvent)
        # BOTÃO DE AUTORIZAR
        self.afirmar.clicked.connect(self.autorizar)
        # BOTÃO DE NÃO AUTORIZAR
        self.negar.clicked.connect(self.nao_autorizar)
        # BOTÃO DE ENVIAR TEMPERATURA
        self.enviar_temp.clicked.connect(self.salvar_temp)
        # BOTÕES DE ENVIAR OU NAO TEMPERATURA
        self.sim.clicked.connect(self.opcao_sim)
        self.nao.clicked.connect(self.opcao_nao)

        self.abrir_camera.setShortcut(QKeySequence("Ctrl+C"))
        self.fechar_camera.setShortcut(QKeySequence("Ctrl+C"))
        self.sair.setShortcut(QKeySequence("Ctrl+S"))
        self.sim.setShortcut(QKeySequence("Enter"))
        self.afirmar.setShortcut(QKeySequence("Enter"))
        self.enviar_temp.setShortcut(QKeySequence("Enter"))
        self.negar.setShortcut(QKeySequence("Delete"))
        self.nao.setShortcut(QKeySequence("Delete"))

        # CONTROLE DE CAMADAS
        self.window.temp.close()
        self.window.aviso_temp.close()
        self.window.fechar_camera.close()
        self.window.observacao.close()
        self.window.regi_saida.close()
        self.window.frame_user.show()
        self.window.campus_all.close()
        self.window.campus_stm.close()
        self.label_user.setText(f"Usuário {USER}")
        self.label_user.setStyleSheet(
            "color: rgb(255, 255, 255);\n"
            'font: 75 16pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;\n"
            "align: center;"
        )

    @pyqtSlot()
    def onClicked(self):
        self.window.abrir_camera.close()
        self.window.fechar_camera.show()
        self.window.observacao.close()
        # FUNÇÃO QUE ABRE A CÂMERA
        self.window.imgLabel.show()
        try:
            self.cap = cv2.VideoCapture(0)
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                ok = False
                frame, ok = read_barcodes(frame)
                self.displayImage(frame, 1)
                cv2.waitKey(0)
                if ok is True:
                    self.window.regi_saida.show()
                    self.text_saida.setText("Verificando registro...")
                    self.text_saida.setStyleSheet(
                        "background-color: rgb(73, 122, 166);\n"
                        "color: rgb(255, 255, 255);\n"
                        'font: 75 18pt "Arial";\n'
                        "padding-top:5px;\n"
                        "padding-left: 5px;\n"
                        "align: center;"
                    )
                    sleep(1)
                    (
                        nome_aluno,
                        permissao,
                        data_solicitacao,
                        hora_comparacao_fim,
                        hora_comparacao_ini,
                        area,
                        curso,
                        hora_ini,
                        hora_fim,
                        verificacao,
                    ) = dados_aluno()
                    if verificacao is False:
                        self.window.regi_saida.show()
                        self.text_saida.setText(
                            "Aluno não possui\nsolicitação registrada\nPor favor, entrar em contato\ncom o técnico"
                        )
                        self.text_saida.setStyleSheet(
                            "background-color: rgb(73, 122, 166);\n"
                            "color: rgb(255, 255, 255);\n"
                            'font: 75 16pt "Arial";\n'
                            "padding-top:5px;\n"
                            "padding-left: 5px;\n"
                            "align: center;"
                        )
                        sleep(7)
                        self.window.regi_saida.close()

                    else:
                        resposta, nome, h_saida = ponto(util.matricula, util.token)
                        quantidade = verifica_vacinacao(util.token, util.matricula)
                        Horario(HORARIO_ATUAL)

                        if resposta == "Negativo":
                            self.window.regi_saida.close()
                            self.window.CAPA.close()
                            self.window.campus_all.show()
                            data_atual = date.today()
                            data = data_atual.strftime("%d/%m/%Y")
                            if (
                                HD < hora_comparacao_ini
                                or HD > hora_comparacao_fim
                                or data_solicitacao != data
                            ) or quantidade < 2:
                                permissao = "Negado"

                            else:
                                self.window.observacao.close()

                            self.nome_aluno.setText(nome_aluno)
                            self.matricula.setText("Matricula: %s" % util.matricula)
                            self.curso.setText("Curso: %s" % curso)
                            self.espaco_reservado.setText("Espaço Reservado: %s" % area)
                            self.hora_ini.setText("Inicio: %s" % hora_ini)
                            self.hora_fim.setText("Fim: %s" % hora_fim)
                            self.data.setText("Data: %s" % data_solicitacao)
                            # DA SINAL VERMELHO CASO O ACESSO SEJA PERMITIDO
                            if permissao == "Negado":
                                self.detalhes("255", "0", "0")
                                self.window.afirmar.close()
                                self.window.negar.close()
                                self.observacao.show()

                                if quantidade < 2:
                                    self.observacao.setText(
                                        "Não tomou as duas doses da vacina\ncontra Covid-19"
                                    )
                                else:
                                    self.observacao.setText(
                                        "Acesso negado ao campus\nOu fora do horário reservado"
                                    )

                                self.observacao.setStyleSheet(
                                    "background-color: rgb(255, 0, 0);\n"
                                    "color: rgb(0, 0, 0);\n"
                                    'font: 75 14pt "Arial";\n'
                                    "padding-top:5px;\n"
                                    "padding-left: 5px;"
                                )

                                if quantidade == 0:
                                    self.quant_vacina(quantidade)
                                elif quantidade == 1:
                                    self.quant_vacina(quantidade)
                                elif quantidade == 2:
                                    self.quant_vacina(quantidade)

                                sleep(5)
                                self.normal()
                                self.window.CAPA.show()

                            # DA SINAL VERDE CASO O ACESSO SEJA PERMITIDO
                            elif permissao == "Permitido" and quantidade == 2:
                                self.detalhes("73", "122", "166")
                                self.window.afirmar.show()
                                self.window.negar.show()
                                self.quant_vacina(quantidade)

                        elif resposta == "Positivo":
                            self.window.regi_saida.show()
                            self.text_saida.setText(
                                f"{nome}\nRegistrando Horário de Saída\nàs {h_saida}"
                            )
                            self.text_saida.setStyleSheet(
                                "background-color: rgb(73, 122, 166);\n"
                                "color: rgb(255, 255, 255);\n"
                                'font: 75 14pt "Arial";\n'
                                "padding-top:5px;\n"
                                "padding-left: 5px;\n"
                                "align: center;"
                            )
                            sleep(3)
                            self.window.regi_saida.close()

                    # VERIFICA A HORA E O DIA ATUAL DO SISTEMA E COMPARA COM A HORA DE CHEGADA DO ALUNO E O DIA SOLICITADO
                    # CASO O ALUNO ESTEJA FORA DO HORÁRIO OU DO DIA RESERVADO, O ACESSO SERÁ NEGADO

                elif ok is False:
                    self.window.CAPA.show()

                if self.logic == 2:
                    continue

                elif self.logic == 3:
                    break

                elif self.logic == 4:
                    # FECHA A CAMERA
                    self.cap.release()
                    self.window.imgLabel.close()
                    self.window.fechar_camera.close()
                    self.window.abrir_camera.show()
                    self.logic = 0
                    self.window.CAPA.show()
        except:
            self.window.regi_saida.show()
            self.text_saida.setText(
                "Problemas técnicos no sistema\nPor favor, contatar o técnico"
            )
            self.text_saida.setStyleSheet(
                "background-color: rgb(73, 122, 166);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 75 16pt "Arial";\n'
                "padding-top:5px;\n"
                "padding-left: 5px;\n"
                "align: center;"
            )
            sleep(7)
            self.window.regi_saida.close()
            self.window.imgLabel.close()
            self.window.fechar_camera.close()
            self.window.abrir_camera.show()

        self.cap.release()
        cv2.destroyAllWindows()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Deseja retornar à tela de login?")
        close.setStyleSheet(
            "background-color: rgb(255,255,255);\n"
            "color: rgb(28, 41, 48);\n"
            'font: 75 12pt "Arial";\n'
        )

        close.setWindowTitle("SCAC - Minha Vida Acadêmica")
        close.setWindowIcon(QIcon("_imagens/icon.ico"))
        close.setIcon(QMessageBox.Warning)
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            self.logic = 3
            self.window.close()
            confirma(cond=True)
        elif close == QMessageBox.Cancel:
            if not type(event) == bool:
                event.ignore()
                self.logic = 2

    def CloseCapture(self):
        self.logic = 4

    def opcao_temp(self):
        self.window.aviso_temp.show()

    def autorizar(self):
        self.detalhes("73", "122", "166")
        self.window.observacao.close()
        self.opcao_temp()

    def quant_vacina(self, quantidade):
        if quantidade == 0:
            self.window.p_dose_all.setStyleSheet(
                "background-color: rgb(157, 157, 157);"
            )
            self.window.fig_vac_1.setStyleSheet(
                "image: url(:/newPrefix/2646111.png);\n"
                "background-color: rgb(157, 157, 157);"
            )
            self.window.p_dose_n.setStyleSheet("background-color: rgb(157, 157, 157);")
            self.window.s_dose_all.setStyleSheet(
                "background-color: rgb(157, 157, 157);"
            )
            self.window.fig_vac_2.setStyleSheet(
                "image: url(:/newPrefix/2646111.png);\n"
                "background-color: rgb(157, 157, 157);"
            )
            self.window.s_dose_n.setStyleSheet("background-color: rgb(157, 157, 157);")
        elif quantidade == 1:
            self.window.p_dose_all.setStyleSheet(
                "background-color: rgb(157, 157, 157);"
            )
            self.window.fig_vac_1.setStyleSheet(
                "image: url(:/newPrefix/2646111.png);\n"
                "background-color: rgb(157, 157, 157);"
            )
            self.window.p_dose_n.setStyleSheet("background-color: rgb(157, 157, 157);")
        elif quantidade == 2:
            self.window.p_dose_all.setStyleSheet("background-color: rgb(73, 122, 166);")
            self.window.fig_vac_1.setStyleSheet(
                "image: url(:/newPrefix/2646111.png);\n"
                "background-color: rgb(73, 122, 166);"
            )
            self.window.p_dose_n.setStyleSheet("background-color: rgb(73, 122, 166);")
            self.window.s_dose_all.setStyleSheet("background-color: rgb(73, 122, 166);")
            self.window.fig_vac_2.setStyleSheet(
                "image: url(:/newPrefix/2646111.png);\n"
                "background-color: rgb(73, 122, 166);"
            )
            self.window.s_dose_n.setStyleSheet("background-color: rgb(73, 122, 166);")

    def nao_autorizar(self):
        self.detalhes("255", "0", "0")
        self.observacao.setStyleSheet(
            "background-color: rgb(255, 0, 0);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;"
        )
        self.window.observacao.show()
        self.observacao.setText("Não cumpriu os requisitos mínimos")
        self.opcao_temp()

    def detalhes(self, r, g, b):
        self.nome_aluno.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

        self.curso.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

        self.hora_ini.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

        self.matricula.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

        self.hora_fim.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )
        self.data.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

        self.espaco_reservado.setStyleSheet(
            "background-color: rgb(%s, %s, %s);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;" % (r, g, b)
        )

    def normal(self):
        _translate = QtCore.QCoreApplication.translate
        self.window.aviso_temp.close()
        self.window.nome_aluno.setText(_translate("MainWindow", "Nome do Aluno"))
        self.window.matricula.setText(_translate("MainWindow", "Matricula"))
        self.window.curso.setText(_translate("MainWindow", "Curso"))
        self.window.espaco_reservado.setText(
            _translate("MainWindow", "Espaço Reservado")
        )
        self.window.data.setText(_translate("MainWindow", "Data Reservada"))
        self.window.hora_ini.setText(_translate("MainWindow", "Entrada"))
        self.window.hora_fim.setText(_translate("MainWindow", "Saída"))
        self.window.observacao.close()
        self.detalhes("255", "255", "255")

    def opcao_nao(self):
        self.normal()
        hora_ini = util.horario
        dict_dados = {"entrada": hora_ini, "saida": "00:00:00", "temperatura": "NULL"}
        enviar_dados(util.token, util.matricula, dict_dados)
        self.window.CAPA.show()

    def opcao_sim(self):
        self.window.temp.show()
        self.window.aviso_temp.close()

    def salvar_temp(self):
        temperatura = self.window.temperatura.text()
        hora_ini = util.horario
        try:
            dict_dados = {
                "entrada": hora_ini,
                "saida": "00:00:00",
                "temperatura": float(temperatura),
            }
            enviar_dados(util.token, util.matricula, dict_dados)
            self.window.aviso_2.setText("Insira a temperatura")
            self.window.aviso_1.setText("Apenas Números")
            self.window.temp.close()
            temperatura = self.window.temperatura.clear()
            self.normal()
            self.window.CAPA.show()

        except:
            self.window.aviso_2.setText("Dados não conferem")
            self.window.aviso_1.setText("")
            sleep(1)
            self.window.aviso_2.setText("Insira a temperatura")
            self.window.aviso_1.setText("Apenas Números")
            self.window.temp.close()
            temperatura = self.window.temperatura.clear()

    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if (img.shape[2]) == 4:
                qformat = QImage.Format_RGBA888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.scaled(1250, 700, QtCore.Qt.KeepAspectRatio)
        img = img.rgbSwapped()

        self.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
