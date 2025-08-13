import yfinance as yf
from openai import OpenAI
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv()
client = OpenAI()

def retorna_cotacao(ticker, periodo="1mo"):
    ticker_obj = yf.Ticker(f"{ticker}.SA")
    hist = ticker_obj.history(period=periodo)["Close"]
    hist.index = hist.index.strftime ("%Y-%m-%d")
    hist = round(hist,2)
    #limitar em 30 resultados messclados

    if len(hist)>30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]
    return hist.to_json()

tools = [
    {
        "type":"function",
        "function":{
            "name": "retorna_cotacao",
            "description":"Retorna cotacoes da Ibovespa",
            "parameters":{
                "type": "object",
                "properties":{
                    "ticker":{
                        "type":"string",
                        "description": "O ticker da ação: BBAS3, BBDC4, etc"
                    },
                    "periodo":{
                        "type":"string",
                        "description":"Periodo retornado dos dados historicos da cotação \
                            sendo '1mo' equivale a um mes, '1d' equivale a um dia \
                                e '1y' equivale a um ano e 'ytd' equivale a todos os tempos",
                        "enum":["1d", "5d", "1mo", "6mo","1y","5y","10y","ytd", "max"]
                    }
                }
            }
        }
    }
]

funcao_disponivel = {"retorna_cotacao":retorna_cotacao}
mensagens = [{"role": "user", "content":"Qual é a cotação do Banco do Brasil no ultimo ano?"}]


resposta = client.chat.completions.create(
    messages=mensagens,
    model="gpt-4o-mini",
    tools=tools,
    tool_choice="auto"
)

mensagem_resposta = resposta.choices[0].message
tool_calls = mensagem_resposta.tool_calls

if tool_calls:
    mensagens.append(mensagem_resposta)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = funcao_disponivel[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_return = function_to_call(**function_args)

        mensagens.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_return,
        })

    segunda_resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,
    )
    mensagens.append(segunda_resposta.choices[0])
    print(segunda_resposta.choices[0].message.content)

