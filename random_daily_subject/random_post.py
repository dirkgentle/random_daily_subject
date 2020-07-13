import random


def choose_random_title(database, log_limit=6):
    log = database.get_latest_submissions(log_limit)
    all_titles = database.get_all_titles()

    options = [title for title in all_titles if title.title not in log]

    choosing_bag = []
    count_avg = sum([option.count for option in options]) / len(options)
    for option in options:
        # favour those options that haven't come out so much
        multiplier = (
            1 + int(2 * (count_avg - option.count)) if option.count < count_avg else 1
        )
        for _ in range(multiplier):
            choosing_bag.append(option.id)

    return random.choice(choosing_bag)


def choose_random_body(database, title_id):
    options = [option for option in database.get_all_bodies(title_id)]

    count_avg = sum([option.count for option in options]) / len(options)
    choosing_bag = [option.id for option in options if option.count <= count_avg]

    return random.choice(choosing_bag)
