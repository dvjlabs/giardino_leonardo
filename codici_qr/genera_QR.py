import qrcode

file = open("piante.txt","r")


for riga in file:
    nome,sito = riga.split("$")
    url = f"https://giardino.dvjlabs.org/pianta/{nome}"
    img = qrcode.make(url)
    img.save(f"{nome}.png")
    
file.close()