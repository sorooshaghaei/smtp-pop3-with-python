import tkinter
from tkinter import *
import getpass
import poplib
import email
import io
from email import parser

def recieve() :
    #tkinter text edit update text
    msg_text.delete("1.0", END)
    msg_text.insert(END, "\n")
        
    google_pop3_server = 'pop.gmail.com'

    google_mailbox = poplib.POP3_SSL(google_pop3_server,'995')
    google_mailbox.set_debuglevel(1)
    pop3_server_welcome_msg = google_mailbox.getwelcome().decode('utf-8')


    google_mailbox.user(temp_username.get() )
    google_mailbox.pass_(temp_password.get())

    messages = [google_mailbox.retr(i) for i in range(1, len(google_mailbox.list()[1]) + 1)]
    # Concat message pieces:
    messages = ['\n'.join(map(bytes.decode, mssg[1])) for mssg in messages]
    #print("num of messages", len(messages))
    msg_text.insert(END, "-"*15 + "num of messages"+"-"*15+ '> '+ str(len(messages)))
    msg_text.insert(END, "\n")
    
    #Parse message intom an email object:
    messages = [parser.Parser().parsestr(mssg) for mssg in messages]

    for message in messages:
     
        #print ("subjet", message['Subject'])
        #print ("from",message['From'])
        msg_text.insert(END, "Subjet : " + message['Subject'] +"\n")
        msg_text.insert(END, "From : "+ message['From']+"\n")
    
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
                if type(body) == bytes :
                    #print("body ====")
                    #print(body.decode("utf-8") )
                    msg_text.insert(END, "============  message ==========="+"\n")
                    msg_text.insert(END, body.decode("utf-8") +"\n")
    
    #google_mailbox.quit()

#Main Screen Init
master  = Tk()
master.title = 'Custom Email App'

#labels
Label(master, text="Custom Email App", font=('Calibri',15)).pack()
Label(master, text="Please use the form below to check your mailbox", font=('Calibri',11)).pack()

notif = Label(master, text="", font=('Calibri', 11),fg="red")
notif.pack()

#storage
temp_username = StringVar()
temp_password = StringVar()


#Entries
user_frame = Frame(master)
user_frame.pack()
usernameEntry = Entry(user_frame, textvariable = temp_username)
usernameEntry.pack(side="top")
passwordEntry = Entry(user_frame, show="*", textvariable = temp_password)
passwordEntry.pack(side="top")

#Buttons
Button(master, text='Recieve', command=recieve).pack()
Button(master, text='Quit', command=master.quit).pack()


#emails text edit
frame = LabelFrame(
              master,
              text='emails : '
          )
frame.pack(
                    ipadx=10,
                    ipady=10, 
                    padx=20,
                    side='left',
                    fill='both',
                    expand=True
                )
h=Scrollbar(frame, orient='horizontal')
h.pack(side="bottom", fill='x')

          
msg_text = Text(frame, width=50, wrap=NONE, xscrollcommand=h.set)
msg_text.bind("<Key>", lambda e: "break") 
msg_text.configure(font=("Calibri", 11))
msg_text.pack(ipadx=10,
                 ipady=10,
                 padx=20,
                 fill='both',
                 expand=True
                 )
# Attach the scrollbar with the text widget
h.config(command=msg_text.xview)
          

master.mainloop()
