import json


def main():
    data = {}
    data["Entreprise"] = ["Entreprise_general", "Voyages", "Salons"]
    data["Laboratoire"] = ["Laboratoire_general", "Conferences", "Redaction thèse"]
    data["Autres"] = ["Autre_general", "Lectures personelles"]
    with open("categories_new.config", "w") as input_file:
        input_file.write(json.dumps(data))



if __name__ == '__main__':
    main()

