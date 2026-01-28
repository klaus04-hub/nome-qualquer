"""
Bianca Bot - Versão com Variáveis de Ambiente
Uso: python main.py
"""

import os
from dotenv import load_dotenv
from bianca_bot import BiancaBot

# Carrega variáveis de ambiente
load_dotenv()

def main():
    """Função principal"""
    
    # Obtém credenciais
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Validação
    if not telegram_token:
        print("❌ ERRO: TELEGRAM_TOKEN não configurado!")
        print("Configure suas credenciais no arquivo .env")
        return
    
    if not anthropic_key:
        print("❌ ERRO: ANTHROPIC_API_KEY não configurada!")
        print("Configure suas credenciais no arquivo .env")
        return
    
    # Inicia o bot
    print("="*50)
    print("🌙 BIANCA BOT - TELEGRAM + IA")
    print("="*50)
    print()
    
    bot = BiancaBot(telegram_token, anthropic_key)
    bot.run()


if __name__ == "__main__":
    main()
