override=success

extends=inheritance.pl

statement ==
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Morbi auctor nunc nisi. Donec eu felis sapien. 
Nam porta libero nunc.
==

formState =: CodeEditor
formState.form.initialCode = print("Hello World")
formState.form.tabSize = 4
formState.form.language = python