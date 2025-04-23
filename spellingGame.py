# layout
# top frame: labels for word, a guess button
# middle frame: guess label with entry and guess button
# bottom frame includes a game button

import random
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import pymongo
import gridfs
import os
from PIL import Image, ImageTk
import io

## functions
def guessClick():

    global guess_count, count_left, win, loss, nb_right

    if game_on:
        count_left -= 1
        #print(count_left)
        # get guess input
        l_right = 0 # number of letters guessed right
        l_guessed=guess_entry.get()
        current_text = ""
        if l_guessed:
            if l_guessed.lower() not in current_word:
                #print("not in the word!")
                current_text = f"Letter '{l_guessed.upper()}' doesn't exist in the word!"

            label_indx = 0
            for l in current_word:
                if l_guessed.lower() == l.lower() and label_indx not in guessed_indx:
                #if l_guessed.lower() == l.lower():
                    guessed_letters.insert(label_indx, l)
                    guessed_indx.append(label_indx)
                    labels[label_indx].config(text=l.upper())
                    current_text = f"Letter '{l_guessed.upper()}' has been found!"
                    print(f"guessed list: {guessed_letters}, stored_indx: {guessed_indx}, label_indx: {label_indx}")         
                    l_right += 1
                    #break
                
                #if l_guessed.lower() != l.lower():
                    #print("I have here anyway!!")
                    #current_text = f"Letter '{l_guessed.upper()}' doesn't exist in the word!"
                    #label_guess.config(text=f"Letter: {l_guessed} has been found!  {count_left} attempt left!")
                label_indx += 1
                #print(f"l: {l}; l_guessed: {l_guessed}; {l_right} right guessed")
            label_guess.config(text=f"{current_text}  {count_left} attempt left!")
        else:
            label_guess.config(text=f"Please enter a letter!   {count_left} attempt left!")
         
        guess_entry.delete(0, tk.END)
        
        #print(f"loss: {loss}")
        nb_right = nb_right + l_right
        #print(nb_right)

        if count_left < 0:
            loss = True
            endGame()
        elif len(guessed_letters) == len(current_word):
            win = True
            endGame()
        
        

        #print(f"geuss attempt {guess_count}, guessed letter: {l_guessed}")
    else:
        print(f"click Start")

    return 

def endGame(): 
    # win or loss
    
    info = ""
    if loss:
        info = f"You loss! {current_word.upper()} is looked for. \nMaximum {max_count} attempts have been reached! \nPlease try again."       
        #print("You loss!")
    elif win:
        nb_attempt = max_count - count_left
        info = f"You win! \nA '{current_word.upper()}' is found! \nNumber of attempts {nb_attempt}"  
        #print("You win!")

    messagebox.showinfo("", info)

    resetClick()

    

    
def initialClick(): # initialize game and prepare for reset

    welcome_label.grid_forget()

    global game_on, current_word, count_left, nb_right, win, loss
    game_on = True
    win = False
    loss = False

    count_left = max_count
    nb_right = 0

    # randomly choose a word from words list
    word_indx = random.randrange(len(words)) # get a random number in range of the word list size
    current_word = words[word_indx] 

    # get animal info from data base
    animal = current_word

    metadata_animal = db.figures.find_one({"title": f"{animal}"})
    image_animal_name = metadata_animal["title"]
    image_animal_description = metadata_animal["description"]

    # Fetch image from GridFS
    fs = gridfs.GridFS(db)
    image_animal = fs.get(metadata_animal["image_id"]).read()

    # Convert to Tkinter-compatible image
    image = Image.open(io.BytesIO(image_animal))
    photo = ImageTk.PhotoImage(image)

    image_label.config(image=photo)
    title_label.config(text=f"{image_animal_description}")

    #image_label = tk.Label(figure_frame, image=photo, pady=10)
    #title_label = tk.Label(figure_frame, text=f"{image_animal_description}", font=('Arial', 12, 'bold'), pady=10)

    image_label.pack(expand=True)
    title_label.pack()

    image_label.image = photo
    
    # split letters in the word and make a list out of it
    l_list = list(current_word)
    print(f"word choice: {current_word}, lenght: {len(l_list)}")

    # create labels for word dynamically
    indx = 0
    for l in l_list:
        #print(f"{l}")
        l_label = tk.Label(top_frame, text=" ", width=2, font=("Arial", 48), bg="Blue", fg="White")
        l_label.grid(row=1, column=indx, padx=15, pady=15) 
        labels.append(l_label)
        indx = indx + 1
    
    # create guess button
    label_guess.config(text=f"Let's spell it! {count_left} attempt left!")
    button_guess.config(text="Click to spell a letter!",state="active")
    button_guess.grid(row=0, column=0, padx=5, pady=15) 
    guess_entry.grid(row=0, column=1, padx=35, pady=15)
    label_guess.grid(row=1, columnspan=2, padx=15, pady=5)


    # update button state
             
    button_play.config(text="Reset",command=resetClick)
    return

def resetClick(): # reset game and prepare for initialization

    global game_on
    game_on = False

    # update label state
    for l in labels:
        l.grid_forget()

    # update game state
    button_guess.config(state="disabled")
    label_guess.grid_forget()
    guessed_letters.clear()
    guessed_indx.clear()
    labels.clear()
    image_label.grid_forget()
    title_label.grid_forget()
    #button_play.config(text="Start",command=initialClick)
    #welcome_label.grid(row=0, column=0)
    initialClick()
    
    return

def validate_input(new_text):
    # Allow empty (for backspace) or exactly one alphabetic character
    return (len(new_text) <= 1 and (new_text == "" or new_text.isalpha()))
  

## Create main window
root = tk.Tk()
root.title("Basic GUI Window")
root.geometry("1000x600")

## Top-frame inludes a welcome label appearing only once 
top_frame = tk.Frame(root)
top_frame.pack(expand=True)
#
welcome_label = tk.Label(top_frame, text="Spelling Game!", font=("Arial", 24), width=20, fg="Blue")
welcome_label.grid(row=0, column=0)

## Figure frame
figure_frame = tk.Frame(root)
figure_frame.pack(expand=True, fill='both', padx=10, pady=10)
image_label = tk.Label(figure_frame, pady=10)
title_label = tk.Label(figure_frame, text="", font=('Arial', 12, 'bold'), pady=10)

## Middle-frame includes a guess filed with label, button and entry
mid_frame = tk.Frame(root)
mid_frame.pack(expand=True)
#
vcmd = (mid_frame.register(validate_input), '%P')
label_guess = tk.Label(mid_frame, text="")
button_guess = tk.Button(mid_frame,text="Guess",command=lambda: guessClick(), state="disabled")
guess_entry = tk.Entry(mid_frame, textvariable=" ", width=5, validate="key", validatecommand=vcmd, borderwidth=5)


## Bottom-frame includes a game filed with a button for intialize and reset the game
bottom_frame = tk.Frame(root)
bottom_frame.pack(expand=True)
button_play = tk.Button(bottom_frame, text="Start",command=initialClick)
button_play.pack(expand=True)

## Game attributes
# a list of words contents animals from data base
path = os.getenv("MONGODB_VARIABLE")
#print(f"mogodb path: {path}")
client = pymongo.MongoClient(path)
db = client['animal_database']
collection = db['figures']

words = []

for document in collection.find({}):
    if 'title' in document:
        words.append(document['title'])
        print(f"{document['title']}")

# a list of labels store letters of the chose word
labels = []

global guess_count, max_count, guessed_letters, guessed_indx
guess_count = 0
max_count = 20
guessed_letters = []
guessed_indx = []


# run game
root.mainloop()