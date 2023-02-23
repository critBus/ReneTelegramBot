import os
from telegram import Bot, ParseMode
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,Dispatcher
from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import CallbackQueryHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext import (
    BasePersistence,
    CallbackContext,

    ChosenInlineResultHandler,
    DispatcherHandlerStop,
    Handler,
    InlineQueryHandler,
)
from telegram.ext.utils.types import CCT

from telegram import InlineQueryResultArticle, InputTextMessageContent
#from telegram.ext import InlineQueryHandler

from typing import TYPE_CHECKING, Dict, List, NoReturn, Optional, Union, Tuple, cast, ClassVar


from RenePy.Utiles import *



NumeroOpcionActual:int=1000
def getNumeroOpcionActual():
    global NumeroOpcionActual
    NumeroOpcionActual=NumeroOpcionActual+1
    return(NumeroOpcionActual+0)

class IAccionComando:
    def __init__(self,metodoComando=None,opcionComando:int=None):
        if opcionComando == None:
            opcionComando = getNumeroOpcionActual()

        self.opcionComando:int=opcionComando
        self.metodoComando=metodoComando
class ITextAccionComando(IAccionComando):
    def __init__(self, texto: str, metodoComando=None, opcionComando: int = None):
        self.texto: str = texto
        IAccionComando.__init__(self, metodoComando=metodoComando, opcionComando=opcionComando)

class IEncadenados:
    def __init__(self,encadenados:List=None):
        if encadenados==None:
            encadenados=[]
        self.encadenados:List=encadenados
    def hayEncadenados(self):
        return len(self.encadenados)>0

class BotonDeMenuC(ITextAccionComando):
    def __init__(self, textoDeboton:str,metodoComando=None,opcionComando:int=None):
        self.textoDeboton:str=textoDeboton
        ITextAccionComando.__init__(self,texto=textoDeboton,metodoComando=metodoComando,opcionComando=opcionComando)

class ComandoEnMenu(ITextAccionComando):
    def __init__(self, textoDeComando:str,metodoComando=None,opcionComando:int=None):
        self.textoDeboton:str=textoDeComando
        ITextAccionComando.__init__(self,texto=textoDeComando,metodoComando=metodoComando,opcionComando=opcionComando)
TEXTO_EN_MENU_DEFAULT="Selecciona una opcion del menu"
class Teclado(IEncadenados):
    def __init__(self,menuSoloTextoEnBotones,textoDeMenu=None,encadenados:List=None):
        if menuSoloTextoEnBotones is None:
            menuSoloTextoEnBotones=[]
        if textoDeMenu is None:
            textoDeMenu=TEXTO_EN_MENU_DEFAULT
        self.textoDeMenu=textoDeMenu
        self.__menuSoloTextoEnBotones = menuSoloTextoEnBotones
        IEncadenados.__init__(self, encadenados=encadenados)
    def getMenuSoloTextoEnBotones(self,update=None,ctx=None):
        if esFuncion(self.__menuSoloTextoEnBotones):
            return self.__menuSoloTextoEnBotones(update,ctx)
        return self.__menuSoloTextoEnBotones
    def tieneBotones(self):
        return len(self.getMenuSoloTextoEnBotones())>0
    def getTextoDeMenu(self,update=None,ctx=None):
        if esFuncion(self.textoDeMenu):
            return self.textoDeMenu(update,ctx)
        return self.textoDeMenu

    def addTextoAlMenuSoloTextoEnBotones(self,texto:str):
        getMenuSoloTextoEnBotones = self.getMenuSoloTextoEnBotones
        def getMenuSoloTextoEnBotonesAgregado(update=None,ctx=None):
            menu=getMenuSoloTextoEnBotones(update,ctx)
            if not contiene(menu,[texto]):
                menu.append([texto])
            return menu
        self.getMenuSoloTextoEnBotones=getMenuSoloTextoEnBotonesAgregado



class MenuDeBotonesC(Teclado):
    def __init__(self, matrizDeBotones,textoDeMenu=None,comandosInternos=None,encadenados:List=None):
        """

        :param matrizDeBotones:  List[List[BotonDeMenuC]] o function(update,ctx)
        :param textoDeMenu:
        :param comandosInternos: List[ComandoEnMenu] o function(update,ctx)
        """
        #:List[List[BotonDeMenuC]]
        #:List[ComandoEnMenu]
        if comandosInternos==None:
            comandosInternos=[]
        self.__matrizDeBotones = matrizDeBotones

        def getMenuSoloTextoEnBotones( update=None, ctx=None):
            menuSoloTextoEnBotones: List[List[str]] = []
            if esFuncion(matrizDeBotones):
                submatriz = matrizDeBotones(update, ctx)
            else:
                submatriz = matrizDeBotones
            for filaBotones in submatriz:
                filaTemporalDeTexoEnBotones: List[str] = []
                for botonDeMenu in filaBotones:
                    filaTemporalDeTexoEnBotones.append(botonDeMenu.textoDeboton)
                menuSoloTextoEnBotones.append(filaTemporalDeTexoEnBotones)
            return menuSoloTextoEnBotones
        super().__init__(menuSoloTextoEnBotones=getMenuSoloTextoEnBotones,textoDeMenu=textoDeMenu,encadenados=encadenados)



        self.__comandosInternos=comandosInternos
    def getComandosInternos(self):#,update=None,ctx=None
        # if esFuncion(self.__comandosInternos):
        #     comandosInternos=self.__comandosInternos(update,ctx)
        # else:
        #     comandosInternos=self.__comandosInternos
        # return comandosInternos
        return self.__comandosInternos
    def getListaDeBotones(self,update=None,ctx=None):
        listaDeBotones: List[BotonDeMenuC] = []
        if esFuncion(self.__matrizDeBotones):
            matrizDeBotones=self.__matrizDeBotones(update,ctx)
        else:
            matrizDeBotones=self.__matrizDeBotones
        for filaBotones in matrizDeBotones:
            #filaTemporalDeTexoEnBotones: List[str] = []
            for botonDeMenu in filaBotones:
                #filaTemporalDeTexoEnBotones.append(botonDeMenu.textoDeboton)
                listaDeBotones.append(botonDeMenu)
        return listaDeBotones

    def addBoton(self,boton:BotonDeMenuC):


        getMenuSoloTextoEnBotones=self.getMenuSoloTextoEnBotones
        def getMenuSoloTextoEnBotonesAgregado(update=None,ctx=None):
            menu=getMenuSoloTextoEnBotones(update,ctx)
            menu.append([boton.textoDeboton])
            return menu
        self.getMenuSoloTextoEnBotones=getMenuSoloTextoEnBotonesAgregado

        getListaDeBotones=self.getListaDeBotones
        def getListaDeBotonesAgregado(update=None,ctx=None):
            menu = getListaDeBotones(update, ctx)
            menu.append(boton)
            return menu
        self.getListaDeBotones=getListaDeBotonesAgregado




        #self.menuSoloTextoEnBotones.append([boton.textoDeboton])
        #self.listaDeBotones.append(boton)
        # self.matrizDeBotones.append([boton])


class Inputt(Teclado):#IAccionComando
    def __init__(self,metodoComando,textoDeMenu,menuSoloTextoEnBotones=None,ponerBotonCancelar:bool=True,encadenados:List=None,tipo=Filters.text):#opcionComando:int=None
        """

        :param metodoComando:
        :param textoDeMenu:
        :param menuSoloTextoEnBotones: List[List[str]] o function(update,ctx)
        :param ponerBotonCancelar:
        :param encadenados:
        :param tipo:
        """
        #:List[List[str]]
        if menuSoloTextoEnBotones==None:
            menuSoloTextoEnBotones=[]
        super().__init__(menuSoloTextoEnBotones=menuSoloTextoEnBotones,textoDeMenu=textoDeMenu,encadenados=encadenados)
        #IEncadenados.__init__(self,encadenados=encadenados)
        self.metodoComando=metodoComando
        self.ponerBotonCancelar:bool=ponerBotonCancelar
        # if encadenados==None:
        #     encadenados=[]
        # self.encadenados:List=encadenados
        self.tipo=tipo

    # def hayEnencadenadosdos(self):
    #     return len(self.encadenados)>0

class IParaInputt:
    def __init__(self,inputt:Inputt):
        self.inputt=inputt

class ITieneMenu:
    def __init__(self,menuDeBotonesC:MenuDeBotonesC):
        self.menuDeBotonesC: MenuDeBotonesC = menuDeBotonesC

class _BotonMenuInicial(BotonDeMenuC,ITieneMenu):
    def __init__(self, botonMenuInicial:BotonDeMenuC,menuDeBotonesC:MenuDeBotonesC):
        self.botonMenuInicial:BotonDeMenuC=botonMenuInicial
        #self.menuDeBotonesC:MenuDeBotonesC=menuDeBotonesC
        super().__init__(textoDeboton=botonMenuInicial.textoDeboton,metodoComando=botonMenuInicial.metodoComando,opcionComando=botonMenuInicial.opcionComando)
        ITieneMenu.__init__(self,menuDeBotonesC=menuDeBotonesC)

class BotonParaMenu(BotonDeMenuC,ITieneMenu):
    def __init__(self,textoDeboton:str,menuDeBotonesC:MenuDeBotonesC,metodoComando=None,opcionComando:int=None):
        # if opcionComando == None:
        #     opcionComando = getNumeroOpcionActual()
        super().__init__(textoDeboton=textoDeboton,metodoComando=metodoComando,opcionComando=opcionComando)
        #self.menuDeBotonesC:MenuDeBotonesC=menuDeBotonesC
        ITieneMenu.__init__(self, menuDeBotonesC=menuDeBotonesC)
class ComandoParaMenu(ComandoEnMenu,ITieneMenu):
    def __init__(self,textoDeComando:str,menuDeBotonesC:MenuDeBotonesC,metodoComando=None,opcionComando:int=None):
        # if opcionComando == None:
        #     opcionComando = getNumeroOpcionActual()
        super().__init__(textoDeComando=textoDeComando,metodoComando=metodoComando,opcionComando=opcionComando)
        ITieneMenu.__init__(self, menuDeBotonesC=menuDeBotonesC)
class BotonParaInputt(BotonDeMenuC,IParaInputt):
    def __init__(self,textoDeboton:str,inputt:Inputt,metodoComando=None,opcionComando:int=None):
        super().__init__(textoDeboton=textoDeboton, metodoComando=metodoComando, opcionComando=opcionComando)
        IParaInputt.__init__(self,inputt=inputt)
class ComandoParaInputt(ComandoEnMenu,IParaInputt):
    def __init__(self,textoDeComando:str,inputt:Inputt,metodoComando=None,opcionComando:int=None):
        super().__init__(textoDeComando=textoDeComando, metodoComando=metodoComando, opcionComando=opcionComando)
        IParaInputt.__init__(self,inputt=inputt)
class AccionParaInputt(IAccionComando,IParaInputt):
    def __init__(self,inputt:Inputt,metodoComando=None,opcionComando:int=None):
        IAccionComando.__init__(self, metodoComando=metodoComando, opcionComando=opcionComando)
        IParaInputt.__init__(self,inputt=inputt)

class AccionParaMenu(IAccionComando,ITieneMenu):
    def __init__(self,menuDeBotonesC:MenuDeBotonesC,metodoComando=None,opcionComando:int=None):
        super().__init__(metodoComando=metodoComando,opcionComando=opcionComando)
        ITieneMenu.__init__(self, menuDeBotonesC=menuDeBotonesC)

class BotonRetroceder(BotonDeMenuC):
    def __init__(self,textoDeboton:str,parent,metodoComando=None):
        super().__init__(textoDeboton=textoDeboton, metodoComando=None, opcionComando=parent.opcionComando)
        if isinstance(parent,ITieneMenu):
            self.menuDeBotonesC: MenuDeBotonesC = parent.menuDeBotonesC
        else:
        #elif isinstance(IParaInputt):
            self.menuDeBotonesC =None#parent.inputt.
        self.parent=parent


class UsuarioDeTelegram:
    def __init__(self,id,first_name,last_name,username,is_bot,link  ):
        self.first_name:str=first_name
        self.id:int=id
        self.last_name:str=last_name
        self.username:str=username
        self.is_bot:bool=is_bot
        self.link = link
class ChatDeTelegram:
    def __init__(self, id, type, title, first_name,last_name,username,invite_link,linked_chat_id,link):
        self.id=id
        self.type = type
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.invite_link = invite_link
        self.linked_chat_id = linked_chat_id
        self.link = link
class DocumentoDeTelgram:
    def __init__(self, file_id, file_unique_id , file_name , mime_type , file_size ):
        self.file_id=file_id
        self.file_unique_id = file_unique_id
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

class OpcionDeSalida:
    def __init__(self,iaccionComando:IAccionComando=None):
        self.iaccionComando:IAccionComando=iaccionComando

