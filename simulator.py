"""
Simulador de Conversa com Bianca
Permite testar as respostas da IA sem usar o Telegram
"""

import os
from dotenv import load_dotenv
import anthropic
from config import PERSONA_PROMPT
from datetime import datetime

load_dotenv()

class BiancaSimulator:
    """Simula conversas com Bianca"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada no .env")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []
    
    def _get_periodo_dia(self):
        """Retorna período do dia"""
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return "manhã", "Início do dia, energia renovada"
        elif 12 <= hora < 18:
            return "tarde", "Metade do dia, momento de pausa"
        elif 18 <= hora < 23:
            return "noite", "Fim do dia, hora de relaxar"
        else:
            return "madrugada", "Horas silenciosas, momento íntimo"
    
    def _build_system_prompt(self, is_premium=False):
        """Constrói prompt do sistema"""
        periodo, contexto = self._get_periodo_dia()
        status = "Premium ✨" if is_premium else "Grátis (5/10 msgs)"
        
        return PERSONA_PROMPT.format(
            periodo=periodo,
            contexto_horario=contexto,
            status_usuario=status
        )
    
    def send_message(self, user_message: str, is_premium: bool = False) -> str:
        """Envia mensagem e recebe resposta"""
        
        # Adiciona mensagem do usuário ao histórico
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Mantém apenas últimas 10 mensagens
        messages = self.conversation_history[-10:]
        
        try:
            # Chama API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                system=self._build_system_prompt(is_premium),
                messages=messages
            )
            
            ai_response = response.content[0].text
            
            # Adiciona resposta ao histórico
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            return f"Erro: {e}"
    
    def reset(self):
        """Reseta a conversa"""
        self.conversation_history = []
        print("💫 Conversa resetada\n")


def main():
    """Interface de linha de comando"""
    
    print("="*60)
    print("🌙 SIMULADOR DE CONVERSA COM BIANCA")
    print("="*60)
    print()
    print("Comandos especiais:")
    print("  /reset    - Reinicia conversa")
    print("  /premium  - Alterna status premium")
    print("  /sair     - Sai do simulador")
    print()
    print("="*60)
    print()
    
    simulator = BiancaSimulator()
    is_premium = False
    
    # Mensagem inicial
    print("🌙 Bianca: Olá, estranho... Interessante você me encontrar aqui.")
    print()
    
    while True:
        # Input do usuário
        try:
            user_input = input("💬 Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Até logo!")
            break
        
        if not user_input:
            continue
        
        # Comandos especiais
        if user_input.lower() == "/sair":
            print("\n👋 Até logo!")
            break
        
        elif user_input.lower() == "/reset":
            simulator.reset()
            continue
        
        elif user_input.lower() == "/premium":
            is_premium = not is_premium
            status = "✨ PREMIUM ATIVADO" if is_premium else "⚠️ MODO GRÁTIS"
            print(f"\n{status}\n")
            continue
        
        # Envia mensagem
        print()
        print("⏳ Bianca está digitando...")
        
        response = simulator.send_message(user_input, is_premium)
        
        print(f"🌙 Bianca: {response}")
        print()


if __name__ == "__main__":
    main()
