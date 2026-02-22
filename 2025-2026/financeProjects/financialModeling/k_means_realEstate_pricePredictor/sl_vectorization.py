"""
Read vectoize_dataset_seloger.ipynb for more details
"""
#manipulate/organize data/visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#preprocess data
import unicodedata as ud
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
#Linear regression to fill missing data for certain types
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_absolute_error, r2_score


# In[50]:


"""
    the first dataset (about 1500 properties) i scraped only contain these locations. 
    (i carefully extracted all preprocessed tokens and collect all distinct locations to make this list,
    i added some exception for some locations because my preprocessing code don't reduce them exactly like some other do.
    Although it's not me who assigned them the postcodes.
"""
STEM_TO_POSTCODES = {
    "BOULOGN": "92000",                       # Boulogne-Billancourt
    "BILLANCOURT": "92000",                   # Boulogne-Billancourt
    "BOULOGN BILLANCOURT": "92000",           # Boulogne-Billancourt
    "NEUILLY": "92000",                       # Neuilly-sur-Seine
    "NEUILLY SEIN": "92000",                  # Neuilly-sur-Seine
    "LEVALLOIS PERRET": "92000",              # Levallois-Perret
    "CLICHY": "92000",                        # Clichy
    "CLICHY GAREN": "92000",                  # Clichy-la-Garenne (same CP)
    "SAINT CLOUD": "92000",                   # Saint-Cloud
    "CLOUD": "92000",                         # Saint-Cloud
    "PUTEAU": "92000",                        # Puteaux
    "SURESN": "92000",                        # Suresnes
    "ISSY": "92000",                          # Issy-les-Moulineaux
    "ISSY MOULINEAU": "92000",                # Issy-les-Moulineaux
    "MOULINEAU": "92000",                     # Issy-les-Moulineaux
    "MONTROUG": "92000",                      # Montrouge
    "LE LIL": "93000",                        # Les Lilas
    "AUBERVILLI": "93000",                    # Aubervilliers
    "SAINT OUEN SEIN": "93000",               # Saint-Ouen-sur-Seine
    "OUEN": "93000",                          # Saint-Ouen-sur-Seine
    "CHARENTON": "94000",                     # Charenton-le-Pont
    "CHARENTON PONT" : "94000",
    "VANV": "92000",                          # Vanves
    "MONTREUIL": "93000",                     # Montreuil
    "PANTIN": "93000",                        # Pantin
    "PONT": "94000",                          # (mapped by you to Charenton-le-Pont)
    "SEIN": "92000",                          # (mapped by you to Neuilly-sur-Seine)
    "SAINT DEN" : "93000",
    "DEN": "93000",                           # Saint-Denis
    "PARIS": "75000",
    "BAGNOLET": "93000"
}
#decide which tokens are valid, other tokens were not carefully analyzed by humans therefore would likely to produce errors, and inaccuracy.
valid_tokens = {'APPART A VENDR',
     'AUBERVILLI',
     'BAGNOLET',
     'BOULOGN BILLANCOURT',
     'CHAMBR',
     'CHARENTON PONT',
     'CLICHY',
     'CLICHY GAREN',
     'DISPONIBL MAINTEN',
     'DIVISIBL',
     'DUPLEX A VENDR',
     'ETAG',
     'HOTEL PARTICULI A VENDR',
     'ISSY MOULINEAU',
     'LE LIL',
     'LEVALLOIS PERRET',
     'LOFT A VENDR',
     'MAISON A VENDR',
     'MAISON VILL A VENDR',
     'MONTREUIL',
     'MONTROUG',
     'M²',
     'NEUF',
     'NEUILLY SEIN',
     'PANTIN',
     'PARIS',
     'PIEC',
     'PUTEAU',
     'RDC',
     'SAINT CLOUD',
     'SAINT DEN',
     'SAINT OUEN SEIN',
     'STUDIO A VENDR',
     'SURESN',
     'TERRAIN',
     'TERRAIN CONSTRUCTIBL A VENDR',
     'VANV',
     'VILL A VENDR'}
"""
     We decide to only analyze residential properties and remove all commercial properties,
     later, we will drop all type (categorical data, include postcodes) that do not meet necessary threshold number of datapoint (property).
"""
valid_types = {
    'APPART A VENDR',
    'DUPLEX A VENDR',
    'LOFT A VENDR',
    'MAISON A VENDR',
    'MAISON VILL A VENDR',
    'STUDIO A VENDR',
    'TERRAIN CONSTRUCTIBL A VENDR',
    'VILL A VENDR'
}

#regrex patterns to identify and extract or to replace patterns in string.
# Currency tokens (symbol or word forms)

EUR_PATTERN = re.compile(
    r"(€|\b(?:eur|euro(?:s)?)\b)", re.IGNORECASE
)
GBP_PATTERN = re.compile(
    r"(£|\b(?:gbp|pound(?:s)?)\b)", re.IGNORECASE
)
USD_PATTERN = re.compile(
    r"(\$|\b(?:usd|dollar(?:s)?)\b)", re.IGNORECASE
)
NUM_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")
ORDINAL_PATTERN = re.compile(r"\b\d+(?:ER|EM)\b", flags=re.IGNORECASE)
PARIS_PATTERN = re.compile(r"PARIS")
PATTERN_NUM = re.compile(r"[+-]?\d+(?:\.\d+)?")

PATTERN_AREA = re.compile(r"(?:[-–—]?\s*)(?:M(?:²|2)|SURFAC\w*|TERRAIN)", re.I)
PATTERN_TERRAIN = re.compile(r"\bTERRAIN\b", re.I)
PATTERN_HAS_DIGIT = re.compile(r"\d")
PATTERN_DISPO_NOW = re.compile(r"\bDISPONIBL\w*\s+MAINTEN\w*\b", re.I)
PATTERN_FLOOR = re.compile(r"\b(?:ETAG\w*|RDC)\b", re.I)
PATTERN_ETAG = re.compile(r"\bETAG\w*\b", re.I)
PATTERN_RDC = re.compile(r"\bRDC\w*\b", re.I)
PATTERN_PIECE = re.compile(r"\bPIEC\w*\b", re.I)
PATTERN_NEUF = re.compile(r"\bNEUF\w*\b", re.I)
PATTERN_CHAMBRE = re.compile(r"\bCHAMBR\w*\b", re.I)
PATTERN_BEFORE_SLASH = re.compile(r"([+-]?\d+(?:\.\d+)?)\s*/")
PATTERN_AFTER_SLASH = re.compile(r"/\s*([+-]?\d+(?:\.\d+)?)")
PATTERN_SLASH = re.compile(r"/")
def remove_accents(text: str)->str:
    """
    this function serve to remove accents and diacritics of french alphabet.
    input string
    output string
    """
    #replace diacritics
    text = (text.replace("œ", "oe").replace("Œ", "OE")
           .replace("æ", "ae").replace("Æ", "AE"))
    #decompose form 'è' -> 'e' + '`'
    text = ud.normalize("NFD",text)
    #remove accents like '`','^',...
    text = "".join([char for char in text if ud.category(char) != "Mn"])
    #recompose 
    text = ud.normalize("NFC",text)
    return str(text)


# In[60]:


def preprocess_french_nltk(text: str)->str:
    """
    this function serve to normalize tokens, preprocess the texts to better detect patterns,repetition of tokens.
    input string
    output string
    """
    #get text that doesn't have accents.
    text = remove_accents(text)
    stemmer = SnowballStemmer("french")#prepare stemming process for french.
    stop_fr = set(stopwords.words("french"))#prepare stopwords removal for french (stopwords are à de la le etc..)
    #extract tokens from text under french alphabet condition and m2/m^2 for extracting area value
    tkns = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ\d/(m2|m²).]+", text)
    tkns = [t for t in tkns if t not in stop_fr]#adding to a list if token not in stopwords (to remove stopwords we defined earlier)
    stems  = [stemmer.stem(t) for t in tkns]#stem, normalize words, for ex in english GO and GOES all normalized to GO (i dnt have ex in fr)
    return (" ".join(stems)).upper()
preprocess_french_nltk("test : go goes")


# In[54]:


"""
- after brief visual inspection of the scraped data, we can find some patterns like, 
pieces of informations are separated by "-" and ",".
- but we have some "," that belongs to decimal numbers (e.g. 1,2 5,9 3,14 etc).
- let's find the distinction between between seperation by "," and "," for decimals,
we concluded that "," for decimal stick with numbers and "," to separate pieces of information is between 2 spaces.
- let's replace "," for decimal by a ".".
"""
def extract_tokens(text : str = ""):
    #convert "," of float num to "."
    text = re.sub(r"(?<=\d),(?=\d)",".",text)
    #convert "-" to " "
    text = re.sub(r'(?<=[^\W\d_])-(?=[^\W\d_])', ' ', text, flags=re.UNICODE)
    tkns = [tkn.strip() for tkn in re.split("[-,]",text)]
    return tkns

def convert_2price(price_str : str = None):
    """
        to extract price,
        price is in format like :
        1234(some unicodedata)5678(some unicodedata)90
        - we are just gonna get the digit and ignore the *special char with escape sequence*, 
        because big price don't need decimal numbers, it's useless (probably).
    """
    try :
        #get the point pattern (remember we convert all "," to "." if it's a decimal point)
        where_is_the_point = re.compile(r"\.")
        #get matches
        matches = list(where_is_the_point.finditer(price_str))
        #initalize stop index (default'd be end of the input string)
        stop_index = len(price_str)
        #if theres a match, reassign stop index to the start index of the "."
        if matches :
            for match in matches :
                stop_index = match.start()
                break
        price_str = "".join([chr for chr in price_str[:stop_index] if chr.isdigit()])#search only from 0 to the stop index
        return float(price_str)
    except Exception :
        return None
# In[92]:


def extract_price(tkns : list = None):
    """
    -function to extract price token.
    -input tokens : list (but actually it works both for tuple,set too but i only allow list here.)
    -output list of [[*tokens with out price token*],*price token*]
    """
    if not tkns :
        raise ValueError("elements = None")
    #create patterns.
    EUR_PATTERN = re.compile(r"(€|\b(?:eur|euro(?:s)?)\b)", re.IGNORECASE)
    GBP_PATTERN = re.compile(r"(£|\b(?:gbp|pound(?:s)?)\b)", re.IGNORECASE)
    USD_PATTERN = re.compile(r"(\$|\b(?:usd|dollar(?:s)?)\b)", re.IGNORECASE)
    #m_tkns for the tokens without price token, prices are price we find.
    m_tkns = []
    prices = []
    #loop throught tokens to categorize.
    for tkn in tkns :
        if bool(EUR_PATTERN.search(tkn)):
            prices.append([tkn,"EUR"])
        elif bool(GBP_PATTERN.search(tkn)):
            prices.append([tkn,"GBP"])
        elif bool(USD_PATTERN.search(tkn)):
            prices.append([tkn,"USD"])
        else :
            m_tkns.append(tkn)
    if len(prices) != 1:
        raise ValueError("More than 1 or no price for this property")
    return [m_tkns,prices[0]]


# In[94]:


def get_processed(raw_df):
    """
    just a function to apply all the functions i created above.
    input df (pd.DataFrame or pandas.DataFrame depend how you assign alias)
    output df with cols (names i mention in return line)
    """
    list_tags = []
    prices =[]
    price_units = []
    raws = []
    for i in range(len(raw_df)):
        tags,(price_str,price_unit)=extract_price(extract_tokens(raw_df.iloc[i]))
        tags = list(map(preprocess_french_nltk,tags))
        price = convert_2price(price_str)
        if price == None :
            print(price_str)
        if price > 1000 :# add threshold to prevent false pricing, or maybe i just don't like extreme little houses/appartments
            list_tags.append(tags)
            prices.append(price)
            price_units.append(price_unit)
            raws.append(raw_df.iloc[i])
    return (pd.DataFrame({"RAW" : tuple(raws),"DATA TAG":list_tags,"PRICE":prices,"PRICE_UNIT":price_units}))


# In[96]:


def normalize_token(tag):
    """
    function to normalize tokens, well, in short, i just don't like meaningless variations like "12eme PARIS" or "15eme PARIS",
    they are all "PARIS", so lets consider them this way, and don't worry, im not erasing the info of it's district,
    just putting all these normalized tokens in a different column so it would be easier to find and to list and to analyze and to inspect.
    but i suppose i can achieve the same result with regrex, but i find it much much simpler this way.
    - input string
    - output string, or None-(isn't an efficient way but we learn along the way)
    """
    tag = tag.upper().strip()
    if "ETAG" in tag :
        return "ETAG"
    if 'RDC' in tag:    
        return 'RDC'
    """
    if 'TERRAIN' in tag:
        return 'TERRAIN'
    """
    if 'SURFAC' in tag:
        return 'SURFAC'
    #remove tags
    if 'DIVISIBL A PART M²' in tag or 'DIVISIBL JUSQU A M²' in tag or 'DIVISIBL M² A M²' in tag:
        return None
    #reduce all M² to M²
    if 'M²' in tag :
        return 'M²'

    # Remove ordinals like 1ER / 12EM and plain numbers/decimals
    tag = ORDINAL_PATTERN.sub('', tag)
    tag = tag.replace('/', ' ')            # split fractions like "1/7"
    tag = NUM_PATTERN.sub('', tag)

    # Collapse whitespace
    tag = re.sub(r'\s+', ' ', tag).strip()

    return tag
#apply the normalize to tags (PLURAL)
def normalize_tags(tags):
    n_tkns = [] #normalized tokens
    for tkn in tags :
        if str(tkn).strip() :
            n_tkn = normalize_token(tkn)
            if n_tkn:
                if n_tkn in valid_tokens :#verify if it's valid tokens.
                    n_tkns.append(n_tkn)
                else :
                    return pd.NA
    if len(n_tkns) == 0 :
        return None
    return tuple(n_tkns)
def clean_tags(seqs):
    return {normalize_sequence(tags) for tags in seqs }
def extract_type(cleaned_tags):
    """
    to extract type of property ("APPART A VENDR" or "MAISON A VENDR" , etc)
    """
    for t in cleaned_tags :
        if t in valid_types : # only return allowed types
            return t
    return pd.NA#to drop them later.
def get_paris_cp(tags):
    """
    get paris codepostal.
    it's designed for paris because, other districts don't matter. and we won't have that much data to futher divide categories.
    - possible input list,tuple,set of tokens, also sometime tags can be referred to sequences (seqs).
    - output : string (e.g. "75015",...)
    """
    paris_tag = ""
    for tag in tags :
        if "PARIS" in tag :
            if not bool(re.search(r"\d", tag))  :#if find no digit
                print("Got tag with no digit : ", tag)
                return None
            try :
                digits = int("".join([ch for ch in tag if ch.isdigit()]))
                if digits <= 20 and digits > 0:
                    return str(75000 + int(digits))
                else :
                    print("District code doesn't exist")
                    return None
            except Exception :
                print(f"Error encountered (got digits = {digits}): ", tag)
                return None
    return None
#now let's extract all locations to a column
def extract_loc(df,dict_map):
    """
    extract_loc is gonna focus on inside paris, and others will be more generalized.
    - inputs :
        + df -> pd.DataFrame
        + dict_map : a dict that contains locations mapped with codepostals.
    - output : dataframe with loc col (extracted codepostals in string type)
    """
    df= df.copy()
    mask_not_paris = df["CLEANED TAG"].apply(lambda x: isinstance(x, (list, tuple, set)) and "PARIS" not in x)
    valid_locs = set(dict_map.keys())
    df.loc[mask_not_paris, "LOC"] = (
        df.loc[mask_not_paris, "CLEANED TAG"]
          .apply(lambda x: (set(x) & valid_locs) if x else pd.NA)
          .apply(lambda x: {dict_map[c] for c in x} if x else pd.NA)
    )
    df.loc[~mask_not_paris,"LOC"] = (
        df[~mask_not_paris]["DATA TAG"].apply(lambda x : set([get_paris_cp(x)]) if get_paris_cp(x) else pd.NA)
    )
    mask_multi_loc = df["LOC"].apply(lambda x: isinstance(x, (list, tuple, set)) and len(x) > 1)
    #print("Multi loc assigned detected : ",(mask_multi_loc & mask_not_paris).sum())
    return df
def _numbers_in_text(s):
    """Return all numbers (as floats) found in a string. Spaces already preprocessed upstream."""
    if not isinstance(s, str):
        return []
    s_clean = s.replace(" ", "")  # e.g. '2 645' -> '2645'
    return [float(m.group(0)) for m in PATTERN_NUM.finditer(s_clean)]
"""
Now let's extract area, we know that area can be represented in 3 tags/tokens : 
-M²
-SURFAC
-TERRAIN
"""
def extract_area(df):
    """
    Normalize surface data into two scalars per row:
      - AREA: one scalar for all non-TERRAIN surfaces (or TERRAIN tokens without digits)
      - TERRAIN: one scalar for terrain (only if the token contains 'TERRAIN' + a digit)
      - some special case will be handled (if there are), case where a token/tag contains "DIVISIBL", would often contains more than 1 area value,
      we decide to take the min area for the indicated price (that's often how marketing do)
    Inputs:
      df: DataFrame
    Returns:
      new df with cols AREA,TERRAIN, both in float type.
    """
    #create a set for tokens/tags that we area interested in extracting.
    area_tags = {"M²","SURFAC","TERRAIN"}
    #create a mask for token/tag that contains patterns in area_tags.
    has_area = df["CLEANED TAG"].apply(
        lambda xs: bool(set(xs) & set(area_tags)) if isinstance(xs, (list, tuple, set)) else False
    )
    #remove all rows that don't contain any area_tags, those miss the most crucial feature in determining a property value.
    out = df.loc[has_area].copy()
    #function to extract all tokens that match tags M,M^2,SURFAC,TERRAIN patterns.
    def get_area_tokens(tokens):
        """
        input : tokens type list,tuple,set (we are extracting from DATA TAG so it's likely to be a list.)
        output : pd.NA if any or list of matched tokens.
        """
        #just safety condition if tokens is type list,tuple,set
        if not isinstance(tokens, (list, tuple, set)):
            return pd.NA#assign them pd.NA
        #a list to store matched tokens
        hits = []
        for t in tokens:#loop token in tokens
            if re.search(PATTERN_AREA, str(t)):#if found
                hits.append(str(t))#convert the token to string and add to hits list
        if hits:
            return hits
        return pd.NA
    #put all extracted tokens in a col named "ALL AREA" represent both AREA and TERRAIN scalars, we will separate them later.
    out["ALL AREA"] = out["DATA TAG"].apply(
        lambda x: get_area_tokens(list(x)) if isinstance(x, (list, tuple, set)) else pd.NA
    )
    #function to get the lowest number found in a tag/token (designed for tag that contains multiple area values like "DIVISIBL")
    def get_lowest_value(tokens):
        if not tokens:
            return pd.NA
        vals = []
        for t in tokens:
            try:
                vals.extend(_numbers_in_text(t))#store 
            except Exception:
                pass#if don't find any number or incompatible token/function
        return min(vals) if vals else pd.NA
    def is_divisible(tokens):
        if not tokens:
            return pd.NA
        for t in tokens:
            if isinstance(t, str) and "DIVISIBL" in t:
                return True
        return False
    def split_area_vs_terrain(tokens):
        if not isinstance(tokens, (list, tuple, set)):
            return [], []
        area_tokens, terrain_tokens = [], []
        for t in tokens:
            t_str = str(t)
            has_terrain = bool(PATTERN_TERRAIN.search(t_str))#if tag/token has "TERRAIN" pattern.
            has_digit   = bool(PATTERN_HAS_DIGIT.search(t_str))#same for digit.
            if has_terrain and has_digit:
                terrain_tokens.append(t_str)#that's a scalar for TERRAIN.
            else:
                area_tokens.append(t_str)#that's a scalar for AREA.
        return area_tokens, terrain_tokens
    #compute scalars for AREA and TERRAIN from 'ALL AREA'
    def compute_scalars(tokens):
        if not isinstance(tokens, (list, tuple, set)) or not tokens:
            return pd.Series({"AREA": pd.NA, "TERRAIN": pd.NA})#in case theres nothing, we return with cols that contains pd.NA
        #get area,terrain tokens.
        area_tokens, terrain_tokens = split_area_vs_terrain(tokens)
        if area_tokens:#area tokens is considered all tokens without "TERRAIN" pattern.
            area_val = get_lowest_value(area_tokens)#in case have multiple area values in on area token ("DIVISIBL" case.)
        else:
            area_val = pd.NA
        terrain_val = get_lowest_value(terrain_tokens) if terrain_tokens else pd.NA
        return pd.Series({"AREA": area_val, "TERRAIN": terrain_val})
    scalars = out["ALL AREA"].apply(compute_scalars)
    out.loc[:, "AREA"] = scalars["AREA"]
    out.loc[:, "TERRAIN"] = scalars["TERRAIN"]
    return out
#bool tag detect functions
"""
these are function that's to detect if a sequences (CLEANED TAG) col or (DATA TAG) contain a certain token.
return true or false in digit (0,1).
"""
def is_dispo(tags):
    # DISPONIBL MAINTEN: 1 if present, 0 if explicitly absent, <NA> if no tokens
    if not isinstance(tags, (set, tuple, list)) or len(tags) == 0:
        return pd.NA
    return 1 if any(PATTERN_DISPO_NOW.search(str(t)) for t in tags) else 0

def is_neuf(tags):
    # NEUF: 1 if present, 0 if explicitly absent, <NA> if no tokens
    if not isinstance(tags, (set, tuple, list)) or len(tags) == 0:
        return pd.NA
    return 1 if any(PATTERN_NEUF.search(str(t)) for t in tags) else 0

def has_chambr(tags):
    # CHAMBR: 1 if present, <NA> otherwise (to be averaged later, per your design)
    if not isinstance(tags, (set, tuple, list)) or len(tags) == 0:
        return pd.NA
    return 1 if any(PATTERN_CHAMBRE.search(str(t)) for t in tags) else pd.NA

def has_piece(tags):
    # PIEC: 1 if present, <NA> otherwise (to be averaged later)
    if not isinstance(tags, (set, tuple, list)) or len(tags) == 0:
        return pd.NA
    return 1 if any(PATTERN_PIECE.search(str(t)) for t in tags) else pd.NA

def has_floor(tags):
    # ETAG/RDC: 1 if present, 0 if explicitly absent, <NA> if no tokens
    if not isinstance(tags, (set, tuple, list)) or len(tags) == 0:
        return pd.NA
    return 1 if any(PATTERN_FLOOR.search(str(t)) for t in tags) else 0

#bool for floor extraction
def is_rdc(tag):
    if not tag :
        raise ValueError("No tag provided")
    if bool(PATTERN_RDC.search(tag)):
        return 1
    else : return 0
def is_etag(tag):
    if not tag :
        raise ValueError("No tag provided")
    if bool(PATTERN_ETAG.search(tag)):
        return 1
    else : return 0    
def has_slash(tag):
    if not tag:
        raise ValueError("No tag provided")
    if bool(PATTERN_SLASH.search(tag)):
        return 1
    else : return 0
def extract_additionals(df,col_seq="CLEANED TAG",col_tag="DATA TAG"):
    """
    extract all additional features: number of piece, number of chamber, number of floors, and which floor located,
    is it new ? is it dispo mtn ?
    - for floor feature (contains "ETAG" or "RDC" patterns) :
        + have couple type of format like RDC/(digit) or (digit)/(digit) or RDC alone,
        + here is how we treat them:
            + RDC/(digit) -> floor = 0 and floors = (digit)
            + RDC alone -> floor = 0 and floors = 0
            + (digit)/(digit) -> floor = first digit before the slash and floors = second digit after the slash

    and as usual, input a dataframe (this time there are parameters to indicate which cols to look for)
    and output new dataframe with new cols for extracted features.
    """
    #create masks
    mask_is_dispo = df[col_seq].apply(lambda x : is_dispo(list(x)) if isinstance(x,(tuple,list,set)) else pd.NA).fillna(0).astype(bool)
    mask_is_neuf = df[col_seq].apply(lambda x : is_neuf(list(x)) if isinstance(x,(tuple,list,set)) else pd.NA).fillna(0).astype(bool)
    mask_has_chambr = df[col_seq].apply(lambda x : has_chambr(list(x)) if isinstance(x,(tuple,list,set)) else pd.NA).fillna(0).astype(bool)
    mask_has_piece = df[col_seq].apply(lambda x : has_piece(list(x)) if isinstance(x,(tuple,list,set)) else pd.NA).fillna(0).astype(bool)
    mask_has_floor = df[col_seq].apply(lambda x : has_floor(list(x)) if isinstance(x,(tuple,list,set)) else pd.NA).fillna(0).astype(bool)
    #extract tags
    def get_chambr_tag(tags):
        if not tags :
            raise ValueError("Tags not provided")
        if not isinstance(tags,(set,list,tuple)):
            return pd.NA
        for t in tags :
            if bool(PATTERN_CHAMBRE.search(t)):
                return t
        return pd.NA
    def get_piece_tag(tags):
        if not tags :
            raise ValueError("Tags not provided")
        if not isinstance(tags,(set,list,tuple)):
            return pd.NA
        for t in tags :
            if bool(PATTERN_PIECE.search(t)):
                return t
        return pd.NA
    def get_floor_tag(tags):
        if not tags :
            raise ValueError("Tags not provided")
        if not isinstance(tags,(set,list,tuple)):
            return pd.NA
        for t in tags :
            if bool(PATTERN_FLOOR.search(t)):
                return t
        return pd.NA
    #get numerical values
    def get_floor(tag):
        if not tag :
            raise ValueError("No tag provided")
        nb_floor = PATTERN_BEFORE_SLASH.search(tag)
        if bool(nb_floor):
            return int(float(nb_floor.group(1)))
        else : return 0
    def get_floors(tag):
        if not tag :
            raise ValueError("No tag provided")
        nb_floors = PATTERN_AFTER_SLASH.search(tag)
        if bool(nb_floors):
            return int(float(nb_floors.group(1)))
        else : return 0
    def get_num(tag):
        tag = str(tag)
        if not tag :
            raise ValueError("tag not provided")
        num = PATTERN_NUM.search(tag)
        if bool(num):
            return int(num.group(0))
        else :
            return 0
    #this function to split something like 5/7 to floor = 5 and floors = 7
    def split_floor_tag(tag):
        if not tag or not bool(PATTERN_FLOOR.search(tag)):#verify (safety check) if tag is provided and there must be floor patterns in tag
            #floor patterns is ETAG or RDC
            raise ValueError("tag not provided or no floor pat in tag")
        #we need to distinguish if taf is rdc or etag, cuz rdc don't have same format as etag
        is_rdc_flag = bool(PATTERN_RDC.search(tag))
        has_slash   = bool(PATTERN_SLASH.search(tag))
        #default is floor = 0 and floors = 0
        floor, floors = 0, 0
        if is_rdc_flag:
            floor = 0 #as mentioned.
        if has_slash: #get digit before the slash and after the slash
            nb_floor  = PATTERN_BEFORE_SLASH.search(tag)
            nb_floors = PATTERN_AFTER_SLASH.search(tag)
            if not is_rdc_flag and nb_floor: #case of RDC/(digit) "and nb_floor" mean if the code find number
                floor = int(float(nb_floor.group(1)))
            if nb_floors:
                floors = int(float(nb_floors.group(1)))
            if not nb_floors:
                floors = floor
        else:
            if not is_rdc_flag:
                floor = int(get_num(tag)) or 0
            floors = floor
    
        return (floor, floors)
    """
    these codes are to identify and extract numerical data.
    """
    #bool extraction
    series_dispo = df[col_seq].apply(lambda x : is_dispo(x))
    series_neuf = df[col_seq].apply(lambda x : is_neuf(x))
    #unconditional extraction & pd.NA to be averaged
    #chambre
    series_chambr = df[col_seq].apply(lambda x : has_chambr(x))
    series_chambr.loc[series_chambr.notna()] = df.loc[mask_has_chambr,col_tag].apply(lambda x : get_chambr_tag(x))
    series_chambr.loc[series_chambr.notna()] = series_chambr.loc[series_chambr.notna()].apply(lambda x : int(get_num(x)) if x else pd.NA)
    is_valid_series_chambr = series_chambr.dropna().apply(lambda x : isinstance(x,int)).all()
    if not is_valid_series_chambr :
        raise ValueError("is_valid_series_chambr not valid")
    #piece
    series_piece = df[col_seq].apply(lambda x : has_piece(x))
    series_piece.loc[series_piece.notna()] = df.loc[mask_has_piece,col_tag].apply(lambda x : get_piece_tag(x))    
    series_piece.loc[series_piece.notna()] = series_piece.loc[series_piece.notna()].apply(lambda x : int(get_num(x)) if x else pd.NA)
    is_valid_series_piece = series_piece.dropna().apply(lambda x : isinstance(x,int)).all()
    if not is_valid_series_piece :
        raise ValueError("is_valid_series_piece not valid")
    #conditional extraction
    series_floor_tag = df[col_seq].apply(lambda x: has_floor(x))
    mask_floor_any = series_floor_tag.fillna(0).astype(bool)
    series_floor_tag.loc[mask_floor_any] = df.loc[mask_has_floor, col_tag].apply(lambda x: get_floor_tag(x) if x else pd.NA)
    series_floor_tag.loc[mask_floor_any] = series_floor_tag.loc[mask_floor_any].apply(lambda x: split_floor_tag(x) if isinstance(x, str) else (0, 0))
    idx = ~mask_floor_any
    series_floor_tag.loc[idx] = [(0, 0)] * int(idx.sum())
    # validate
    is_valid_series_floor = series_floor_tag.apply(lambda x: isinstance(x, tuple) and len(x) == 2).all()
    if not is_valid_series_floor :
        raise ValueError("is_valid_series_floor not valid")
    if len(series_floor_tag) == len(series_chambr) == len(series_piece) == len(series_dispo) == len(series_neuf) :
        out = df.copy(deep=True)
        out["DISPONIBL MAINTEN"] = series_dispo
        out["NEUF"] = series_neuf
        out["CHAMBRE"] = series_chambr
        out["PIECE"] = series_piece
        out[["FLOOR","FLOORS"]] = pd.DataFrame(series_floor_tag.tolist(), index=df.index)
        return out
    else : 
        raise ValueError("len don't match")#len -> size.
"""
- creating linear regression model to predict missing values for CHAMBR,PIECE based on AREA.
- why linear regression model ? 
    + cuz it's num or area is relative to chambre and piece for residential properties,
    meaning more area -> more pieces -> more chambres. (that's the relation this code assume)
    + we are not going to build the linear regression model from scratch because it's gonna take time
    ( i have more thing to do other then sticking my face to the screen all day. 
        + ps btw i only had less than 1 week to scrape data of seloger.com (got blocked couple times) and k-means applied model training.
        + k-means was built from scratch the week before.
- we have 3 models, one
"""
def round_int(arr):
    a = np.asarray(arr, dtype =float)#convert arr to np.array, and cast type to float
    return np.round(a).astype(int)#round and convert them to integer
def as_float(arr):
    return np.asarray(arr, dtype=float)#convert arr to np.array, and cast type to float
def make_model(x_cols, alpha=1.0):#just creating model from the lib i imported, to know details, search youtube, or on the website direct.
    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imp", SimpleImputer(strategy = "median")),#fill missing value with median (most appear value)
            ("sc", StandardScaler()),#standardize features, mean to rescale values by (value-mean)/standard_deviation, standardScaler is the name of the method to scale.
        ]), x_cols)
    ])
    return Pipeline([("pre", pre), ("reg", Ridge(alpha=alpha))])
#create + train models, LRM -> Linear Regression Model :)
def train_LRM(df, alpha_piece=1.0, alpha_ch_direct=1.0, alpha_ch_chain=1.0):#care only about input df, the rest are default settings.
    df = df.copy()
    for c in ["AREA", "PIECE", "CHAMBRE"]:
        df[c] = pd.to_numeric(df[c], errors ="coerce")
    #drop them just in case, most likely when we train the model, we dropped them before.
    df_piece = df.dropna(subset = ["PIECE"])
    df_ch_dir = df.dropna(subset = ["CHAMBRE"])
    df_ch_chain = df.dropna(subset = ["CHAMBRE", "PIECE"])
    #train models.
    m_piece_from_area = make_model(["AREA"], alpha = alpha_piece)
    m_piece_from_area.fit(df_piece[["AREA"]], df_piece["PIECE"])#to predict piece from area
    m_chambre_from_area = make_model(["AREA"], alpha = alpha_ch_direct)
    m_chambre_from_area.fit(df_ch_dir[["AREA"]], df_ch_dir["CHAMBRE"])#to predict chambre from area
    m_chambre_from_area_piece = make_model(["AREA", "PIECE"], alpha = alpha_ch_chain)#take area + piece to predict chambre
    m_chambre_from_area_piece.fit(df_ch_chain[["AREA", "PIECE"]], df_ch_chain["CHAMBRE"])
    #return models
    models = {
        "piece_from_area": m_piece_from_area,
        "chambre_from_area": m_chambre_from_area,
        "chambre_from_area_piece": m_chambre_from_area_piece,
    }
    return models
#create predicting funcs
def predict_A2P(x, models):
    try:
        X_area = pd.DataFrame([{"AREA": float(x)}])
        pred = float(models["piece_from_area"].predict(X_area)[0])
        return int(round(max(1.0, pred)))
    except Exception as e:
        raise ValueError(f"Error predicting AREA to PIECE: {e}")
def predict_A2C(x, models):
    try:
        X_area = pd.DataFrame([{"AREA": float(x)}])
        pred = float(models["chambre_from_area"].predict(X_area)[0])
        return int(round(max(0.0, pred)))
    except Exception as e:
        raise ValueError(f"Error predicting AREA to CHAMBRE: {e}")
def predict_AP2C(area, piece, models):
    try:
        X_ap = pd.DataFrame([{"AREA": float(area), "PIECE": float(piece)}])
        pred = float(models["chambre_from_area_piece"].predict(X_ap)[0])
        pred = max(0.0, min(float(piece), pred))  # 0 ≤ CHAMBRE ≤ PIECE
        return pred
    except Exception as e:
        raise ValueError(f"Error predicting (AREA,PIECE) to CHAMBRE: {e}")
def lin_predict_features(df, models):
    out = df.copy(deep=True)
    #create masks
    mask_both_missing = (out["PIECE"].isna() & out["CHAMBRE"].isna())
    mask_piece_missing = (out["PIECE"].isna() & out["CHAMBRE"].notna())
    mask_chambre_missing = (out["CHAMBRE"].isna() & out["PIECE"].notna())
    #bool for any missing chambre
    if mask_chambre_missing.any():
        X_AP = out.loc[mask_chambre_missing, ["AREA", "PIECE"]].astype(float)
        y_hat = models["chambre_from_area_piece"].predict(X_AP).astype(float)
        #clip and round
        y_hat = np.maximum(0.0, np.minimum(X_AP["PIECE"].to_numpy(), y_hat))
        out.loc[mask_chambre_missing, "CHAMBRE"] = np.round(y_hat).astype(int)
    #cbool for any both chambre and piece missing
    if mask_both_missing.any():
        #get area vals for rows miss both n convert to float (area is already float type) and convert 1D series to 2D dataframe
        area_vals = out.loc[mask_both_missing, "AREA"].astype(float).to_frame()
        #get prediction
        p_hat = models["piece_from_area"].predict(area_vals).astype(float)
        p_hat = np.maximum(1.0, p_hat)
        p_hat_round = np.round(p_hat).astype(int)
        out.loc[mask_both_missing, "PIECE"] = p_hat_round
        # chambre_hat with chained model
        X_for_ch = pd.DataFrame({
            "AREA": area_vals["AREA"].values,
            "PIECE": p_hat  # use float p_hat inside model
        })
        c_hat = models["chambre_from_area_piece"].predict(X_for_ch).astype(float)
        c_hat = np.maximum(0.0, np.minimum(p_hat, c_hat))
        out.loc[mask_both_missing, "CHAMBRE"] = np.round(c_hat).astype(int)
    # 3) PIECE missing but CHAMBRE present simply : PIECE = CHAMBRE + 1
    if mask_piece_missing.any():
        out.loc[mask_piece_missing, "PIECE"] = (out.loc[mask_piece_missing, "CHAMBRE"].astype(float) + 1).astype(int)
    return out
def vectorize_dataset_seloger(csv_file : str = None, save : bool = False, fname : str = "Untitled"):
    if not csv_file :
        raise ValueError("Require dataset filepath")
    #vopen file
    try :
        raw_df = pd.read_csv(csv_file)
    except Exception :
        raise ValueError("Error converting file.csv to dataframe")
    raw_df_cols = raw_df.columns.tolist()
    #verify columns
    if raw_df_cols != ['href', 'title']:
        raise ValueError(f"Unexpected columns {raw_df_cols}")

    
    #1 extract price,unit-price,data-tags -------------------------------
    out_df = get_processed(raw_df["title"]) 
    #2 clean tags (remove numbers, normalize them)
    out_df = out_df.loc[out_df["DATA TAG"].notna()]
    out_df["CLEANED TAG"] = out_df["DATA TAG"].apply(
        lambda x : normalize_tags(x) if isinstance(x,(tuple,list,set)) else pd.NA
    )
    out_df = out_df.loc[out_df["CLEANED TAG"].notna()]
    #3 extract type
    out_df["TYPE"] = out_df["CLEANED TAG"].apply(
        lambda x : extract_type(x) if isinstance(x,(tuple,list,set)) else pd.NA
    )
    out_df = out_df.loc[out_df["TYPE"].notna()]

    #4 extract location(postcode)
    out_df = extract_loc(df=out_df,dict_map=STEM_TO_POSTCODES)
    out_df = out_df.loc[out_df["LOC"].notna()]
    if out_df["LOC"].apply(lambda x : len(x) == 1 if isinstance(x,(set)) else False).any():
        out_df["LOC"] = out_df["LOC"].apply(lambda x : next(iter(x)))
    else :
        raise ValueError("Multiple location in one row detected.")
    #5 extract area,terrain
    out_df = extract_area(out_df)
    out_df = out_df.loc[~(out_df["AREA"].isna() & out_df["TERRAIN"].isna())]
    out_df.loc[out_df["TERRAIN"].isna(),"TERRAIN"] = 0
    out_df.loc[out_df["AREA"].isna(),"AREA"] = 0
    out_df["AREA"] = out_df["AREA"].astype(float)
    out_df["TERRAIN"] = out_df["TERRAIN"].astype(float)
    #6 extract feature
    out_df = extract_additionals(out_df)
    out_df["FLOOR"] = out_df["FLOOR"].astype(int)
    out_df["FLOORS"] = out_df["FLOORS"].astype(int)
    #7 fill missing values for chambre and piece, use linear regression model
    models = train_LRM(out_df.dropna())
    out_df = lin_predict_features(df=out_df,models=models)
    out_df["CHAMBRE"] = out_df["CHAMBRE"].astype(int)
    out_df["PIECE"] = out_df["PIECE"].astype(int)
    out_df.loc[out_df["TYPE"] == "TERRAIN CONSTRUCTIBL A VENDR" ,["PIECE","CHAMBRE","FLOOR","FLOORS"]] =0
    if save :
        out_df.to_csv(f"{fname}.csv",index = False)
    return out_df

