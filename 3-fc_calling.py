import json 
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv()
client = OpenAI()

# Funçao para calcular IMC e fornecer recomendação

def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    if imc < 18.5:
        estado = "abaixo do peso"
        recomendado = "É importante que você consulte um médico para ajustar sua alimentação"
    elif 18.5 <= imc < 24.9:
        estado = "com peso normal"
        recomendado = "Continue mantendo uma alimentação equilibrada e praticando exercícios regularmente"
    elif 25 <= imc < 29.9:
        estado = "com sobrepeso"
        recomendado = "É aconselhável que você consulte um nutricionista para ajustar sua dieta"
    else:
        estado = "obeso"
        recomendado = "É fundamental que você busque orientação médica para um plano de emagrecimento saudável"
    
    return json.dumps({
        "imc": imc,
        "estado": estado,
        "recomendado": recomendado
    })
tools = [
    { 
        "type": "function",
        "function": {
            "name": "calcular_imc",
            "description": "Calcula o IMC e fornece recomendações baseadas no resultado",
            "parameters": {
                "type": "object",
                "properties": {
                    "peso": {
                        "type": "number",
                        "description": "Peso em kg"
                    },
                    "altura": {
                        "type": "number",
                        "description": "Altura em metros"
                    }
                },
                "required": ["peso", "altura"]
            }
        },
    } 
]

funcoes_disponiveis = {
    "calcular_imc": calcular_imc,
}
mensagens = [
    {"role": "user", "content": "Qual é o IMC de uma pessoa que pesa 70 kg e tem 1.75 m de altura?"}
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=mensagens,
    tools=tools,
    tool_choice="auto",
)

mensagem_resposta = response.choices[0].message
tool_calls = mensagem_resposta.tool_calls

if tool_calls:
    mensagens.append(mensagem_resposta)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = funcoes_disponiveis[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            peso=function_args.get("peso"),
            altura=function_args.get("altura")
        )

        mensagens.append(
            {
                "tool_call_id": tool_call.id,
                "role":"tool",
                "name": function_name,
                "content": function_response
            }
        )



    segunda_resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,
    )
    mensagem_final = segunda_resposta.choices[0].message
else:
    mensagem_final = mensagem_resposta

print(mensagem_final.content)