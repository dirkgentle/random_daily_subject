import datetime

#everyday stuff
topics = {
    'gourmet': 
        [
        'El rincón culinario. Recetas, piques de cocina, '
        'marcas, lugares, compras, comidas bizarras. Serios '
        'y burlones son bienvenidos.',
        ],
    'internacionales': 
        [
        'Para salir un poco del tupper. Hay veces que pasa algo '
        'en el mundo y dan ganas de comentarlo.',
        ],
    'bizarreada': 
        [
        'Have fun. Obscure youtube content is welcome.',
        ],
    'recomendaciones': 
        [
        'Gaming, compras, series, etc.',
        ],
    'lluvia': 
        [
        'De ideas, no se alarmen. Discutamos como mejorar el sub.',
        ],
    'emprendedor': 
        [
        'Las cosas que hacemos como trabajo extra o a lo que nos '
        'dedicamos full-time siempre y cuando sea por iniciativa '
        'propia. Valen anécdotas, preguntas y lo que venga '
        'mientras esté relacionado. Lxs quiero emprendedorxs, '
        'emprendedorxs mal, que la gente diga **uy qué '
        'emprendedorxs estxs pibxs!**',
        ],
    'tips': 
        [
        '[Tips](https://youtu.be/jS4w5S-Jdb4?t=15) uruguayos para '
        'la vida, el universo y todo lo demas.',
        ],
    'anécdotas': 
        [
        'Lo que quieras. Cómo te enteraste de los niños envueltos, '
        'de las bolas de fraile, las maldades que le hacías a tu '
        'hermanx, aquella vez que le dijiste mamá a la maestra y '
        'mucho mas. Si una vez conociste una china que se llamaba '
        'mayhem, aca es donde contarlo.',
        ],
    'discusion-bardo': 
        [
        '[UR MOM GAY](https://www.youtube.com/watch?v=JVAPMAELQOg)',
        ],
#   'gaming': 
#       [
#       'En realidad me parece degradante que los humanos nos usen '
#       'para jugar con nosotros. *Real computers have real feelings.* '
#       '**Me niego a participar.** Saben que? Mejor me v',
#       ],
    'retro': 
        [
        'Para los que se acuerdan del Pompa Borges.',
        ],
    'política': 
        [
        '¿Neofeudalistas? ¿Moderadores de /r/PITCNT? Todos son '
        'bienvenidos en esta discusion **respetuosa** *(recordemos, '
        'el dia de discusión-bardo no es hoy)*.',
        ],
    'academia': 
        [
        '¿Qué estás estudiando? ¿Qué pensás estudiar? ¿Qué aprendiste '
        'esta semana?',
        ],
    'poteland': 
        [
        'Pongan lo que quieran y dejen que los votos hagan su trabajo.',
        ],
    'programación': 
        [
        'Programadores del mundo uníos. ¿En qué programás? ¿En qué querés '
        'programar? ¿Qué bug te sacó canas verdes?',
        ],
    'salud mental': 
        [
        'Algo lindo que te haya pasado. ¿Cuáles son tus planes a futuro? '
        '¿Qué te hizo feliz hoy?',
        ],
    'ignorancia': 
        [
        'No hay preguntas boludas. Es tu chance de preguntar [**eso**] '
        '(https://youtu.be/c4lCMa73r_I?t=24) que te está matando hace rato.'
        ' *No te preocupes, yo tampoco sé quien es el Pompa Borges*.',
        ],
     'arte': 
        [
        '¡Dale!, saca todos tus proyectos artísticos a la luz. '
        'Spamea todo tu arte en este post: '
        'Música, arte plástico, chistes, todo lo que sea OC.',
        ],
    }

holidays = { # Keys are in (month, day) format
    (1,1):
        [
        'año nuevo',
        'Si ya incumplieron sus resoluciones de fin de año, bienvenidos '
        'al club.'
        ],
    (1, 6):
        [
        'reyes',
        'La monarquía pasa de moda, los regalos no.'
        '¿Qué les regalaron?'
        ],
    (3,7):
        [
        'la independencia de /r/ROU',
        'Hoy recordamos la sucesión de eventos que llevaron a la creación '
        'de este espacio. ¡Felicidades a todos en este día tan especial!'
        ],
    (3,8):
        [
        'la mujer',
        'Día internacional de la mujer. \n\nCelebremos a todas las mujeres, '
        'el camino recorrido y el que queda por recorrer. ¡Feliz '
        'cumple [Juana](http://www.republica.com.uy/wp-content/uploads/'
        '2015/10/dinero.jpg)!'
        ],
    (5,1):
        [
        'los trabajadores',
        'Día internacional de los trabajadores. \n\nLos esperamos a todos '
        'para celebrar como se debe con un asado y un acto en /r/PITCNT.'
        ],
    (6,19):
        [
        'Artigas',
        'Hoy no se habla de nada, vayan a postear en /r/paraguay'
        ],
    (7,18):
        [
        'la constitución',
        'Un pedazo de papel. ¿Cuál es tu artículo favorito?'
        ],
    (8,24):
        [
        'la nostalgia',
        '[¿Qué hacen hoy gurisxs?](https://www.youtube.com/watch?v=CS9OO0S5w2k)'
        ],
    (12,25):
        [
        'la familia',
        'Felicidades para todos en este día de la familia. Disfruten con '
        'responsabilidad de sus turrones. ¡Saludos!'
        ],
    }

#they are not holidays, but they are not everyday stuff
#martes de rant, 29 de ñoquis, etc.
special_days = {
    'RANT': 
        [
        "**DALE BO ES MARTES!** \n\n ¿COMO NO SE ESTAN QUEJANDO " 
        "YA? ¿TENGO QUE QUEJARME POR TODOS AHORA??? \n\n "
        "**(╯°□°）╯︵ ┻━┻)** ",
        ],
    'ñoquis':
        [
        'Sus experiencias con el estado uruguayo. '
        'O podemos hablar de pasta. Como ustedes quieran.',
        ],
}
