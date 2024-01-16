import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.backends.backend_pdf import PdfPages

def chargement_schedule(csv_file):
    df = pd.read_csv(csv_file, parse_dates=['Début', 'Fin'])
    df['Début'] = df['Début'].dt.tz_localize(None)
    df['Fin'] = df['Fin'].dt.tz_localize(None)
    return df

def emplacements_disponibles(schedule, start_date, group):
    groupe_schedule = schedule[schedule['Description'].str.contains(group, case=False, na=False)]
    start_date = pd.to_datetime(start_date).tz_localize(None)
    horaire_modifie = groupe_schedule[groupe_schedule['Début'] >= start_date]

    emplacements_disponibles = []
    date_actuelle = start_date

    while len(emplacements_disponibles) < 5:
        if date_actuelle.weekday() in [5, 6]:  # Samedi et Dimanche
            date_actuelle += timedelta(days=1)
            continue
        if date_actuelle.weekday() == 3 and date_actuelle.hour >= 12:  # Jeudi après-midi
            date_actuelle += timedelta(days=1)
            continue
        if 8 <= date_actuelle.hour < 16:  # Entre 8h et 18h
            end_of_slot = date_actuelle + timedelta(hours=2)
            if horaire_modifie[(horaire_modifie['Début'] < end_of_slot) & (horaire_modifie['Fin'] > date_actuelle)].empty:
                emplacements_disponibles.append((date_actuelle, end_of_slot))

        date_actuelle += timedelta(hours=1)
        if date_actuelle.hour >= 18:
            date_actuelle = date_actuelle.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)

    return emplacements_disponibles

if __name__ == "__main__":
    csv_file = "/media/mg397494/CNED/SAÉ 15 - Traitement des données/Git/!Projet n9/Final/ADECal.csv"  # Remplacez par le chemin réel du fichier CSV
    schedule = chargement_schedule(csv_file)

    start_date_str = input("Veuillez entrer la date de début au format YYYY-MM-JJ : ")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=None)
    group = input("Veuillez entrer le groupe d'étudiants : ")

    creneaux = emplacements_disponibles(schedule, start_date, group)

    print("Créneaux disponibles :")
    for i, creneaux in enumerate(creneaux, start=1):
        print(f"{i}. Début : {creneaux[0]}, Fin : {creneaux[1]}")

    # Création de la frise chronologique
    fig, ax = plt.subplots()
    for i, creneaux in enumerate(creneaux, start=1):
        # Convertir les objets Timestamp en format matplotlib
        start_matplotlib = mdates.date2num(creneaux[0])
        end_matplotlib = mdates.date2num(creneaux[1])
        ax.plot([start_matplotlib, end_matplotlib], [i, i], marker='o', linestyle='-', color='b')
        ax.annotate(f"Créneau {i}\n{creneaux[0].strftime('%H:%M')} - {creneaux[1].strftime('%H:%M')}",
                    (start_matplotlib, i), textcoords="offset points", xytext=(0,10), ha='center')

    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))  # Graduation de 1 en 1 sur l'axe des données

    plt.title('Timeline des Créneaux Disponibles pour le Groupe ' + group)
    plt.xlabel('Dates')
    plt.ylabel('Créneaux')

    fig.autofmt_xdate()
    plt.tight_layout()

    # Enregistrement de la frise chronologique sous forme de fichier PNG
    plt.savefig('Diagramme.png', format='png')
    
    # Sauvegarde des créneaux disponibles dans un fichier PDF
    creneaux_df = pd.DataFrame(creneaux, columns=['Début', 'Fin'])
    pdf_filename = 'creneaux_disponibles.pdf'
    pdf_pages = PdfPages(pdf_filename)
    
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    table_data = [list(map(str, row)) for row in creneaux_df.values]
    table = ax.table(cellText=table_data, colLabels=['Début', 'Fin'], cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1])
    
    pdf_pages.savefig(fig, bbox_inches='tight')
    pdf_pages.close()
    
    plt.show()
