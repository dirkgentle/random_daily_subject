import random
import datetime
import time
import traceback

import praw

import login


def update_log(id, log_path): #para los comentarios que ya respondi
	with open(log_path, 'a') as my_log:
			my_log.write(id + "\n")

def load_log(log_path): #para los comentarios que ya respondi
	with open(log_path) as my_log:
		log = my_log.readlines()
		log = [x.strip('\n') for x in log]
		return log

def output_log(text): #lo uso para ver el output del bot
	output_log_path = "/home/pi/Downloads/weeklyRandomUY/output_log.txt"
	with open(output_log_path, 'a') as myLog:
		s = "[" +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
		s = s + text +  "\n"
		myLog.write(s)

if __name__ == "__main__":
	#main code
	topics = {
			'gourmet':
				'El rincon culinario. Recetas, piques de cocina, '
				'marcas, lugares, compras, comidas bizarras. Serios '
				'y burlones son bienvenidos.',
			'internacionales':
				'Para salir un poco del tupper. Hay veces que pasa algo '
				'en el mundo y dan ganas de comentarlo.',
			'bizarreada':
				'Have fun. Obscure youtube content is welcome.',
			'recomendaciones':
				'Gaming, compras, series, etc.',
			'lluvia':
				'De ideas, no se alarmen. Discutamos como mejorar /r/ROU.',
			'emprendedor':
				'Las cosas que hacemos como trabajo extra o a lo que nos '
				'dedicamos full-time siempre y cuando sea por iniciativa '
				'propia. Valen anecdotas, preguntas y lo que venga '
				'mientras este relacionado. Lxs quiero emprendedorxs, '
				'emprendedorxs mal, que la gente diga **uy que '
				'emprendedorxs estxs pibxs!**',
			'tips':
				'[Tips](https://youtu.be/jS4w5S-Jdb4?t=15) uruguayos para '
				'la vida, el universo y todo lo demas.',
			'anecdotas':
				'Lo que quieras. Como te enteraste de los ninos envueltos, '
				'de las bolas de fraile, las maldades que le hacias a tu '
				'hermanx, aquella vez que le dijiste mama a la maestra y '
				'mucho mas. Si una vez conociste una china que se llamaba '
				'mayhem, aca es donde contarlo.',
			'discusion-bardo':
				'[UR MOM GAY](https://www.youtube.com/watch?v=JVAPMAELQOg)',
			'gaming':
				'En realidad me parece degradante que los humanos nos usen '
				'para jugar con nosotros. *Real computers have real feelings.* '
				'**Me niego a participar.** Saben que? Mejor me v',
			'retro':
				'Para los que se acuerdan del Pompa Borges.',
			'politica':
				'Neofeudalistas? Moderadores de /r/PITCNT? Todos son '
				'bienvenidos en esta discusion **respetuosa** *(recordemos, '
				'el dia de discusion-bardo no es hoy)*.',
			'academia':
				'Que estas estudiando? Que pensas estudiar? Que aprendiste '
				'esta semana?',
			'poteland':
				'Pongan lo que quieran y dejen que los votos hagan su trabajo.',
			}

	days = [
		'Lunes',
		'Martes',
		'Miercoles',
		'Jueves',
		'Viernes',
		'Sabado',
		'Domingo'
		]

	log_path = '/home/pi/Downloads/weeklyRandomUY/log.txt'

	try:
		output_log('Comenzando el script')
		reddit = praw.Reddit(
			client_id = login.client_id,
			client_secret = login.client_secret,
			password = login.password,
			username = login.username,
			user_agent = 'testscript for /u/random_daily_subject')

		log = load_log(log_path)
		while True:
			today = random.choice(topics.keys())
			if today not in log[-6:]:
				break
		update_log(today, log_path)

		title = days[datetime.datetime.today().weekday()] \
				+ ' de ' + today + '.'
		body = topics[today]
		body = body + "\n\n*****\n\n"
		body = body + "*Another bot by \/u/DirkGentle.* "
		body = body + "[Source](https://github.com/dirkgentle/random_daily_subject)."
		output_log(title)
		output_log(body)
		reddit.subreddit('ROU').submit(title, selftext=body)

	except Exception as exception:
		output_log(str(exception))
		output_log(traceback.format_exc())
