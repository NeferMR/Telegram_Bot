from enchant.checker import SpellChecker
from telegram.ext import Updater, CommandHandler, ConversationHandler,CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, chataction
import enchant, operator
from collections import Counter

#Se importa el diccionario en español, necesario para la interpretación
d = enchant.Dict('es_CO')

#Se crean variables necesarias para todas las interacciones posbiles con el usuario
texto = []
cifrados = []
corrimientos = []
k = 0

##Se crea un boton el cual sera usado en repetidas ocasicones y para eficiencia de codigo se guarda en una variable
buttonfin = InlineKeyboardButton(text='No',callback_data='fin')

#Se Crea un string muy util para el cifrado
abc = '1aábc2deéf3ghií4jklmn5ñoópq6rstu8úüvw7xyzA9ÁBCDEÉ0FGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ.,;:"()[]{}%#$/¿?¡!-_' + "'"

#Se crea la funcion que se correra al momento de que el usuario decida no seguir codificando o decodificando
#Esta Da un mensaje de despedida y finaliza el proceso de conversacion que se tenia con el usuario
def fin (update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Muchas gracias por usar nuestro bot, si desea seguir usandolo utilice alguno de los comandos disponibles'
    )
    return ConversationHandler.END


#Se crea la funcion en la cual se realiza el corrimiento del cifrado de cesar
def corrimientocesar(text, corrimiento):
    cifrad = ''
    for c in text:
        if c in abc:
            cifrad += abc[(abc.index(c) + corrimiento) % (len(abc))]
        elif c == ' ':
            cifrad += c
        else:
            print(f"oops!, error con la letra {c}")
    return cifrad


#Funcion util para elegir de multiples cadenas de texto, cual tiene el 80% de sus palabras correctamente escritas
def selector(lista, pos):
    f = 0
    for i,j in zip(lista,pos):
        f = 0
        palabras = i.split(" ")
        chkr = SpellChecker('es_CO', i)
        for err in chkr:
            f+=1
            if (f > (len(palabras) * 0.2)):
                break
        if (f < (len(palabras) * 0.1)): return i,j
    return ""

#Se define la funcion Start el cual se ejecutara cuando el usuario digite el comando /start
#Esta cumple la función de dar un mensaje de bienvenida y un par de instrucciones
def start(update, context):
    update.message.reply_text(
        'Hola!, un gusto verte! \n\n utiliza:\n /cifrar para codificar un texto\n/descifrar para decodificar un texto\n/historial Para ver su historial de palabras codificadas y decodificadas\n/ayuda para ver los comandos disponibles con sus descripciones')

#Se define la funcion ayuda el cual se ejecutara cuando el usuario digite el comando /ayuda
#Esta cumple la función de dar un mensaje de ayuda, diciendo todos los posibles comandos por ejecutar y detallandolos
def ayuda(update, context):
    update.message.reply_text(
        'Utiliza:\n\n/cifrar: Para codificar un texto mediante el metodo cesar, deberas especificar los espacios a correr\n\n/decifrar: Decodifica un texto cifrado mediante el metodo cesar\n\n/historial: Te mostrara todas las palabras cifradas o descifradas con sus respectivos corrimientos\n\n/ayuda: Despliega este menu')


#esta funcion se ejecuta cuando el usuario ingrese el comando /cifrar y su funcion sera pedir el texto al usuario y luego devolvera un estado 0 el cual estara escuchando
def cifrar(update, context):
    update.message.reply_text('por favor envia el texto a cifrar')
    return 0

#Esta funcion recibira el texto del usuario a cifrar y luego pedira el numero de corrimientos y devolvera el siguiente estado
def input_text(update, context):
    texto.append(update.message.text)
    update.message.reply_text('por favor introduce el numero de posiciones a correr')
    return 1

#Esta funcion recibira el numero de corrimientos y con el texto hara el cifrado cesar
def cifrado(update, context):
    #Si el usuario no ha ingresado un numero si no en su lugar ingresa otro caracter, el programa volvera a pedir el numero nuevamente
    if not update.message.text.isdigit():
        update.message.reply_text('Por favor debe digitar un numero, intentelo de nuevo')
        update.message.reply_text('por favor introduce el numero de posiciones a correr')
        return 1
    #Si el usuario digito un numero correctamente se comensara a hacer el cifrado
    else:
        global k
        #Se envia el texto y el corrimiento a la funcion y luego se mostrara al usuario
        cifrad = corrimientocesar(texto[k], int(update.message.text))
        update.message.reply_text('Su texto cifrado es:')
        update.message.reply_text(cifrad)

        #Si el usuario ya ha cifrado el mismo texto con el mismo corrimiento con anterioridad no se añadira al historial para evitar duplicados
        #En caso contrario se añadira al historial
        if (not cifrad in cifrados):
            cifrados.append(cifrad)
            corrimientos.append(int(update.message.text))
            k += 1
        else:
            texto.remove(texto[k])

        #Se crea dos botones el cual le indique al usuario si desea continuar o no
        update.message.reply_text(
            text='Desea continuar cifrando mas textos?',
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Si', callback_data='siuu'),buttonfin]
            ])
        )
        return ConversationHandler.END

#Funcion creada necesariamente para interpretar la entrada del boton y continuar con la interaccion con el usuario
def cifradobutton(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='por favor envia el texto a cifrar'
    )
    return 0

#Funcion creada para cuando el usuario digite el comando /descifrar
#Esta pedira el texto y enviara el siguiente estado el cual esperara que el usuario envie el texto
def decifrar(update, context):
    update.message.reply_text('por favor envia el texto a descifrar')
    return 2

#Funcion creada necesariamente para interpretar la entrada del boton y continuar con la interaccion con el usuario
def descifrarbutton(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Por favor envia el texto a descifrar'
    )
    return 2


#Una vez que el usuario ingrese el texto a descifrar, comenzara el proceso de descifrar
def descifrado(update, context):
    global k
    pasa = True
    #Diccionario creado para interpretar numeros puestas con la intension de reemplazar letras
    numtoletras = {'1' : 'i','2' : '2', '3' : 'e', '4' : 'a', '5' : 's', '6' : 'g', '7' : 't','8' : '8', '9' : '9', '0' : 'o'}

    #Se hace un conteo de las letras y si el numero de letras excede el numero 30 se tomara como un numero grande de letras, esto quiere decir que se trata de un texto razonablemente largo
    #De esta forma se podra utilizar el metodo de descifrado del cesar que tradicionalmente se utiliza
    #De lo contrario se utilizara el diccionario del español colombia para verificar el texto
    if (len(update.message.text) <= 30):
        #Se crean listas auxiliares necesarias
        elegidas = []
        pos = []

        #Se crea un ciclo que comience a verificar cada corrimiento del metodo cesar
        for i in range(0, len(abc) + 1, 1):
            pasa = True

            #Se cifra la palabra en el numero de posiciones indicado por el ciclo
            cifrad = corrimientocesar(update.message.text, i)

            #Se toman las palabras del descifrado resultado para comprobar si el resultado es coherente o no
            palabras = cifrad.split(" ")
            for w in palabras:
                #Si la palabra contiene simbolos, se eliminaran los simbolos que impidan la verificacion de la palabra
                palabralimpia = ''
                if not w.isalnum():
                    for c in w:
                        if c.isalnum():
                            palabralimpia += c
                    w = palabralimpia
                    palabralimpia = ''

                #Si la palabra no es un numero en su totalidad se comenzará la verificacion de que la palabra exista
                if not w.isdigit():

                    #Si la palabra contiene algun numero de por medio este numero se cambiara por la letra que mas posiblemente pueda identificarse
                    if any(chr.isdigit() for chr in w):
                        palabralimpia = ''
                        for c in w:
                            if c.isdigit():
                                palabralimpia += numtoletras.get(c)
                            else:
                                palabralimpia += c
                        w = palabralimpia
                        palabralimpia = ''

                    #Si la palabra resultante no es vacia, se comenzara a verificar si la palabra existe en el diccionario
                    #De lo contrario, quiere decir que la palabra era solo simbolos y por tanto no existira en el diccionario
                    if not w == "":
                        if not d.check(w.lower()):
                            pasa = False
                            break
                    else:
                        pasa = False
                        break

            #Si todas las palabras existen, se enviaran a la lista de textos elegidos para verificar por segunda vez
            if pasa:
                elegidas.append(cifrad)
                pos.append(i)

        #Se crean variables auxiliarias necesarias
        elegir = len(update.message.text)
        elegirw = ''

        #Se realizar una busqueda secuencial entre los textos descifrados elegidos
        #El objetivo de esta revision es escoger el texto que menos caracteres especiales contenga, ya que generalmente estos suelen ser los textos objetivo
        for y,s in zip(elegidas,pos):
            cont = 0
            corri = 0
            for h in range(0,len(y), 1):
                if not y[h].isalnum(): cont += 1
            if elegir > cont:
                elegir = cont
                elegirw = y
        if elegirw == "":
            pasa = False
        else:
            pasa = True
            cifrad = elegirw
            corri = s

    #Si tiene mas de 30 palabras se utiliza el descifrado comun del cesar
    else:
        #Se crean variables auxiliares necesarias
        cadenas = []
        pos = []

        #Se hace un ciclo para pobrar todos los descifrados
        for i in range(0,len(abc) + 1, 1):

            #Se descifra la palabra segun la iteracion del ciclo
            cifrad = corrimientocesar(update.message.text, i)

            #Se toma la frecuencia de todas las letras y luego se toman las cadenas que se repitan mas la 'a' y la 'e'
            #Estas cadenas seran agregadas a una lista para luego agregar la que tenga mayor coherencia
            frecuencias = Counter(cifrad.lower())
            frecuencias.pop(" ")
            max_key = max(frecuencias.items(), key=operator.itemgetter(1))[0]
            if (max_key == 'a') | (max_key == 'e'):
                cadenas.append(cifrad)
                pos.append(i)

        #Se verifica que el programa halla elegido una palabra que contenga al menos el 80% de sus palabras correctas
        if selector(cadenas,pos) == "":
            pasa = False
        else:
            cifrad,corri = selector(cadenas,pos)
            pasa = True

    #Si se ha encontrado un posible texto de descifrado o no, se le notificara al usuario
    if pasa:
        update.message.reply_text(f'Su texto descifrado es:')
        update.message.reply_text(cifrad)

        #Si se ha hallado el texto y este no esta dentro del historial, se agregara
        if (not cifrad in texto) & (not update.message.text in cifrados):
            texto.append(cifrad)
            cifrados.append(update.message.text)
            corrimientos.append(corri)
            k += 1
    else:
        update.message.reply_text(
            'Su texto no ha podido ser decifrado, por favor verifique que el texto decifrado final sea coherente: ')

    #Se mostrara al usuario dos botones, indicando si desea continuar o no
    update.message.reply_text(
        text='Desea continuar descifrando mas textos?',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Si', callback_data='descifrar'), buttonfin]
        ])
    )
    return ConversationHandler.END


#Se crea la funcion para ser ejecutada cuando el usuario digite /historial
#Su funcion es mostrar todos los textos cifrados o descifrados que se han hecho durante la interaccion con el usuario
def history(update, context):
    global k
    if k == 0:
        update.message.reply_text('Usted no ha codificado o decodificado ninguna palabra, le invitamos a utilizar nuestro bot!')
    else:
        update.message.reply_text('El historial de sus palabras cifradas y decifradas es el siguiente: ')
        for a, b, c in zip(texto, cifrados, corrimientos):
            update.message.reply_text('Texto decifrado: ')
            update.message.reply_text(a)
            update.message.reply_text(f'Texto cifrado con {c} corrimientos: ')
            update.message.reply_text(b)


if __name__ == '__main__':
    #Se crea la comunicación con el bot por medio del token otorgado por telegram y guardamos las actualizaciones en la variable llamada update
    updater = Updater(token='5306241530:AAHYb_-svAp6VKlgZXlfG8rk8dcgK1muojw', use_context=True)

    dp = updater.dispatcher

    #Creamos una variable util para el historial incorporado en el bot
    k = 0

    #Se crean los comandos que daran salida a una respuesta rapida por parte del bot
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ayuda', ayuda))
    dp.add_handler(CommandHandler('Historial', history))

    #Se crean los comandos por los cuales sera necesario mantener una conversación con el usuario
    dp.add_handler(ConversationHandler(
        #Se crean los puntos de entrada, o en otras palabras los comandos por lo cuales se entrara a la conversacion
        entry_points=[
            CommandHandler('cifrar', cifrar),
            CommandHandler('descifrar', decifrar),
            CallbackQueryHandler(pattern='siuu', callback=cifradobutton),
            CallbackQueryHandler(pattern='descifrar', callback=descifrarbutton),
            CallbackQueryHandler(pattern='fin', callback=fin)
        ],

        #Se crean los estados, utiles para que el bot sepa que hacer en cada parte de la conversación
        states={
            0: [MessageHandler(Filters.text, input_text)],
            1: [MessageHandler(Filters.text, cifrado)],
            2: [MessageHandler(Filters.text, descifrado)]
        },

        #Se crea una lista fallbacks el cual recibira todas las posibles excepciones no tomadas en cuenta por el programador
        fallbacks=[]
    ))

    #Se crea la escucha y el ciclo infinito del bot
    updater.start_polling()
    updater.idle()
