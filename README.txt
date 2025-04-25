READ THIS TO CATCH UP ON OUR WORKFLOW                                                                           ^
                                                                                                                |
                                                                                                            PRESS THE SMALL
                                                                                                            SQUARES
                                                                                                            AT THE TOP
                                                                                                            TO OPEN/CLOSE
                                                                                                            CERTAIN BARS
                                                                                                            IF YOU ARE 
                                                                                                            READING IN
                                                                                                            VSCODE

------------------------------------- SETTING UP -----------------------------------------------------------

!IMPORTANT!
make sure you're on local main branch 
run | git branch --set-upstream-to origin main |
#this sets your local main branch upstream to origin (remote repository or GitHub) main branch

run | git pull |
#this will pull main from remote into your local main

MAKE SURE IN .gitignore, IT HAS THESE 3 THINGS:

- /__pycache__
- /.venv
- /instance

MAKE SURE TO NAME YOUR VIRTUAL ENVIRONMENT TO | .venv |

ACTIVATE YOUR VIRTUAL ENVIRONMENT (just run activatevenv.bat in terminal) THEN RUN | pip install -r requirements.txt |
#this will install all the libraries we need into your virtual environment

MAKE SURE WHEN YOU'RE RUNNING python main.py , YOU ARE IN YOUR VENV; CHECK IF THERE IS (.venv) next to your terminal

AFTER ALL OF THIS IS GOOD, YOU CAN run | git checkout -b INSERT_BRANCH_NAME |
#this will move you to another branch, THIS BRANCH IS WHERE YOU MAKE CHANGES! DON'T MAKE CHANGES ON MAIN BRANCH!
    AFTER ALL CHANGES ARE MADE STAGE(git add .) THEN, COMMIT(git commit -m "PUT USEFUL MESSAGE ON WHAT CHANGES YOU MADE") 
    THEN, PUSH(git push --set-upstream-to INSERT_BRANCH_NAME) THEN NOTIFY OTHERS YOU PUSHED YOUR CHANGES

DOWNLOAD SQLite Viewer extension to view users.db files

------------------------------------- SCRIPTING FORMAT -------------------------------------------------------
MAKE SURE TO UNDERSTAND ALL THE FILES/SCRIPTS AFTER YOU PULL FROM MAIN, I CAN'T TELL YOU ONE BY ONE, I 
HAVE OTHER SUBJECTS TO STUDY, ASK AI AND BE DESCRIPTIVE, COPY/PASTE THE CODE TO AI IF NEEDED; 
MAKE SURE THE AI UNDERSTANDS WHAT YOU'RE ASKING, AND YOU UNDERSTAND WHAT THE AI IS SHOWING DON'T JUST COPY FROM AI 
WITHOUT UNDERSTANDING

A SHORT SUMMARY IS
CSS WILL BE STORED AS INTERNAL CSS IN HTML FILES WHICH IS IN <styles> TAG
THERE ARE 2 COMPONENTS TO HTML,PARENT AND CHILD; PARENT HTML EXAMPLES ARE guestparent.html,homeparent.html
PARENT HTML IS BASICALLY THE TEMPLATE, AND CHILD HTML INHERIT THE TEMPLATE; CHILD HTML WILL HAVE {% extends "parent.html" %}
AT THE TOP OF IT, THEN IT WILL HAVE {% block blablabla %}{% endblock %} WHICH WILL PASS ANYTHING BETWEEN THOSE 
BLOCKS TO THE CORRESPONDING BLOCK IN PARENT HTML 

AFTER UNDERSTANDING ALL THE SCRIPTS YOU CAN BEGING WORKING ON YOUR FEATURES