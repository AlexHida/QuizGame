import tkinter as tk
from tkinter import *
import os
import json
from PIL import Image, ImageSequence, ImageTk, ImageOps

# Función para cargar preguntas desde el archivo JSON
def load_questions():
    if not os.path.exists("preguntas.json"):
        return None  # Retorna None si no hay archivo

    with open("preguntas.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Cargar preguntas desde el archivo externo
questions_data = load_questions()

# Obtener niveles dinámicamente según el JSON
all_levels = []
if questions_data:
    for key in sorted(questions_data.keys()):  # Ordenar niveles por nombre (level_1, level_2, ...)
        all_levels.append(questions_data[key])

# Variables globales
current_question = 0
score = 0
level = 0
error_window = None  
questions = all_levels[level] if all_levels else []

answered_questions = []

# Variable global para la ventana de puntuaciones
scores_window = None 

# Colores y estilos
BACKGROUND_COLOR = "#1E1E2E"  # Azul oscuro
BUTTON_COLOR = "firebrick2"  # Naranja vibrante
BUTTON_HOVER = "gray90"  # Amarillo cuando el cursor está encima
TEXT_COLOR = "#FFFFFF"  # Blanco
QUESTION_BOX_COLOR = "#252547"  # Color de fondo del cuadro de pregunta

# Función para iniciar el juego
def start_game():
    global current_question, score, level, questions, answered_questions

    answered_questions = []   # Limpia la lista de respuestas anteriores
    # Borra el archivo respuestas_usuario.json
    if os.path.exists("respuestas_usuario.json"):
        os.remove("respuestas_usuario.json")

    if not all_levels:
        show_no_questions_message()
        return

    current_question = 0
    score = 0  
    level = 0
    questions = all_levels[level]

    update_score_label()
    main_frame.pack_forget()
    question_frame.pack(fill="both", expand=True)

    load_question()

# Función para verificar respuesta
def check_answer(selected_option):
    global current_question, score, level, questions, answered_questions

    question_data = questions[current_question]
    correcta = question_data["answer"]
    acertó = selected_option == correcta

    # Guardar en la lista
    answered_questions.append({
        "pregunta": question_data["question"],
        "opciones": question_data["options"],
        "respuesta_correcta": correcta,
        "respuesta_usuario": selected_option,
        "acertó": acertó
    })

    if acertó:
        score += 1

    current_question += 1

    if current_question < len(questions):
        load_question()
    else:
        # Guardar el JSON de respuestas antes de mostrar resultados
        save_answers_to_file()
        if score == sum(len(lvl) for lvl in all_levels[:level + 1]):
            if level < len(all_levels) - 1:
                level += 1
                show_level_up_message()
            else:
                show_results("¡Felicidades! Completaste todos los niveles")
        else:
            show_results("Puntos insuficientes para avanzar")

def save_answers_to_file():
    with open("respuestas_usuario.json", "w", encoding="utf-8") as f:
        json.dump(answered_questions, f, indent=4, ensure_ascii=False)

# Función para mostrar mensaje de "Has avanzado el Nivel" por 2 segundos
def show_level_up_message():
    question_frame.pack_forget()
    level_up_label.config(text=f"¡Has avanzado al Nivel {level + 1}!")
    level_up_frame.pack(fill="both", expand=True)
    root.after(2000, continue_to_next_level)

# Función para cargar el Nivel 2 después del mensaje
def continue_to_next_level():
    global current_question, questions

    level_up_frame.pack_forget()
    question_frame.pack(fill="both", expand=True)

    current_question = 0
    questions = all_levels[level]
    load_question()

# Función para cargar una nueva pregunta
def load_question():
    question_data = questions[current_question]
    question_label.config(text=question_data["question"])
    
    for i, option in enumerate(question_data["options"]):
        buttons[i].config(text=option, command=lambda opt=option: check_answer(opt))
    
    update_score_label()

# Función para mostrar los resultados con el puntaje
def show_results(message):
    global score

    results_label.config(text=f"{message}\n\nPuntaje obtenido: {score}")
    name_entry.delete(0, tk.END)  
    
    question_frame.pack_forget()
    results_frame.pack(fill="both", expand=True)

# Función para guardar el puntaje en un archivo
# Número máximo de puntuaciones a almacenar
MAX_SCORES = 7
# Función para guardar el puntaje en un archivo usando una cola FIFO
def save_score():
    global score

    player_name = name_entry.get().strip()

    if len(player_name) > 5:
        player_name = player_name[:5]  # Limitar a 5 caracteres

    if not player_name:  # No guardar si no se introduce un nombre
        return

    scores = []

    # Leer el archivo y cargar las puntuaciones existentes
    if os.path.exists("puntajes.txt"):
        with open("puntajes.txt", "r") as file:
            scores = [line.strip() for line in file.readlines()]

    # Convertir la lista de puntuaciones en una lista de tuplas (nombre, puntaje)
    score_tuples = []
    for s in scores:
        try:
            name, points = s.rsplit(":", 1)
            points = int(points.strip())  # Convertir a número
            score_tuples.append((name.strip(), points))
        except ValueError:
            continue  # Ignorar líneas con formato incorrecto

    # Agregar la nueva puntuación si cumple la condición
    if len(score_tuples) < MAX_SCORES or score > min(points for _, points in score_tuples):
        score_tuples.append((player_name, score))

    # Ordenar la lista de mayor a menor puntaje
    score_tuples.sort(key=lambda x: x[1], reverse=True)

    # Mantener solo los 7 mejores puntajes
    score_tuples = score_tuples[:MAX_SCORES]

    # Guardar la lista actualizada en el archivo
    with open("puntajes.txt", "w") as file:
        for name, points in score_tuples:
            file.write(f"{name}: {points}\n")

    return_to_main()  # Volver a la pantalla principal después de guardar

# Función para volver a la pantalla principal
def return_to_main():
    global score

    score = 0  
    update_score_label()

    # Ocultar todas las pantallas activas
    question_frame.pack_forget()  # Oculta la pantalla de preguntas
    results_frame.pack_forget()   # Oculta la pantalla de resultados
    level_up_frame.pack_forget()  # Oculta la pantalla de nivel avanzado

    # Mostrar solo la pantalla principal
    main_frame.pack(fill="both", expand=True)

# Función para actualizar el puntaje en pantalla
def update_score_label():
    score_label.config(text=f"Puntaje: {score}")

# Función para mostrar el contenido de puntajes.txt
def show_scores():
    global scores_window  

    # Si la ventana ya está abierta, la trae al frente
    if scores_window and scores_window.winfo_exists():  
        scores_window.lift()  
        return  

    # Crear ventana emergente para puntuaciones
    scores_window = tk.Toplevel(root)
    scores_window.title("📜 Puntuaciones")
    scores_window.geometry("400x320")
    scores_window.configure(bg=BACKGROUND_COLOR)

    # Título de la ventana
    title_label = tk.Label(scores_window, text="🏆 Mejores Puntajes 🏆", 
                           font=("Arial", 18, "bold"), fg="white", bg=BACKGROUND_COLOR)
    title_label.pack(pady=10)

    # Marco para las puntuaciones con scrollbar
    scores_frame = tk.Frame(scores_window, bg=QUESTION_BOX_COLOR, padx=10, pady=10)
    scores_frame.pack(pady=5, padx=10, fill="both", expand=True)

    scores_canvas = tk.Canvas(scores_frame, bg=QUESTION_BOX_COLOR, highlightthickness=0)
    scores_scrollbar = tk.Scrollbar(scores_frame, orient="vertical", command=scores_canvas.yview)
    scores_list_frame = tk.Frame(scores_canvas, bg=QUESTION_BOX_COLOR)

    scores_list_frame.bind("<Configure>", lambda e: scores_canvas.configure(scrollregion=scores_canvas.bbox("all")))

    scores_window_frame = scores_canvas.create_window((0, 0), window=scores_list_frame, anchor="nw")

    scores_canvas.configure(yscrollcommand=scores_scrollbar.set)

    scores_canvas.pack(side="left", fill="both", expand=True)
    scores_scrollbar.pack(side="right", fill="y")

    # Leer el archivo de puntuaciones
    try:
        with open("puntajes.txt", "r") as file:
            scores_content = file.readlines()
    except FileNotFoundError:
        scores_content = ["No hay puntuaciones registradas."]

    # Mostrar cada puntuación con formato llamativo
    for idx, score in enumerate(scores_content):
        score_label = tk.Label(scores_list_frame, text=f"🥇 {score.strip()}",
                               font=("Arial", 14), fg="white", bg=QUESTION_BOX_COLOR, anchor="w", justify="left")
        score_label.pack(anchor="w", padx=10, pady=2)

    # Botón para cerrar la ventana
    close_button = tk.Button(scores_window, text="❌ Cerrar", font=("Arial", 12, "bold"), 
                             bg=BUTTON_COLOR, fg="black", activebackground=BUTTON_HOVER, command=scores_window.destroy)
    close_button.pack(pady=10)

# Función para mostrar mensaje de error si no hay preguntas
def show_no_questions_message():
    global error_window
    if error_window and error_window.winfo_exists():
        return
    
    error_window = tk.Toplevel(root)
    error_window.title("Error")
    error_window.geometry("400x200")
    error_window.configure(bg="#1E1E2E")
    
    error_label = tk.Label(error_window, text="⚠️ No se encontraron preguntas ⚠️", font=("Arial", 14, "bold"), fg="#FFD700", bg="#1E1E2E", wraplength=380)
    error_label.pack(pady=20)
    
    error_message = tk.Label(error_window, text="Asegúrate de agregar un archivo preguntas.json para jugar.", font=("Arial", 12), fg="#FFFFFF", bg="#1E1E2E", wraplength=380)
    error_message.pack(pady=10)
    
    close_button = tk.Button(error_window, text="Aceptar", font=("Arial", 12, "bold"), bg="#FF9800", fg="black", activebackground="#FFC107", command=error_window.destroy)
    close_button.pack(pady=20)

# Crear ventana principal
root = tk.Tk()
root.title("Juego de Preguntas")
root.geometry("1050x650")
root.configure(bg=BACKGROUND_COLOR)

def show_answers_summary():
    if not os.path.exists("respuestas_usuario.json"):
        return

    with open("respuestas_usuario.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    answers_window = tk.Toplevel(root)
    answers_window.title("Resumen de Respuestas")
    answers_window.geometry("800x600")
    answers_window.configure(bg="gray10")

    canvas = tk.Canvas(answers_window, bg="gray10", highlightthickness=0)
    scrollbar = tk.Scrollbar(answers_window, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="gray10")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for idx, q in enumerate(data, start=1):
        status = "✅ Correcto" if q["acertó"] else "❌ Incorrecto"
        color = "green" if q["acertó"] else "red"
        tk.Label(scroll_frame, text=f"{idx}. {q['pregunta']}", wraplength=700, font=("Arial", 13, "bold"), fg="yellow", bg="gray10").pack(anchor="w", pady=3)
        tk.Label(scroll_frame, text=f"Respuesta correcta: {q['respuesta_correcta']}", wraplength=700, font=("Arial", 12), fg="lightgreen", bg="gray10").pack(anchor="w")
        tk.Label(scroll_frame, text=f"Tu respuesta: {q['respuesta_usuario']}  → {status}", wraplength=700, font=("Arial", 12), fg=color, bg="gray10").pack(anchor="w", pady=(0, 10))

    close_btn = tk.Button(answers_window, text="Cerrar", font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="black", command=answers_window.destroy)
    close_btn.pack(pady=10)

# --------- Pantalla principal ---------
main_frame = tk.Frame(root, bg="RoyalBlue4")
main_frame.pack(fill="both", expand=True)  # Hace que el frame ocupe toda la ventana

# Frame interno para centrar elementos
content_frame = tk.Frame(main_frame, bg="DeepSkyBlue3", borderwidth=2, relief="solid")
content_frame.place(relx=0.5, rely=0.47, width=750, height=370, anchor="center")  # Centrar elementos

title_label = tk.Label(content_frame, text="🎮 QUIZ GAME 🎮", font=("Fixedsys", 40, "bold"), width=18, height=2, borderwidth=2, relief="groove", fg=TEXT_COLOR, bg="grey1")
title_label.pack(pady=30)  # Espaciado entre elementos

# Cargar el logo PNG y redimensionarlo
logo_image = Image.open("logouteq.png")
logo_image = logo_image.resize((150, 175), Image.Resampling.LANCZOS)  # Puedes ajustar el tamaño a tu gusto
logo_photo = ImageTk.PhotoImage(logo_image)

# Colocar el logo dentro del content_frame, a la izquierda de los botones
logo_label = tk.Label(content_frame, image=logo_photo, bg="DeepSkyBlue3")
logo_label.place(x=50, y=170)

# Cargar el logo PNG FCI y redimensionarlo
logo_image2 = Image.open("fci.png")
logo_image2 = logo_image2.resize((150, 165), Image.Resampling.LANCZOS)  # Puedes ajustar el tamaño a tu gusto
logo_photo2 = ImageTk.PhotoImage(logo_image2)

# Colocar el logo dentro del content_frame, a la izquierda de los botones
logo_label2 = tk.Label(content_frame, image=logo_photo2, bg="DeepSkyBlue3")
logo_label2.place(x=550, y=175) 

# Función para cambir colores título
def change_title_color(i=0):
    colors = ('purple1', 'purple2', 'purple3', 'purple4', 'purple3', 'purple2', 'purple1')  # Colores que irán rotando
    title_label.config(fg=colors[i])  # Cambia el color del texto
    
    # Llama a la función después de 75ms con el siguiente color
    next_index = (i + 1) % len(colors)  # Reinicia al llegar al final de la lista
    title_label.after(75, change_title_color, next_index)  

# Inicia el cambio de colores
change_title_color()

# Función para efectos de hover en botones
def on_hover(event):
    event.widget.config(bg=BUTTON_HOVER)

def on_leave(event):
    event.widget.config(bg=BUTTON_COLOR)

def on_hover2(event):
    event.widget.config(bg="purple1")

def on_leave2(event):
    event.widget.config(bg="SpringGreen3")

def on_leave3(event):
    event.widget.config(bg="gray80")

# Botón para jugar
play_button = tk.Button(content_frame, text="▶ Jugar", font=("Fixedsys", 18, "bold"), width=15, bg=BUTTON_COLOR, fg="gray2", activebackground=BUTTON_HOVER, command=start_game)
play_button.pack(pady=10)
play_button.bind("<Enter>", on_hover)
play_button.bind("<Leave>", on_leave)

# Botón para ver puntuaciones
scores_button = tk.Button(content_frame, text="📜 Puntuaciones", font=("Fixedsys", 18, "bold"), width=15, bg=BUTTON_COLOR, fg="gray2", activebackground=BUTTON_HOVER, command=show_scores)
scores_button.pack(pady=10)
scores_button.bind("<Enter>", on_hover)
scores_button.bind("<Leave>", on_leave)

# --------- Pantalla de preguntas ---------
question_frame = tk.Frame(root, bg="steel blue")

# Botón para salir y regresar al menú principal
exit_button = tk.Button(
    question_frame, 
    text="Salir", 
    font=("Arial", 12, "bold"), 
    bg="DodgerBlue2", 
    fg="white", 
    command=return_to_main  
)
exit_button.place(x=10, y=10)  

score_label = tk.Label(question_frame, text="Puntaje: 0", font=("Arial", 14, "bold"), width=10, height=1, fg=TEXT_COLOR, bg="SpringGreen3")
score_label.pack(pady=5)

# Cuadro de pregunta
QUESTION_BOX_COLORS = ('SteelBlue1', 'SteelBlue1', '#5fb2f6', '#5fb2f6', 'SteelBlue2', 'SteelBlue2', '#5fb2f6', '#5fb2f6', 'SteelBlue1', 'SteelBlue1')  # Colores en rotación

question_box = tk.Frame(question_frame, bg=QUESTION_BOX_COLORS[0], padx=20, pady=20)
question_box.pack(pady=10, padx=20, fill="x")

question_label = tk.Label(question_box, text="", wraplength=900, font=("Arial", 15, "bold"), fg=TEXT_COLOR, bg=QUESTION_BOX_COLORS[0])
question_label.pack()

# Función para cambiar de color el cuadro de preguntas
def change_question_box_color(i=0):
    question_box.config(bg=QUESTION_BOX_COLORS[i])
    question_label.config(bg=QUESTION_BOX_COLORS[i])
    next_index = (i + 1) % len(QUESTION_BOX_COLORS)  # Rotación de colores
    root.after(70, change_question_box_color, next_index)

# Inicia el cambio de colores en el cuadro de preguntas
change_question_box_color()

# Botones de respuesta con efectos visuales
buttons = []
for _ in range(4):
    btn = tk.Button(question_frame, text="", width=70, font=("Arial", 15, "bold"), bg="SpringGreen3", fg="black", relief="raised")
    btn.pack(pady=5)
    btn.bind("<Enter>", on_hover2)
    btn.bind("<Leave>", on_leave2)
    buttons.append(btn)

# --------- Agregar el GIF ---------
gif_file = "animation7.gif"
gif_info = Image.open(gif_file)
frames = gif_info.n_frames  # Número de fotogramas

# Establece el nuevo tamaño del GIF
NEW_WIDTH = 200  # Ancho del GIF
NEW_HEIGHT = 200  # Alto del GIF

# Remover fondo blanco GIF
def remove_white_background(img):
    """Convierte el fondo blanco en transparente."""
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Detectar color blanco (o casi blanco) y hacerlo transparente
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))  # Hacer transparente
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

photoimage_objects = []
photoimage_objects_flipped = []

for frame in ImageSequence.Iterator(gif_info):
    frame = remove_white_background(frame)  # Eliminar fondo blanco
    resized_frame = frame.resize((NEW_WIDTH, NEW_HEIGHT), Image.Resampling.LANCZOS)
    flipped_frame = resized_frame.transpose(Image.FLIP_LEFT_RIGHT)  # Espejar imagen

    photoimage_objects.append(ImageTk.PhotoImage(resized_frame))  # Normal
    photoimage_objects_flipped.append(ImageTk.PhotoImage(flipped_frame))  # Espejado

photoimage_objects = []
photoimage_objects_flipped = []  # Versión espejada del GIF

for frame in ImageSequence.Iterator(gif_info):
    resized_frame = frame.resize((NEW_WIDTH, NEW_HEIGHT), Image.Resampling.LANCZOS)
    flipped_frame = resized_frame.transpose(Image.FLIP_LEFT_RIGHT)  # Espejar imagen

    photoimage_objects.append(ImageTk.PhotoImage(resized_frame))  # Normal
    photoimage_objects_flipped.append(ImageTk.PhotoImage(flipped_frame))  # Espejado

# Posición inicial y velocidad del movimiento
x_position = 0  # Posición inicial
direction = 1   # 1 para moverse a la derecha, -1 para moverse a la izquierda
speed = 5       # Velocidad del desplazamiento (pixeles por ciclo)
max_width = 800  # Punto B (ancho máximo de desplazamiento)
current_frame = 0  # Control del frame de animación

gif_label = tk.Label(question_frame, image="", bg="steel blue") 
gif_label.pack(side="bottom", pady=30)  # Se coloca bien abajo con espacio extra

def animate_gif():
    """Función para animar el GIF sin interrupciones."""
    global current_frame, loop

    # Selecciona la imagen en función de la dirección
    if direction == 1:
        gif_label.configure(image=photoimage_objects[current_frame])
    else:
        gif_label.configure(image=photoimage_objects_flipped[current_frame])

    current_frame = (current_frame + 1) % frames
    loop = root.after(150, animate_gif)  # Llama a la función cada 50ms

def move_gif():
    """Función para mover el GIF de izquierda a derecha y cambiar su orientación."""
    global x_position, direction

    x_position += speed * direction

    if x_position >= max_width:  # Si llega al punto B, cambia de dirección
        direction = -1
    elif x_position <= 0:  # Si regresa al punto A, cambia de dirección
        direction = 1

    gif_label.place(x=x_position, y=430)  # Mueve el GIF sin interrumpir la animación
    root.after(30, move_gif)  # Llama a la función repetidamente

# Inicia la animación y el movimiento sin interrupciones
animate_gif()
move_gif()

# --------- Pantalla de Resultados ---------
results_frame = tk.Frame(root, bg="SteelBlue1")

results_label = tk.Label(results_frame, text="", font=("Fixedsys", 22, "bold"), fg=TEXT_COLOR, bg="SteelBlue1")
results_label.pack(pady=10)

name_entry = tk.Entry(results_frame, font=("Fixedsys", 12), width=15)
name_entry.pack(pady=5)
name_entry.insert(0, "Ingrese su nombre")

save_button = tk.Button(
    results_frame, 
    text="💾 Guardar y Regresar al Menú", 
    font=("Arial", 15, "bold"), 
    bg=BUTTON_COLOR, 
    fg="black", 
    activebackground=BUTTON_HOVER, 
    command=save_score
)
save_button.pack(pady=10)
save_button.bind("<Enter>", on_hover2)
save_button.bind("<Leave>", on_leave3)

view_answers_button = tk.Button(
    results_frame, 
    text="👀 Ver Respuestas", 
    font=("Arial", 15, "bold"), 
    bg=BUTTON_COLOR, 
    fg="black", 
    activebackground=BUTTON_HOVER, 
    command=show_answers_summary
)
view_answers_button.pack(pady=10)
view_answers_button.bind("<Enter>", on_hover2)
view_answers_button.bind("<Leave>", on_leave3)

# Cargar el GIF para la pantalla de resultados
results_gif_file = "resul.gif"
results_gif_info = Image.open(results_gif_file)
results_frames = results_gif_info.n_frames  # Número de fotogramas

# Tamaño del GIF
RESULTS_GIF_WIDTH = 300
RESULTS_GIF_HEIGHT = 300

# Función para eliminar fondo blanco
def remove_white_background_results(img):
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))  # Hacer transparente
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

# Lista de fotogramas del GIF
results_photoimage_objects = []

for frame in ImageSequence.Iterator(results_gif_info):
    frame = remove_white_background_results(frame)  # Eliminar fondo blanco
    resized_frame = frame.resize((RESULTS_GIF_WIDTH, RESULTS_GIF_HEIGHT), Image.Resampling.LANCZOS)
    results_photoimage_objects.append(ImageTk.PhotoImage(resized_frame))

# Etiqueta para mostrar el GIF en la pantalla de resultados
results_gif_label = tk.Label(results_frame, image="", bg="SteelBlue1")
results_gif_label.pack(pady=20)

results_current_frame = 0  # Control del frame de animación

def animate_results_gif():
    """Función para animar el GIF en la pantalla de resultados."""
    global results_current_frame
    results_gif_label.configure(image=results_photoimage_objects[results_current_frame])
    results_current_frame = (results_current_frame + 1) % results_frames
    root.after(80, animate_results_gif)  # Llamar a la función cada 150ms

# Iniciar la animación del GIF en la pantalla de resultados
animate_results_gif()

# --------- Pantalla de avance de nivel ---------
level_up_frame = tk.Frame(root, bg=BACKGROUND_COLOR)

level_up_label = tk.Label(level_up_frame, text="🎉 ¡Has avanzado al Nivel 2! 🎉", 
                          font=("Arial", 20, "bold"), fg="#FFD700", bg=BACKGROUND_COLOR)
level_up_label.pack(pady=20)

level_up_message = tk.Label(level_up_frame, text="Prepárate para preguntas más desafiantes. ¡Buena suerte! 🎯",
                            font=("Arial", 14), fg=TEXT_COLOR, bg=BACKGROUND_COLOR, wraplength=500)
level_up_message.pack(pady=10)

level_up_icon = tk.Label(level_up_frame, text="🚀", font=("Arial", 100), fg="white", bg=BACKGROUND_COLOR)
level_up_icon.pack(pady=20)

# Cargar el GIF
level_up_gif_file = "mision.gif"
level_up_gif_info = Image.open(level_up_gif_file)
level_up_frames = level_up_gif_info.n_frames  # Número de fotogramas

# Tamaño del GIF
LEVEL_UP_GIF_WIDTH = 200
LEVEL_UP_GIF_HEIGHT = 200

# Función para eliminar fondo blanco
def remove_white_background_level_up(img):
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))  # Hacer transparente
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

# Lista de fotogramas del GIF
level_up_photoimage_objects = []

for frame in ImageSequence.Iterator(level_up_gif_info):
    frame = remove_white_background_level_up(frame)  # Eliminar fondo blanco
    resized_frame = frame.resize((LEVEL_UP_GIF_WIDTH, LEVEL_UP_GIF_HEIGHT), Image.Resampling.LANCZOS)
    level_up_photoimage_objects.append(ImageTk.PhotoImage(resized_frame))

# Etiqueta para mostrar el GIF
level_up_gif_label = tk.Label(level_up_frame, image="", bg=BACKGROUND_COLOR)
level_up_gif_label.pack(pady=20)

level_up_current_frame = 0  # Control del frame de animación

def animate_level_up_gif():
    """Función para animar el GIF en la pantalla de avance de nivel."""
    global level_up_current_frame
    level_up_gif_label.configure(image=level_up_photoimage_objects[level_up_current_frame])
    level_up_current_frame = (level_up_current_frame + 1) % level_up_frames
    root.after(150, animate_level_up_gif)  # Llamar a la función cada 150ms

# Iniciar la animación del GIF de avance de nivel
animate_level_up_gif()

# --------- Iniciar la aplicación ---------
root.mainloop()
