from flask import Flask, render_template, request, redirect
import json
from pathlib import Path
from importlib.resources import files

FILE_PIANTE = files(__package__) / "piante.txt"
FILE_DATI = files(__package__) / "dati.json"

MAX_DATI = 20
MAX_RIGHE_FILE = 144 * 30  # 144 il numero di letture al giorno * 30 giorni di dati


def create_app(test_config=None):
    app = Flask(__name__)

    # -----------------------------------------------------------------------
    @app.route("/")
    def home():
        return render_template("home.html")

    # -----------------------------------------------------------------------
    @app.route("/dati")
    def dati():
        rows = []
        if Path(FILE_DATI).exists():
            file = open(FILE_DATI,"r")
            for riga in file:
                diz = json.loads(riga.strip())
                rows.append(diz)
            file.close()
        return render_template("dati.html", rows=rows)

    # -----------------------------------------------------------------------
    @app.route("/data", methods=["POST"])
    def gestisci_dati():
        if not request.is_json:
            return "ERRORE!!!!"

        payload = request.get_json()
        file = open(FILE_DATI,"a")
        file.write( json.dumps(payload) +"\n")
        file.close()

        return "Consegnato!!!"

    # -----------------------------------------------------------------------
    @app.route("/piante")
    def piante():
        lista = []
        file = open(FILE_PIANTE,"r")
        for riga in file:
            pianta,link = riga.strip().split("$")
            lista.append( pianta )
        file.close()
        return render_template("piante.html",lista_piante_disponibili = lista)

    # ---------------------------------------------------------------------
    @app.route("/pianta/<nomePianta>")
    def pianta(nomePianta):
        dizPianteDisponibili = {}
        file = open(FILE_PIANTE,"r")
        for riga in file:
            pianta,link = riga.strip().split("$")
            dizPianteDisponibili[pianta] = link
        file.close()

        if nomePianta not in dizPianteDisponibili:
            # TODO messaggio di errore
            return redirect("/piante")

        link = dizPianteDisponibili[nomePianta]
        return render_template("pianta.html", titolo = nomePianta, link = link)

    # ---------------------------------------------------------------------
    @app.route("/statistiche")
    def statistiche():
        rows = []
        file = open(FILE_DATI,"r")
        for riga in file:
            diz = json.loads(riga.strip())
            rows.append(diz)
        file.close()
        return render_template("statistiche.html", dati = rows[-MAX_DATI:])

    #---------------------------------------------------------------------
    @app.route("/reset")
    def cancellaFile():
        file = open(FILE_DATI,"w")
        file.close()
        return redirect("/")

    #----------------------------------------------------------------------
    @app.route("/about")
    def about():
        return render_template("about.html")


    # closing the create_app app!!!
    return app

# RUN ========================================================================================

# if __name__ == '__main__':
#    app = create_app()
#    app.run(debug=True)
