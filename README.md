# Atlas

## Description
Atlas is a language learning tool that allows a foreign text to be read with simultaneous translations and voices. It is a Windows desktop app that allows the user to use any .txt file to help learn a language. The inputted text is segmented into sentences and shown to the user one at a time with automated translations. DeepL and Google Translate provide the translations, and this app supports any language that these services support. This app features Anki compatibility, allowing a user to easily add any sentence pairs into Anki.
## Installation
1. Download Atlas.zip and Atlas - Segmentation Models.zip from the latest release
2. Extract Atlas.zip to a folder of your choosing.
3. Extract Atlas - Segmentation Models.zip into the Atlas folder.
4. Run Atlas.exe
## Usage
Upon first use, the app will prompt the user to edit the configuration to add a text and select it. The program is packaged with several sample texts, but a user may use a .txt file of their own. Before a text can be used, the app must first convert it for use with the app. This may take several seconds. The language of the text is automatically detected, and if the resulting text snippet looks correct, i.e. only a single sentence is shown and the characters are displayed correctly, the user can add the text for use with the app. The user can then select the text they would like to use. Any number of texts can be converted for use with this app, and they can be switched between freely. After saving the config, the user can begin using the text. 

![image](https://github.com/ICantRanch/Atlas/blob/master/Screenshot%202026-02-16%20133641.png)

There are controls on the bottom edge of the app, displayed with their optional hotkeys. 'Advance' will show the user the next sentence in the text. The app will first show a sentence in the user's native language, and when ready the user can advance again to show the original sentence. An automated voice of the original sentence will also play. The user can press the 'Replay Voice' button to replay the voice. The app will also show literal translations for each individual word. This can be useful to determine which word means what in the greater context of a sentence. The 'Revert' button will show the previous sentence. The 'Index' or sentence number is displayed in the top right, along with the percentage completion of the current text. The index for each text is unique. If a user wishes to advance or revert more than 1 sentence at a time, they can use the 'Go to index' button to go to an index of their choosing.

By pressing the 'Save to Output' button, the current sentence and its translation will be added as a pair to a file for use outside of the app. This file is formatted for easy import into Anki. The file can be found in the Output folder inside the Atlas folder. A user can click the 'Output Cards' label to open that folder. The folder will contain 2 files. The 'Last Session' file contains any sentence pairs that were added in the last session of Atlas. The 'Output Cards' label will display the number of sentence pairs added this session. The folder also contains a 'Total' file which contains all saved sentence pairs from when the app was first used.


