import requests
from bs4 import BeautifulSoup
import csv
import psycopg2

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

page = requests.get('https://www.inam.tg/remboursement-produits-pharmaceutiques/', headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')

modals = soup.find_all(class_="modal")
medicaments = []
i=1
for modal in modals:
    medicament = {}
    medicament['id'] = i

    # récupération du nom du médicament et du dosage
    ligne_dosage = modal.select('.row:nth-child(0n+2)')
    dosage_raw_text = ligne_dosage[0].find(class_='col-md-6').find('p').text.replace('Dosage: ', '')
    medicament_raw_name = modal.find(class_="modal-header").text.replace('x', '').replace('\n', '')[:-1]
    medicament['nom'] = medicament_raw_name.strip('x').replace('"', '') + ' ' + dosage_raw_text.replace('"', '')
    medicament['dosage'] = dosage_raw_text.replace('"', '')

    # groupe thérapeutique du médicament

    ligne_groupe_therapeutique = modal.select('.row:nth-child(0n+3)')
    groupe_therapeutique_raw_text = ligne_groupe_therapeutique[0].find(class_='col-md-6').find('p').text.replace('Groupe Therapeutique: ', '')
    medicament['therapie'] = groupe_therapeutique_raw_text

    # forme du médicament
    ligne_forme = modal.select('.row:nth-child(0n+4)')
    forme_raw_text = ligne_forme[0].find_all(class_='col-md-6')[1].find('p').text.replace('Forme: ', '')
    medicament['forme'] = forme_raw_text

    # prix du médicament
    ligne_prix = modal.select('.row:nth-child(0n+5)')
    prix_raw_text = ligne_prix[0].find_all(class_='col-md-6')[1].find('span', class_='badge').text.replace(' FCFA', '')
    medicament['prix'] = float(prix_raw_text)

    # quantitée dans l'emballage
    ligne_qte = modal.select('.row:nth-child(0n+1)')
    qte_raw_text = ligne_qte[0].find_all(class_='col-md-6')[0].find('p').text.replace('Quantité: ', '')
    medicament['quantite'] = qte_raw_text

    # prix de base de remboursement inam
    ligne_prix_inam = modal.select('.row:nth-child(0n+6)')
    prix_inam_raw_text = ligne_prix_inam[0].find_all(class_='col-md-6')[0].find('p').text.replace('Base Remboursement: ', '')
    medicament['prix_inam'] = float(prix_inam_raw_text)
    medicaments.append(medicament)
    i += 1
print('données récupérées')


# enregistrement des données dans un fixhier csv
csv_file = open('drugs_csv.csv', 'w', encoding='utf-8', newline='')
writer = csv.writer(csv_file)

writer.writerow(['id', 'nom', 'dosage', 'therapie', 'forme', 'prix', 'quantite', 'prix_inam'])
for medicament in medicaments:
     writer.writerow(medicament.values())

csv_file.close()



# enregistrement des données dans une base postgreSQL


j=1
total= len(medicaments)
conn = psycopg2.connect(database="xxxxxxx", user="xxxxxxx", password="xxxxxx", host="xxxxxxxxx", port="5432")
cur = conn.cursor()
for medicament in medicaments:
    j += 1
    cur.execute('insert into drugs (name, price, price_inam, shape, quantity, dosage, therapy) values (%(name)s, %(price)s, %(price_inam)s, %(shape)s, %(quantity)s, %(dosage)s, %(therapy)s)',{'name': medicament['nom'],'price': medicament['prix'], 'price_inam': medicament['prix_inam'], 'shape': medicament['forme'], 'quantity': medicament['quantite'], 'dosage': medicament['dosage'], 'therapy': medicament['therapie']} )
    pourcentage = (j/total) * 100
    print('pourcentage: ' + str(round(pourcentage, 2)) + '%')

conn.commit()
cur.close()
conn.close()
