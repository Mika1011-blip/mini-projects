import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
#libraries for removing stopwords and stemming
import pandas as pd
import tkinter as tk 
from tkinter import filedialog
def preprocess_french_nltk(text: str) -> str:
    stemmer = SnowballStemmer("french")
    stop_fr = set(stopwords.words("french"))
    tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ\d,]*", text.lower())
    tokens = [t for t in tokens if t not in stop_fr]
    stems  = [stemmer.stem(t) for t in tokens]
    return (" ".join(stems)).upper()
def iban2int(iban):
    new_iban = ""
    for c in iban.upper() :
        if c.isdigit():
            new_iban += c
        elif c.isalpha():
            new_iban += str(ord(c)-55)
    return new_iban
def chunk_calculate_key(r=0,converted_iban=None):
    #print(type(converted_iban))
    if len(converted_iban) > 9:
        return chunk_calculate_key(r= (r*(10**9) + int(converted_iban[:9]))%97,
                                                       converted_iban=converted_iban[9:])
    else :
        r = 98 - ((r*(10**len(converted_iban)) + int(converted_iban))%97)
        if r < 10 :
            return f"0{r}"
        else :
            return r
def generate_ibans(txt=None):
    cleaned_txt = txt.split("\n")
    acc_holder = []
    accs = []
    ibans = {} # key -> lines from txt that's used to generate iban, value -> iban number
    #clean text then generate iban
    for i_line,line in enumerate(cleaned_txt) :
        if not bool(re.search(r"[A-Za-z0-9]", line)) : # if no letter nor number in the line, we skip
            continue
        #cleaning part
        cleaned_txt[i_line] = line.split("\t")
        for i_word,word in enumerate(cleaned_txt[i_line]):
            #keep only uppercase letters and numbers
            if i_word == 0 :
                cleaned_txt[i_line][i_word] = preprocess_french_nltk(text = "".join([ch for ch in word.upper() if ch.isalpha() or 
                                                                          ch.isdigit() or 
                                                                            ch == " " or ch =="'"]))
            else :
                cleaned_txt[i_line][i_word] = "".join([ch for ch in word.upper() if (ch.isalpha() or ch.isdigit())])
                
        #generate iban part
        #print(cleaned_txt)
        acc_holder.append(cleaned_txt[i_line])
        #print(len(acc_holder))
        if len(acc_holder)%4 == 0:# if we read 4 lines
            acc_data = {} # store data in a dictionary
            checks = [0,0,0,0] # check if an account has complete 4 infos
            #print(acc_holder)
            for i_data, data in enumerate(acc_holder) :
                #print(data[0])

                #Check si tous les info sont présentes
                if "COD" in data[0] and "BANQU" in data[0] :
                    acc_data["CODE BANQUE"] = data[1]
                    checks[0] = 1
                elif "COD" in data[0] and "AGENC" in data[0] :
                    acc_data["CODE AGENCE"] = data[1]
                    checks[1] = 1
                elif "NUMERO" in data[0] and "COMPT" in data[0] and "BANCAIR" in data[0] :
                    acc_data["NUMERO DE COMPTE BANCAIRE"] = data[1]
                    checks[2] = 1
                elif "CHIFFR" in data[0] and "INDIQU" in data[0] and "NATIONAL" in data[0] :
                    acc_data["CHIFFRE D'INDICATIF NATIONAL"] = data[1]
                    checks[3] = 1

            if 0 in checks :
                print(checks)
                print(acc_holder)
                return f"Incomplete data in lines({i_line-2}-{i_line+1})"

            #Calculate ibans
            bban = f"{acc_data["CODE BANQUE"]}{acc_data["CODE AGENCE"]}{acc_data["NUMERO DE COMPTE BANCAIRE"]}{acc_data["CHIFFRE D'INDICATIF NATIONAL"]}"
            #print(bban)
            calculated_iban = f"FR{chunk_calculate_key(converted_iban = f"{iban2int(bban+"FR00")}")}"+bban
            ibans[f"{i_line-2}-{i_line+1}"] = f"{calculated_iban}"

            #restructure accounts info
            elements = ""
            for element in acc_holder :
                elements += " ".join(element) + "\n"
            accs.append(elements)

            #reset acc holder 
            acc_holder = []      
    return ibans,accs
def save_ibans(fname = "untitled", ibans : dict = None,ibans_acc : list = None):
    ibans_value = list(generated_ibans.values())
    ibans_corresponding_lines = list(generated_ibans.keys())
    pd_ibans = pd.DataFrame({"Ligne": ibans_corresponding_lines,
                            "IBAN":ibans_value,
                            "INFO":ibans_acc})
    pd_ibans.to_csv(f"{fname}.csv", index=False)
def open_app():
    #FAIT 90% PAR CHATGPT, JE NE PREND PAS CREDIT
    def import_file():
        path = filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("Text files", "*.txt *.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            s = f.read()
        input_txt.delete("1.0", "end")
        input_txt.insert("end", s)

    def generate_iban_bttn():
        # TODO: put your real logic here.
        data = input_txt.get("1.0", "end-1c")
        generated_ibans,_ = generate_ibans(data)
        dict_keys = list(generated_ibans.keys())
        dict_values = list(generated_ibans.values())
        composed_str = ""
        for i in range(len(generated_ibans)-1):
            composed_str += f"{dict_keys[i]} : {dict_values[i]}\n"
        output_txt.delete("1.0", "end")
        output_txt.insert("end", f"{composed_str}")

    def save_output_bttn():
        path = filedialog.asksaveasfilename(
            title="Save output",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(output_txt.get("1.0", "end-1c"))

    root = tk.Tk()
    root.title("Bulk IBAN Generator (BETA)")
    root.geometry("1000x600")

    # --- layout grid: top buttons (row 0), text areas (row 1) ---
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # Top-left: Import
    tl = tk.Frame(root)
    tl.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))
    btn_import = tk.Button(tl, text="Import", command=import_file)
    btn_import.pack()

    # Top-right: Generate + Save
    tr = tk.Frame(root)
    tr.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 6))
    btn_generate = tk.Button(tr, text="Generate", command=generate_iban_bttn)
    btn_save     = tk.Button(tr, text="Save", command=save_output_bttn)
    btn_generate.pack(side="left", padx=(0, 6))
    btn_save.pack(side="left")

    # Bottom: Input (left) and Output (right)
    input_txt = tk.Text(root, wrap="none", bd=1, relief="solid")
    output_txt = tk.Text(root, wrap="none", bd=1, relief="solid")

    input_txt.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(6, 10))
    output_txt.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(6, 10))

    root.mainloop()

open_app()