"""
Script de Teste Rápido - Verifica se tudo está configurado
"""

import os
import sys
from dotenv import load_dotenv

def test_configuration():
    """Testa configuração do bot"""
    
    print("="*60)
    print("🔍 TESTE DE CONFIGURAÇÃO - BIANCA BOT")
    print("="*60)
    print()
    
    # Carrega .env
    load_dotenv()
    
    # Testa imports
    print("📦 Testando imports...")
    try:
        import telegram
        print("✅ python-telegram-bot instalado")
    except ImportError:
        print("❌ python-telegram-bot NÃO instalado")
        print("   Execute: pip install python-telegram-bot")
        return False
    
    try:
        import anthropic
        print("✅ anthropic instalado")
    except ImportError:
        print("❌ anthropic NÃO instalado")
        print("   Execute: pip install anthropic")
        return False
    
    print()
    
    # Testa variáveis de ambiente
    print("🔑 Testando credenciais...")
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token and telegram_token != "seu_token_aqui":
        print(f"✅ TELEGRAM_TOKEN configurado ({telegram_token[:10]}...)")
    else:
        print("❌ TELEGRAM_TOKEN NÃO configurado")
        print("   Edite o arquivo .env")
        return False
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "sua_chave_api_aqui":
        print(f"✅ ANTHROPIC_API_KEY configurada ({anthropic_key[:15]}...)")
    else:
        print("❌ ANTHROPIC_API_KEY NÃO configurada")
        print("   Edite o arquivo .env")
        return False
    
    print()
    
    # Testa arquivos
    print("📁 Testando arquivos...")
    required_files = [
        "main.py",
        "bianca_bot.py",
        "config.py",
        "reengagement.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} NÃO encontrado")
            return False
    
    print()
    
    # Testa conexão com Telegram (opcional)
    print("🤖 Testando conexão com Telegram...")
    try:
        from telegram import Bot
        bot = Bot(token=telegram_token)
        bot_info = bot.get_me()
        print(f"✅ Conectado com @{bot_info.username}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    print()
    
    # Testa API Anthropic (opcional)
    print("🧠 Testando API Anthropic...")
    try:
        client = anthropic.Anthropic(api_key=anthropic_key)
        # Teste simples
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "oi"}]
        )
        print("✅ API Anthropic funcionando")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
        print("   Verifique créditos ou chave API")
    
    print()
    print("="*60)
    print("✅ TUDO CONFIGURADO! Você pode executar:")
    print("   python main.py")
    print("="*60)
    
    return True


if __name__ == "__main__":
    if not test_configuration():
        sys.exit(1)
