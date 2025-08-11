import openai
import os
from colorama import Fore, Style, init
from dotenv import load_dotenv

load_dotenv()
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

#inicianlizando colorama
init(autoreset=True)

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1000,
        stream=True
    )
    print(f"{Fore.CYAN}Bot: ", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end="")
            texto_completo += texto
    print()
    mensagens.append({"role": "assistant", "content": texto_completo})
    return mensagens

if __name__ == "__main__":
    print(f"{Fore.YELLOW}Bem vindo ao ChatBot 🤖")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN}User: {Style.RESET_ALL}")
        mensagens.append({"role":"user", "content": in_user})
        mensagens = geracao_texto(mensagens) 