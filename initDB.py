from main import db, Pokemon, app
import csv

#intitialze the database
db.create_all(app=app)

# add code to parse csv, create and save pokemon objects
# replace any null values with None to avoid db errors

with open("pokemon.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for line in csv_reader:
        pokemon = Pokemon(pid=line['pokedex_number'], name=line['name'], attack=line['attack'], defense=line['defense'], hp=line['hp'], height=line['height_m'], sp_attack=line['sp_attack'], sp_defense=line['sp_defense'], speed=line['speed'], type1=line['type1'], type2=line['type2'], weight=line['weight_kg'])

        if pokemon.pid == "":
            pokemon.pid = None
        if pokemon.name == "":
            pokemon.name = None
        if pokemon.attack == "":
            pokemon.attack = None
        if pokemon.defense == "":
            pokemon.defense = None
        if pokemon.hp == "":
            pokemon.hp = None
        if pokemon.height == "":
            pokemon.height = None
        if pokemon.sp_attack == "":
            pokemon.sp_attack = None
        if pokemon.sp_defense == "":
            pokemon.sp_defense = None
        if pokemon.speed == "":
            pokemon.speed = None
        if pokemon.type1 == "":
            pokemon.type1 = None
        if pokemon.type2 == "":
            pokemon.type2 = None
        if pokemon.weight == "":
            pokemon.weight = None

        db.session.add(pokemon)
        db.session.commit()
