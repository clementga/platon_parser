extends=base.pl
# Date : 16/06/2022
# Auteur : Clément Gaudet

doc==
Ce template permet de faire des exercices pouvant être résolu avec différents langages, au choix
de l'étudiant. 
==

settings.allow_reroll = 1

editor =: CodeEditor
editor.theme = dark
editor.height = 500px

# une interface standard d'exercice avec un editeur pour la réponse
form==
{{editor|component}}
==

languages==
==

showWanted = True

before==
==