import pandas as pd
import mysql.connector
import unicodedata

def clean_df(df):
    new_cols = {} #dictionary
    for col in df.columns:
        cleaned = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8').strip().replace(" ", "_")
        new_cols[col] = cleaned
    df.rename(columns = new_cols, inplace=True)
    #print(new_cols)
    for col in df.columns:
        df[col] = df[col].apply(lambda x: unicodedata.normalize('NFKD', str(x)).encode('ASCII', 'ignore').decode('utf-8').strip() if isinstance(x, str) else x)


def categorize_df(df, column):
    separated_df = {} 
    for key in df[column].unique():
        separated_df[key] = df.loc[df[column] == key]
    return separated_df  

def connect_mysql() :
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database= "sprintData_decathlon"
    )
    return conn


#print(df_produits)
def create_database(df, table_name): 
    conn = connect_mysql()
    stmt = conn.cursor()
    # Corrected table creation with f-string
    stmt.execute(f'''
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        nom TEXT,
        marque TEXT,
        prix REAL,
        lien TEXT,
        description TEXT,
        avis REAL,
        nombre_avis INTEGER,
        couleurs_disponibles TEXT,
        disponibilite TEXT,
        image TEXT
    )
    ''')

    for _, row in df.iterrows():
        stmt.execute(f'''
            INSERT INTO `{table_name}` (nom, marque, prix, lien, description, avis, nombre_avis, couleurs_disponibles, disponibilite, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row.get('Nom', None),
            row.get('Marque', None),
            float(row['Prix']) if isinstance(row['Prix'], (int, float, str)) and row['Prix'] != "Non disponible" else None,
            row.get('Lien', None),
            row.get('Description', None),
            float(row['Avis']) if isinstance(row['Avis'], (int, float, str)) and row['Avis'] != "Non disponible" else None,
            int(row["Nombre_d'avis"]) if isinstance(row["Nombre_d'avis"], (int, float, str)) and row["Nombre_d'avis"] != "Non disponible" else None,
            row.get('Couleurs_Disponibles', None),
            row.get('Disponibilite', None),
            row.get('Image', None)
        ))

    conn.commit()
    stmt.close() 
    conn.close()


df_produits = pd.read_csv("decathlon_produits_details.csv")
df_produits_parMarque = categorize_df(df_produits, "Marque")
clean_df(df_produits)
create_database(df_produits,"produits")
for brand, df in df_produits_parMarque.items():
    clean_df(df)
    create_database(df, f"produits_{brand}")