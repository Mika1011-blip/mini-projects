from vad_record_utterance import record_one_utterance, SR
from stt_whisper import STT
from commands import *
from llmModel import get_modelReply
import regex as re
from say_melo import say
import os
os.environ["TQDM_DISABLE"] = "1"

language = "EN"
stt = STT(model_name="large-v3", device="cuda", compute_type="float16",language="en")
sys_name = "EMMA"
user_name = "MIKA"

RESET = "\033[0m"
GREEN = "\033[32m"
CYAN  = "\033[36m"

_EMPTY_PAT_EN  = re.compile(r"^(empty|clear|delete|wipe|reset)\s+(the\s+)?vault$")
_OPEN_PAT_EN   = re.compile(r"^(open|show|read|display|print)\s+(the\s+)?vault$")
_INSERT_PAT_EN = re.compile(r"^(insert|add|save|store|remember)\s+(to\s+)?(the\s+)?vault$")

# FR
_EMPTY_PAT_FR  = re.compile(r"^(vider|effacer|supprimer|nettoyer|réinitialiser|reinitialiser)\s+(le\s+)?(coffre|vault)$")
_OPEN_PAT_FR   = re.compile(r"^(montrez|ouvrir|montrer|afficher|lire|voir|imprimer)\s+(le\s+)?(coffre|vault)$")
_INSERT_PAT_FR = re.compile(
    r"^(insérer|inserer|ajouter|sauvegarder|enregistrer|stocker|mémoriser|memoriser)\s+"
    r"(dans\s+|au\s+|sur\s+)?(le\s+)?(coffre|vault)$"
)
# YES (EN+FR)
_YES_PAT = re.compile(
    r"^(yes|y|yeah|yep|sure|ok|okay|affirmative|confirm|confirmed"
    r"|oui|o|ouais|ouai|yep|daccord|d'accord|ok|okay|bien\s*s[uû]r|certainement|confirme|confirm[eé])$"
)

# NO (EN+FR)
_NO_PAT = re.compile(
    r"^(no|n|nope|nah|negative|cancel|stop"
    r"|non|n|nan|nope|annule|annuler|stop|arrete|arrête)$"
)

def _normalize(s: str) -> str:
    s = s.lower().strip()
    # keep letters/numbers/space; turn other chars into spaces
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sys_output(message: str):
    return f"{GREEN}[{sys_name}] : {message}{RESET}"
def user_output(message: str):
    return f"{CYAN}[{user_name}] : {message}{RESET}"

def excute_command(text : str):
    cleaned_text = _normalize(text)
    if _EMPTY_PAT_EN.match(cleaned_text) or _EMPTY_PAT_FR.match(cleaned_text):
        sys_message = "Are you sure to empty vault.txt ?"        
        print(sys_output(sys_message))
        say(text=sys_message,language=language)
        audio = record_one_utterance()
        if audio is None:
            print("No utterance.")
            return
        user_message = stt.transcribe(audio, vad_filter=True, beam_size=5, best_of=5, temperature=0.0)
        if _YES_PAT.match(_normalize(user_message)) :
            print(user_output(user_message))
            empty_vault()
            print(sys_output("Emptied vault.txt"))
        else :
            print(user_output(user_message))
            return

    elif _OPEN_PAT_EN.match(cleaned_text) or _OPEN_PAT_FR.match(cleaned_text):
        vault_content = open_vault()
        print("_"*25,"vault.txt","_"*25)
        print(vault_content)
        print("_"*25,"END","_"*25)

    elif _INSERT_PAT_EN.match(cleaned_text) or _INSERT_PAT_FR.match(cleaned_text):
        sys_message = "What do you want to insert ?"
        print(sys_output(sys_message))
        say(text=sys_message,language=language)

        audio = record_one_utterance()
        if audio is None:
            print("No utterance.")
            return
        insert_content = stt.transcribe(audio, vad_filter=True, beam_size=5, best_of=5, temperature=0.0)
        sys_message = "Are you sure to insert this message to vault.txt ?"
        print("_"*25,"insert_content","_"*25)
        print(insert_content)
        print("_"*25,"END","_"*25)
        print(sys_output(sys_message))
        say(text=sys_message, language=language)
        audio = record_one_utterance()
        if audio is None:
            print("No utterance.")
            return
        user_message = stt.transcribe(audio, vad_filter=True, beam_size=5, best_of=5, temperature=0.0)
        if _YES_PAT.match(_normalize(user_message)) :
            print(user_output(user_message))
            insert_vault(content=insert_content)
            print(sys_output("Inserted to vault.txt"))
        else : 
            print(user_output(user_message))
            return
    else :
        sys_message = get_modelReply(user_message=text)
        print(sys_output(sys_message))
        say(text=sys_message, language=language)
    return

i = 0
while True:
    audio = record_one_utterance(i)
    if audio is None:
        print("No utterance.")
        continue
    user_message = stt.transcribe(audio, vad_filter=True, beam_size=5, best_of=5, temperature=0.0)
    print(user_output(user_message))
    excute_command(user_message)
    i += 1
