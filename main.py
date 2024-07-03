import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import pygame

# Классы игроков с различными ролями
class Player:
    def __init__(self, name, gender, age, cunning, eloquence, role_image=None):
        self.name = name
        self.gender = gender
        self.age = age
        self.cunning = cunning
        self.eloquence = eloquence
        self.role_image = role_image
        self.alive = True
        self.role = "Мирный житель"
        self.display_role = "Мирный житель"


class Mafia(Player):
    def __init__(self, *args):
        super().__init__(*args)
        self.role = "Мафия"


class Doctor(Player):
    def __init__(self, *args):
        super().__init__(*args)
        self.role = "Доктор"
        self.display_role = "Мирный житель"


class Police(Player):
    def __init__(self, *args):
        super().__init__(*args)
        self.role = "Комиссар"
        self.display_role = "Мирный житель"


class Maniac(Player):
    def __init__(self, *args):
        super().__init__(*args)
        self.role = "Маньяк"


class Citizen(Player):
    def __init__(self, *args):
        super().__init__(*args)
        self.role = "Мирный житель"

# Генерация случайных никнеймов
def generate_nicknames():
    return [
        "Боб", "Петрик", "Роман", "Мафиозник", "Джонни", "ВасяПу", "Макс",
        "Джек Потрошитель", "Никита", "Кирюха_22", "Иван2004", "СтивДжопс"
    ]

# Назначение ролей игрокам
def assign_roles(players):
    roles = ['Мафия', 'Мафия', 'Доктор', 'Комиссар', 'Маньяк'] + ['Мирный житель'] * (len(players) - 5)
    random.shuffle(roles)

    nicknames = generate_nicknames()
    random.shuffle(nicknames)

    for i, player in enumerate(players):
        nickname = nicknames[i]
        if roles[i] == 'Мафия':
            players[i] = Mafia(nickname, random.choice(["Male", "Female"]), random.randint(18, 60),
                               random.randint(50, 100), random.randint(50, 100))
        elif roles[i] == 'Доктор':
            players[i] = Doctor(nickname, random.choice(["Male", "Female"]), random.randint(18, 60),
                                random.randint(50, 100), random.randint(50, 100))
        elif roles[i] == 'Комиссар':
            players[i] = Police(nickname, random.choice(["Male", "Female"]), random.randint(18, 60),
                                random.randint(50, 100), random.randint(50, 100))
        elif roles[i] == 'Маньяк':
            players[i] = Maniac(nickname, random.choice(["Male", "Female"]), random.randint(18, 60),
                                random.randint(50, 100), random.randint(50, 100))
        else:
            players[i] = Citizen(nickname, random.choice(["Male", "Female"]), random.randint(18, 60),
                                 random.randint(50, 100), random.randint(50, 100))

# Смена фазы дня и ночи
def change_phase():
    global current_phase, players, reports, police_checked_mafia
    if current_phase == "night":
        current_phase = "day"
        day_events = day_phase()
        reports = day_events
        messagebox.showinfo("Фаза сменена", "День начался!\n" + day_events)
    else:
        current_phase = "night"
        night_events = night_phase()
        reports = night_events
        messagebox.showinfo("Фаза сменена", "Ночь началась!\n" + night_events)
    update_ui()
    check_game_end()

# Логика ночной фазы
def night_phase():
    global players, police_checked_mafia
    events = []

    alive_mafias = [player for player in players if isinstance(player, Mafia) and player.alive]
    alive_maniacs = [player for player in players if isinstance(player, Maniac) and player.alive]

    if not alive_mafias and not alive_maniacs:
        return "Сегодня город может спать мирно."

    mafia_targets = [player for player in players if player.alive and not isinstance(player, Mafia)]
    maniac_targets = [player for player in players if player.alive and not isinstance(player, Maniac)]

    if mafia_targets and alive_mafias:
        mafia_victim = random.choice(mafia_targets)
    else:
        mafia_victim = None

    if maniac_targets and alive_maniacs:
        maniac_victim = random.choice(maniac_targets)
    else:
        maniac_victim = None

    doctor = next((player for player in players if isinstance(player, Doctor) and player.alive), None)
    if doctor:
        save = random.choice([player for player in players if player.alive])

        if mafia_victim and save == mafia_victim:
            events.append(f"{mafia_victim.name} был спасен доктором от мафии.")
            mafia_victim = None
        if maniac_victim and save == maniac_victim:
            events.append(f"{maniac_victim.name} был спасен доктором от маньяка.")
            maniac_victim = None

    if mafia_victim:
        mafia_victim.alive = False
        mafia_victim.display_role = mafia_victim.role
        events.append(f"{mafia_victim.name} был убит мафией.")

    if maniac_victim:
        maniac_victim.alive = False
        maniac_victim.display_role = maniac_victim.role
        events.append(f"{maniac_victim.name} был убит маньяком.")

    police = next((player for player in players if isinstance(player, Police) and player.alive), None)
    if police:
        checkable_players = [player for player in players if player.alive and player != police]
        if checkable_players:
            check = random.choice(checkable_players)
            if isinstance(check, Mafia):
                events.append(f"Комиссар проверил {check.name}, который оказался мафией.")
                check.display_role = "Мафия"
                police_checked_mafia = check

    return "\n".join(events)

# Логика дневной фазы
def day_phase():
    global players, police_checked_mafia
    alive_players = [player for player in players if player.alive]
    if len(alive_players) == 1:
        return f"{alive_players[0].name} остался последним и выигрывает игру!"

    votes = {player: 0 for player in alive_players}
    if police_checked_mafia:
        victim = police_checked_mafia
        votes[victim] = len(alive_players)
        police_checked_mafia = None
    else:
        for player in alive_players:
            vote = random.choice([p for p in alive_players if p != player])
            votes[vote] += 1

    victim = max(votes, key=votes.get)
    victim.alive = False
    if victim.role != "Мирный житель":
        victim.display_role = victim.role
    players_frames[players.index(victim)].config(bg="red")

    return f"{victim.name} был изгнан игроками."

# Обновление интерфейса
def update_ui():
    global players_frames, players
    for i, frame in enumerate(players_frames):
        player = players[i]
        img_label = frame.winfo_children()[0]
        text_label = frame.winfo_children()[1]
        if player.alive:
            frame.config(bg="white")
            img_label.config(image=role_images[player.display_role])
            text_label.config(
                text=f"{player.name}\n{player.display_role if current_phase == 'night' else 'Мирный житель'}")
        else:
            frame.config(bg="red")
            img_label.config(image=role_images[player.display_role])
            text_label.config(text=f"{player.name}\n{player.display_role}")

    update_role_count()

# Обновление количества ролей
def update_role_count():
    global players, role_count_label
    role_count = {"Мафия": 0, "Мирный житель": 0, "Доктор": 0, "Комиссар": 0, "Маньяк": 0}
    for player in players:
        if player.alive:
            role_count[player.role] += 1

    role_count_text = "Текущие роли в игре:\n"
    for role, count in role_count.items():
        if count > 0:
            role_count_text += f"{role}: {count}\n"

    role_count_label.config(text=role_count_text)

# Проверка окончания игры
def check_game_end():
    global players
    alive_players = [player for player in players if player.alive]
    roles = set(player.role for player in alive_players)

    if roles <= {"Мирный житель", "Доктор", "Комиссар"}:
        messagebox.showinfo("Игра окончена", "Победа за мирными жителями!")
        root.destroy()
        return

    if len(roles) == 1:
        role = roles.pop()
        messagebox.showinfo("Игра окончена", f"Победа за ролью: {role}")
        root.destroy()

# Воспроизведение музыки
def play_music():
    try:
        pygame.mixer.init()
        pygame.mixer_music.load('mafia.mp3')
        pygame.mixer_music.set_volume(0.2)
        pygame.mixer_music.play(-1)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось воспроизвести музыку: {e}")

# Инициализация интерфейса
def init_gui():
    global players, players_frames, role_images, root, role_count_label
    root = tk.Tk()
    root.title("Игра Мафия")

    role_images = {
        "Мафия": ImageTk.PhotoImage(Image.open("mafia.png")),
        "Доктор": ImageTk.PhotoImage(Image.open("doctor.png")),
        "Комиссар": ImageTk.PhotoImage(Image.open("police.png")),
        "Маньяк": ImageTk.PhotoImage(Image.open("maniac.png")),
        "Мирный житель": ImageTk.PhotoImage(Image.open("citizen.png")),
    }

    num_players = random.randint(6, 12)
    players = [Player(f"Player {i + 1}", "Male", 30, 50, 50) for i in range(num_players)]
    assign_roles(players)

    num_cols = (num_players + 1) // 2

    players_frames = []

    for i, player in enumerate(players):
        frame = tk.Frame(root, width=150, height=150, relief=tk.RIDGE, borderwidth=2)
        frame.grid(row=i // num_cols, column=i % num_cols, padx=10, pady=10)

        img_label = tk.Label(frame, image=role_images["Мирный житель"])
        img_label.grid(row=0, column=0)

        text_label = tk.Label(frame, text=f"{player.name}\n{player.display_role}", padx=5, pady=5,
                              font=("Helvetica", 12, "bold"))
        text_label.grid(row=1, column=0)

        players_frames.append(frame)

    change_phase_button = tk.Button(root, text="Сменить фазу", command=change_phase, bg="lightblue",
                                    font=("Helvetica", 14, "bold"), padx=10, pady=10)
    change_phase_button.grid(row=num_cols, column=0, columnspan=num_cols, pady=20)

    role_count_label = tk.Label(root, text="", font=("Helvetica", 12, "bold"))
    role_count_label.grid(row=num_cols + 1, column=0, columnspan=num_cols, pady=10)

    update_role_count()

    root.mainloop()

play_music()
current_phase = "night"
players = []
players_frames = []
role_images = {}
reports = ""
police_checked_mafia = None

init_gui()
