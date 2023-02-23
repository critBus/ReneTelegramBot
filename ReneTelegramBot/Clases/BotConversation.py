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

from ReneTelegramBot.Utiles.TBUtiles import *
from ReneTelegramBot.Utiles.TBUtiles import _enviarTecladoMenu,_banearUsuarioEsteUsuario,_enviarMensaje,_getArgsDeComando,_getUsuarioDeTelegramFrom,_getStrMark,_getTextDeMensaje
from ReneTelegramBot.Clases.TBClases import *

from ReneTelegramBot.Clases.TBClases import _BotonMenuInicial
import re
class SoporteDeBot:
    def estaEnMantenimiento(self)->bool:
        return False
    def accionEnMantenimiento(self,u,c)->None:
        pass
    def estaLogeado(self,u,c)->bool:
        return True
    def loguear(self,u,c):
        pass

class BotConversation:
    def __init__(self, token:str):
        self.updater:Updater = Updater(token=token, use_context=True)
        self.dispatcher:Dispatcher = self.updater.dispatcher
        self.__textoEnMenuDefault=None
        self.textoSiNoEstaLogueadoOAunEnMantenimiento=None

    def setTextoEnMenuDefault(self,textoEnMenuDefault):
        self.__textoEnMenuDefault=textoEnMenuDefault
    def __ponerTextoEnMenuDefault(self,teclado:Teclado):
        # print("poner texto ")
        if isinstance(teclado,Teclado):
            # print("default=",self.__textoEnMenuDefault)
            # print("teclado.textoDeMenu=",teclado.textoDeMenu)
            # print("TEXTO_EN_MENU_DEFAULT=",TEXTO_EN_MENU_DEFAULT)
            # print("(self.__textoEnMenuDefault is not None)=",(self.__textoEnMenuDefault is not None))
            # print("(teclado.textoDeMenu==TEXTO_EN_MENU_DEFAULT)=",teclado.textoDeMenu==TEXTO_EN_MENU_DEFAULT)
            if (self.__textoEnMenuDefault is not None) and teclado.textoDeMenu==TEXTO_EN_MENU_DEFAULT:
                # print("lo puso !!!!!!!!!!!!!!!!!!!!!")
                teclado.textoDeMenu=self.__textoEnMenuDefault
    def __enviarTecladoMenu(self,update,ctx,menuDeBotonesC):
        self.__ponerTextoEnMenuDefault(menuDeBotonesC)
        _enviarTecladoMenu(update, ctx, menuDeBotonesC)

    def __setMenuInicial(self,menuDeBotonesC:MenuDeBotonesC,textoDelBoton:str,metodoComando=None):
        OPCION_MENU_SIGUIENTE = getNumeroOpcionActual()

        def metodoMenuInicial( update,ctx):
            self.__enviarTecladoMenu(update,ctx,menuDeBotonesC)
            #_enviarTecladoMenu(update,ctx,menuDeBotonesC)
            if metodoComando!=None:
                metodoComando(update,ctx)
            return(OPCION_MENU_SIGUIENTE)

        botonMenuInicial = BotonDeMenuC(textoDeboton=textoDelBoton, metodoComando=metodoMenuInicial,
                                        opcionComando=OPCION_MENU_SIGUIENTE)
        self.__botonMenuInicial:_BotonMenuInicial=_BotonMenuInicial(botonMenuInicial,menuDeBotonesC)
        self.__states[OPCION_MENU_SIGUIENTE]=self.__crearHandler(self.__botonMenuInicial.menuDeBotonesC,self.__botonMenuInicial)#update,ctx,

    def sendMensaje(self,chat_id,text):
        try:
            self.updater.bot.sendMessage(chat_id,text)
        except Exception as ex:
            try:
                text=_getStrMark(text)
                self.updater.bot.sendMessage(chat_id,text)
            except Exception as ex:
                try:
                    self.updater.bot.sendMessage(chat_id=chat_id,text= text, parse_mode=ParseMode.HTML)
                except Exception as ex:
                    verException()

    def __getSalidaCorrecta(self,update, ctx,metodo):
        if metodo!=None:
            res = metodo(update, ctx)
            if isinstance(res, OpcionDeSalida):
                iaccion=res.iaccionComando
                if iaccion!=None:
                    return iaccion.metodoComando(update, ctx)
                #_enviarTecladoMenu(update, ctx, self.__botonMenuInicial.menuDeBotonesC)
                self.__enviarTecladoMenu(update, ctx, self.__botonMenuInicial.menuDeBotonesC)
                return self.__botonMenuInicial.opcionComando

            if isinstance(res, IAccionComando):
                if res.metodoComando != None:
                    return res.metodoComando(update, ctx)
            return res
        return None
    def __procesarInputt(self,iParaInputt:IParaInputt,parent:IAccionComando):#,parent#,update,ctx
        inputt:Inputt=iParaInputt.inputt

        accionDelinputt0 = inputt.metodoComando

        def accionConRespuestaDelInput(update, ctx):
            return self.__getSalidaCorrecta(update, ctx,accionDelinputt0)


        inputt.metodoComando = accionConRespuestaDelInput

        if inputt.ponerBotonCancelar:
            textoCancelar="🔙 Cancelar"
            inputt.addTextoAlMenuSoloTextoEnBotones(textoCancelar)


            accionDelinputt=inputt.metodoComando

            def accionConCancelar(update, ctx):
                text: str = update.message.text
                if text == textoCancelar:
                    return(parent.metodoComando(update,ctx))
                elif accionDelinputt!=None:
                    valorRetornado=accionDelinputt(update,ctx)
                    if valorRetornado!=None:
                        return(valorRetornado)
                    else:
                        if isinstance(parent,_BotonMenuInicial):
                            #_enviarTecladoMenu(update, ctx, self.__botonMenuInicial.menuDeBotonesC)
                            self.__enviarTecladoMenu(update, ctx, self.__botonMenuInicial.menuDeBotonesC)
                            return self.__botonMenuInicial.opcionComando
                        else:
                            return iParaInputt.opcionComando
            inputt.metodoComando=accionConCancelar

        accionAllamarDeiParaInputt=iParaInputt.metodoComando

        def accionDeliParaInputt(update, ctx):
            #print("Entra en i para input")
            if inputt.tieneBotones():
                #_enviarTecladoMenu(update, ctx,inputt)
                self.__enviarTecladoMenu(update, ctx,inputt)
                #print("enviar teclado i para input")
            if accionAllamarDeiParaInputt!=None:
                accionAllamarDeiParaInputt(update,ctx)
            return(iParaInputt.opcionComando)

        iParaInputt.metodoComando=accionDeliParaInputt
        filtros=Filters.regex("(.+)")
        if inputt.tipo!=Filters.text:
            filtros=filtros|inputt.tipo
        self.__states[iParaInputt.opcionComando]=[MessageHandler(filtros, inputt.metodoComando)]

        if inputt.hayEncadenados():
            for i in range(len(inputt.encadenados)):
                disparador=inputt.encadenados[i]
                if isinstance(disparador,ITieneMenu) and isinstance(disparador,IAccionComando):
                    self.__ponerIAccion(disparador, iParaInputt)#update,ctx
                    self.__states[disparador.opcionComando] =self.__crearHandler(disparador.menuDeBotonesC,iParaInputt)#update,ctx,
                else:
                    self.__procesarInputt(disparador,iParaInputt)#update,ctx,

    def __ponerIAccion(self,iaccion:IAccionComando,parent):#update,ctx,
        #def crearAccion(iaccion:IAccionComando):
        esITieneMenu: bool = isinstance(iaccion, ITieneMenu)
        if esITieneMenu:
            nuevoBotonAtras = BotonRetroceder(textoDeboton="🔙 Atrás",parent=parent)
            iaccion.menuDeBotonesC.addBoton(nuevoBotonAtras)


            self.__states[iaccion.opcionComando] = self.__crearHandler(iaccion.menuDeBotonesC,iaccion)#update,ctx,

        accionDeBoton=iaccion.metodoComando

        esBotonRetroceder = isinstance(iaccion, BotonRetroceder)
        def accion( update,ctx):
            if esITieneMenu or esBotonRetroceder:
                if iaccion.menuDeBotonesC!=None:
                    #_enviarTecladoMenu( update,ctx, iaccion.menuDeBotonesC)
                    self.__enviarTecladoMenu(update,ctx, iaccion.menuDeBotonesC)
                else:
                    print("atras correspondiente")
                    if esBotonRetroceder and isinstance(iaccion.parent,IParaInputt):
                        iaccion.parent.metodoComando(update,ctx)

            if   (not esBotonRetroceder):#accionDeBoton!=None and
                salida=self.__getSalidaCorrecta(update, ctx,accionDeBoton)
                if salida!=None:
                    return salida

            if esITieneMenu or esBotonRetroceder:
                #return(opcionMenuCorrespondiente)
                return iaccion.opcionComando




            #return(accion)

        #iaccion.metodoComando=crearAccion(iaccion)
        iaccion.metodoComando = accion


    def __crearHandler(self,menuDeBotonesC:MenuDeBotonesC,parent):#update,ctx,
        listaRegexHandler:List[Handler[Update, CCT]] = []

        listaID_Procesados=[]
        def procesar(elemento:ITextAccionComando):
            if isinstance(elemento, IParaInputt):
                self.__procesarInputt( elemento, parent)#update, ctx,
            else:
                self.__ponerIAccion( elemento, parent)#update, ctx,
            listaRegexHandler.append(
                MessageHandler(Filters.regex("^" + elemento.texto + "$"), elemento.metodoComando))


        listaDeBotones=menuDeBotonesC.getListaDeBotones()#update,ctx
        leng=len(listaDeBotones)
        for i in range(leng):
            boton = listaDeBotones[i]
            listaID_Procesados.append(boton.opcionComando)
            procesar(boton)

        comandosInternos=menuDeBotonesC.getComandosInternos()#update,ctx
        leng = len(comandosInternos)
        for i in range(leng):
            comando=comandosInternos[i]
            listaID_Procesados.append(comando.opcionComando)
            procesar(comando)


        if menuDeBotonesC.hayEncadenados():
            for i in range(len(menuDeBotonesC.encadenados)):
                encadenado=menuDeBotonesC.encadenados[i]
                if not contiene(listaID_Procesados,encadenado.opcionComando):
                    procesar(encadenado)


        return(listaRegexHandler)



    def comenzar(self,getBotonInicial,soporteDeBot=None):
        if soporteDeBot is None:
            soporteDeBot=SoporteDeBot()

        STR_PATRON_ID_TELEGRAM="([0-9]{10})"
        PATRON_ID_TELEGRAM=re.compile(STR_PATRON_ID_TELEGRAM)

        if soporteDeBot.estaEnMantenimiento():
            self.dispatcher.add_handler(CommandHandler("start",soporteDeBot.accionEnMantenimiento ))
        else:

            b: BotonParaMenu = getBotonInicial()
            def accionStart(u,c):
                if soporteDeBot.estaEnMantenimiento():
                    return soporteDeBot.accionEnMantenimiento(u,c)
                referencia=None
                a = _getArgsDeComando(c)
                if a != None and len(a) > 0:
                    a = a[0]
                    find = re.findall(PATRON_ID_TELEGRAM, str(a))
                    if find != None and len(find) > 0:
                        #_enviarMensaje(u, c, "referencia es " + str(find[0]))
                        referencia=str(find[0])
                return b.metodoComando(u, c, referencia)

            self.__states: Dict[object, List[Handler[Update, CCT]]] = {}
            self.__setMenuInicial(b.menuDeBotonesC, b.textoDeboton, accionStart)

            handlerMenuInicial=CommandHandler("start", self.__botonMenuInicial.metodoComando)
            conv_handler = ConversationHandler(
                entry_points=[CommandHandler("start", self.__botonMenuInicial.metodoComando, Filters.regex(STR_PATRON_ID_TELEGRAM))
                              ,handlerMenuInicial
                              ],
                states=self.__states,
                fallbacks=[handlerMenuInicial]
            )
            self.dispatcher.add_handler(conv_handler)


            #self.__crearMenu( b.menuDeBotonesC, b.textoDeboton,metodoConComprobarSiHayReferencia)#u, c,  # lambda p_u,p_c:b.metodoComando(p_u, p_c, referencia)

            # self.dispatcher.add_handler(CommandHandler("start", llamarACrearMenu, Filters.regex(STR_PATRON_ID_TELEGRAM)))
            # self.dispatcher.add_handler(CommandHandler("start", llamarACrearMenu))


        def rastreoEnTodosLosMensajes(update, ctx):
            try:
                # print("rastrea este mensaje 1")


                if soporteDeBot.estaEnMantenimiento or not soporteDeBot.estaLogeado(update, ctx):
                    # print("rastrea este mensaje 3_1")
                    text = _getTextDeMensaje(update)
                    if text == r"/start":
                        # print("rastrea este mensaje 4_1")
                        if (not soporteDeBot.estaEnMantenimiento) and (
                                not soporteDeBot.estaLogeado(update, ctx)):
                            # print("rastrea este mensaje 5_1")
                            soporteDeBot.loguear(update, ctx)
                            return None
                    else:
                        # print("rastrea este mensaje 6_1")
                        # _enviarMensaje(update, ctx, "llame al comando "+r"/start")
                        _enviarMensaje(update, ctx, self.textoSiNoEstaLogueadoOAunEnMantenimiento)
                    return ConversationHandler.END
                else:
                    # print("rastrea este mensaje 2_1")
                    pass


                msg = update.message
                if msg.new_chat_members != None:
                    for user in msg.new_chat_members:
                        if user.is_bot:
                            _enviarMensaje(update, ctx, "Va a ser baneado por ser bot")
                            _banearUsuarioEsteUsuario(update)


                # else:
                #     print("rastrea este mensaje 2")
                #     if soporteDeBot.estaEnMantenimiento or not soporteDeBot.estaLogeado(update, ctx):
                #         print("rastrea este mensaje 3")
                #         text=_getTextDeMensaje(update)
                #         if text==r"/start":
                #             print("rastrea este mensaje 4")
                #             if (not soporteDeBot.estaEnMantenimiento) and (not soporteDeBot.estaLogeado(update, ctx)):
                #                 print("rastrea este mensaje 5")
                #                 soporteDeBot.loguear(update, ctx)
                #                 return None
                #         else:
                #             print("rastrea este mensaje 6")
                #             #_enviarMensaje(update, ctx, "llame al comando "+r"/start")
                #             _enviarMensaje(update, ctx, self.textoSiNoEstaLogueadoOAunEnMantenimiento)
                #         return ConversationHandler.END

            except:
                print("rastrea este mensaje error")
                #pass

        self.dispatcher.add_handler(MessageHandler(Filters.regex("(.*)"), rastreoEnTodosLosMensajes))



        self.updater.start_polling(allowed_updates=[])
        self.updater.idle()

        # menuDeBotonesC:MenuDeBotonesC,textoDelBoton:str,metodoComando=None
        # class AlmacenReferencia:
        #     def __init__(self,referencia,idt):
        #         self.referencia=referencia
        #         self.idt=idt
        # def llamarACrearMenu(u,c):#,referencia=None
        #     b:BotonParaMenu=getBotonInicial(u,c)
        #     referencia = AlmacenReferencia(None,str(_getUsuarioDeTelegramFrom(u).id))
        #     a = _getArgsDeComando(c)
        #     if a != None and len(a) > 0:
        #         a = a[0]
        #         find = re.findall(PATRON_ID_TELEGRAM, str(a))
        #         if find != None and len(find) > 0:
        #             _enviarMensaje(u, c, "referencia es " + str(find[0]))
        #             referencia.referencia=str(find[0])
        #             #referencia = AlmacenReferencia(str(find[0]),str(_getUsuarioDeTelegramFrom(u).id))
        #
        #     def metodoConComprobarSiHayReferencia(u,c):
        #
        #         # print("referencia=",referencia.referencia," ut=",referencia.idt)
        #         # _enviarMensaje(u, c, strg("2referencia=",referencia.referencia," ut=",referencia.idt))
        #
        #         return b.metodoComando(u, c, referencia.referencia)
        #
        #
        #     self.__crearMenu(u,c,b.menuDeBotonesC,b.textoDeboton,metodoConComprobarSiHayReferencia)#lambda p_u,p_c:b.metodoComando(p_u, p_c, referencia)


    # def __crearMenu(self,menuDeBotonesC:MenuDeBotonesC,textoDelBoton:str,metodoComando=None):#update,ctx,
    #     self.__states: Dict[object, List[Handler[Update, CCT]]] = {}
    #     self.__setMenuInicial(menuDeBotonesC,textoDelBoton,metodoComando)#update,ctx,
    #     # _enviarTecladoMenu(update,ctx,MenuDeBotonesC(
    #     #     matrizDeBotones=[[BotonDeMenuC(textoDeboton=self.__botonMenuInicial.textoDeboton)]]
    #     #     ,textoDeMenu="Para loquearse escriba *"+self.__botonMenuInicial.textoDeboton+"* o seleccionelo en el menu"
    #     # ))
    #
    #     handlerMenuInicial = MessageHandler((Filters.regex("^" + self.__botonMenuInicial.textoDeboton + "$")),#|Filters.regex("^[/]start$")
    #                                       self.__botonMenuInicial.metodoComando)
    #
    #
    #     conv_handler = ConversationHandler(
    #         entry_points=[handlerMenuInicial],
    #         states=self.__states,
    #         fallbacks=[handlerMenuInicial]
    #     )
    #     self.dispatcher.add_handler(conv_handler)
    #
    #     def rastreoEnTodosLosMensajes(update,ctx):
    #         try:
    #             msg=update.message
    #             if msg.new_chat_members!=None:
    #                 for user in msg.new_chat_members:
    #                     if user.is_bot:
    #                         _enviarMensaje(update,ctx,"Va a ser baneado por ser bot")
    #                         _banearUsuarioEsteUsuario(update)
    #         except:
    #             pass
    #
    #     self.dispatcher.add_handler(MessageHandler(Filters.regex("(.*)"), rastreoEnTodosLosMensajes))
    #
