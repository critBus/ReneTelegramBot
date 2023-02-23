from ..Clases.TBClases import *
from telegram.utils import helpers
def _getTextDeMensaje(update):
    return update.message.text
def _getUsuarioDeTelegramFrom(update):
    #user = update.message.from_user
    user = update.effective_message.from_user
    return UsuarioDeTelegram(id=user.id,first_name=user.first_name,last_name=user.last_name
                             ,username=user.username,is_bot=user.is_bot,link=user.link)
def _getChatDeTelgram_DeMensaje(update):
    #chat =update.message.chat
    chat = update.effective_message.chat
    return ChatDeTelegram(id=chat.id,type=chat.type,title=chat.title,first_name=chat.first_name
                          ,last_name=chat.last_name,username=chat.username
                          ,invite_link=chat.invite_link,linked_chat_id=chat.linked_chat_id
                          ,link=chat.link)

def _banearUsuarioEsteUsuario(update):
    user = update.message.from_user
    chat = update.message.chat
    user.decline_join_request(chat.id)
def _deleteMensaje(update):
    update.message.delete()
def _esReplyMensaje(update):
    return update.message.reply_to_message!=None
def _getReplyMensaje(update):
    return update.message.reply_to_message
def _getTextDeReplyMensaje(update):
    return _getReplyMensaje(update).text
def _esDocumento(update):
    return update.message.document!=None
def _descargarDocumento(update,carpeta,nombre):
    url=carpeta+"/"+nombre
    update.message.document.get_file().download(url)
    return url
def _esAudio(update):
    return update.message.audio!=None
def _descargarAudio(update,carpeta,nombre):
    url=carpeta+"/"+nombre
    update.message.audio.get_file().download(url)
    return url
def _getDocumento(update):
    doc=update.message.document
    return DocumentoDeTelgram(file_id=doc.file_id,file_unique_id=doc.file_unique_id,file_name=doc.file_name,mime_type=doc.mime_type,file_size=doc.file_size)

def _tieneFotos(update):
    lf=update.message.photo
    return lf!=None and len(lf)>0
def _descargarFotos(update,carpeta,nombreGenerico):

    lf = update.message.photo
    Lurl=[]
    leng=len(lf)
    for i in range(lf):
        url = carpeta + "/" + nombreGenerico+"%03d"%(i)
        update.message.lf[i].get_file().download(url)
        Lurl.append(url)

    return Lurl

def _esVideo(update):
    return update.message.video!=None
def _descargarVideo(update,carpeta,nombre):
    url=carpeta+"/"+nombre
    update.message.video.get_file().download(url)
    return url

def _esVoz(update):
    return update.message.voice!=None
def _descargarVoz(update,carpeta,nombre):
    url=carpeta+"/"+nombre
    update.message.voice.get_file().download(url)
    return url

def _enviarTecladoMenu( update,ctx,menuDeBotonesC:Teclado):
    reply_keyboard = menuDeBotonesC.getMenuSoloTextoEnBotones(update,ctx)
    # print("se lanza teclado")
    update.message.reply_text(
        menuDeBotonesC.getTextoDeMenu(update,ctx),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=False,
                                         resize_keyboard=True))

def _enviarMensaje(update,ctx,mensaje:str,chat_id=None):
    #updater.message.reply_text(mensaje)
    try:
        if chat_id==None:
            try:
                update.message.reply_text(mensaje)
                #update.message.reply_markdown(_getStrMark(mensaje))
            except:
                update.message.reply_text(mensaje)
        else:
            bot=ctx.bot
            try:
                bot.send_message(chat_id,mensaje,parse_mode=ParseMode.MARKDOWN)
            except:
                bot.send_message(chat_id, mensaje)
    except:
        verException()
def _getMessageID(update,ctx):
    return update.message.message_id

def _getArgsDeComando(context):
    return context.args
def _getUrlReferencia(update,context):
    bot = context.bot
    return helpers.create_deep_linked_url(bot.username, str(_getUsuarioDeTelegramFrom(update).id))

def _enviarDoc(update,url,nombre=None):
    arregloBinario=Archivo.readBinaryData(url)
    chat = update.message.chat
    chat.send_document(arregloBinario,nombre)
def _quitarTodosLosComandos(context):
    bot = context.bot
    bot.deleteMyCommands()

def _getStrMark(mensaje):
    return replaceAll(mensaje,"_",r"\_","*",r"\*","[",r"\[","]",r"\]","(",r"\(",")",r"\)","~",r"\~","`",r"\`",">",r"\>","#",r"\#","+",r"\+","-",r"\-","=",r"\=","|",r"\|","{",r"\{","}",r"\}",".",r"\.","!",r"\!")