from flask import Flask, render_template_string
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

def consultar_leiloes():
    data_leilao = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d %m %Y")
    url = f"https://apiapex.tesouro.gov.br/aria/v1/api-leiloes-pub/custom/portarias?data_leilao={data_leilao}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    registros = data['registros']
    tipo_dia = "terça" if datetime.now(pytz.timezone('America/Sao_Paulo')).weekday() == 1 else "quinta"
    titulos = {'LTN': [], 'NTN-F': [], 'NTN-B': [], 'LFT': []}
    for registro in registros:
        tipo_titulo = registro['TITULO']
        titulos[tipo_titulo].append(registro)
    if tipo_dia == "terça":
        ordem_titulos = ['NTN-B', 'LFT']
    else:  # Quinta-feira
        ordem_titulos = ['LTN', 'NTN-F']
    resultado = []
    for tipo in ordem_titulos:
        registros_tipo = titulos[tipo]
        if registros_tipo:
            resultado.append(f"------ {tipo} ------")
            for registro in registros_tipo:
                oferta = registro['OFERTA']
                titulo = registro['TITULO']
                data_leilao = registro['DATA_LEILAO']
                vencimento = registro['VENCIMENTO']
                oferta_formatada = "{:,.2f}".format(oferta).replace(',', '.')
                resultado.append(f"Título: {titulo}")
                resultado.append(f"Oferta: {oferta_formatada}")
                resultado.append(f"Data do leilão: {data_leilao}")
                resultado.append(f"Vencimento: {vencimento}")
                resultado.append("")
    return resultado

@app.route('/')
def index():
    try:
        resultado = consultar_leiloes()
        return render_template_string("""
            <!doctype html>
            <html lang="pt-br">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <title>Leilões do Tesouro Nacional</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f5;
                        color: #333;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1 {
                        color: #007bff;
                    }
                    pre {
                        background-color: #e9ecef;
                        padding: 15px;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="mt-5">Leilões do Tesouro Nacional</h1>
                    <pre>{{ resultado }}</pre>
                </div>
            </body>
            </html>
        """, resultado="\n".join(resultado))
    except Exception as e:
        return f"Erro ao consultar leilões: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
