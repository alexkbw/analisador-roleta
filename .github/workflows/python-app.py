#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roleta Simples - Versão unificada e simplificada
Captura 5 últimos números, detecta mudança de estado e envia para API
"""

import requests
import time
import logging
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RoletaSimples:
    def __init__(self):
        self.driver = None
        self.api_url = "https://xyzdyurjrixzhtrgxkzv.supabase.co/functions/v1/receive-number/"
        self.ultimo_estado = None
        self.total_enviados = 0
        
    def iniciar_navegador(self):
        """Iniciar o navegador e acessar o site"""
        try:
            logging.info("Iniciando navegador...")
            
            self.driver = Driver(uc=True, headless=False, browser="chrome", incognito=False)
            self.driver.get("https://www.888casino.com/live-casino/#filters=live-roulette")
            
            logging.info("Aguardando carregamento...")
            time.sleep(15)
            
            # Aceitar cookies se aparecer
            try:
                botao = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                botao.click()
                logging.info("Cookies aceitos")
            except:
                pass
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao iniciar navegador: {e}")
            return False
    
    def capturar_ultimos_5(self):
        """Capturar os 5 últimos números da roleta usando seletores corretos"""
        try:
            # Script baseado na estrutura real do site conforme mudanca.md
            script = """
            var results = [];
            
            // Buscar especificamente pelos números da roleta conforme estrutura do site
            // Seletor para o jogo de roleta ID 2380064
            var roletaContainer = document.querySelector('.cy-live-casino-grid-item-2380064');
            
            if (roletaContainer) {
                // Buscar pelos números nos draws (cy-live-casino-grid-item-infobar-draws)
                var drawsContainer = roletaContainer.querySelector('.cy-live-casino-grid-item-infobar-draws');
                
                if (drawsContainer) {
                    var numeroSpans = drawsContainer.querySelectorAll('span');
                    
                    for (var i = 0; i < numeroSpans.length; i++) {
                        var texto = numeroSpans[i].textContent.trim();
                        var numero = parseInt(texto);
                        
                        if (!isNaN(numero) && numero >= 0 && numero <= 36) {
                            results.push(numero.toString());
                        }
                    }
                }
            }
            
            // Se não encontrou com o ID específico, tentar seletores mais gerais
            if (results.length === 0) {
                var todosDraws = document.querySelectorAll('.cy-live-casino-grid-item-infobar-draws span');
                
                for (var j = 0; j < todosDraws.length; j++) {
                    var texto = todosDraws[j].textContent.trim();
                    var numero = parseInt(texto);
                    
                    if (!isNaN(numero) && numero >= 0 && numero <= 36) {
                        results.push(numero.toString());
                    }
                    
                    if (results.length >= 5) break;
                }
            }
            
            return results.slice(0, 5);
            """
            
            resultado = self.driver.execute_script(script)
            
            if isinstance(resultado, list) and len(resultado) >= 3:
                # Preencher com zeros se não tiver 5 números
                while len(resultado) < 5:
                    resultado.append('0')
               
                return resultado[:5]
            else:
                logging.debug(f"Poucos números encontrados: {resultado}")
                return self._captura_alternativa()
                
        except Exception as e:
            logging.debug(f"Erro na captura JavaScript: {e}")
            return self._captura_alternativa()
    
    def _captura_alternativa(self):
        """Método alternativo usando seletores do site conforme mudanca.md"""
        try:
            logging.info("Usando captura alternativa com seletores específicos...")
            
            # Verificar se a página ainda está carregada
            titulo = self.driver.title
            url_atual = self.driver.current_url
            logging.info(f"Página atual: {titulo} | URL: {url_atual}")
            
            # Se não estiver no 888casino, tentar recarregar
            if "888casino" not in url_atual.lower():
                logging.warning("Página não é do 888casino. Recarregando...")
                self.driver.get("https://www.888casino.com/live-casino/#filters=live-roulette")
                time.sleep(15)
            
            numeros_encontrados = []
            
            # Tentar encontrar especificamente os elementos de números da roleta
            try:
                # Primeiro: buscar pelo ID específico 2380064
                elemento_roleta = self.driver.find_elements("css selector", ".cy-live-casino-grid-item-2380064")
                if elemento_roleta:
                    logging.info("Encontrou container da roleta com ID 2380064")
                    spans_numeros = elemento_roleta[0].find_elements("css selector", ".cy-live-casino-grid-item-infobar-draws span")
                    for span in spans_numeros:
                        texto = span.text.strip()
                        if texto.isdigit():
                            num = int(texto)
                            if 0 <= num <= 36:
                                numeros_encontrados.append(str(num))
            except Exception as e:
                logging.debug(f"Erro ao buscar ID específico: {e}")
            
            # Segundo: buscar por qualquer container de draws
            if len(numeros_encontrados) < 3:
                try:
                    todos_draws = self.driver.find_elements("css selector", ".cy-live-casino-grid-item-infobar-draws span")
                    logging.info(f"Encontrou {len(todos_draws)} elementos de draws")
                    for span in todos_draws[:10]:  # Limitar aos primeiros 10
                        texto = span.text.strip()
                        if texto.isdigit():
                            num = int(texto)
                            if 0 <= num <= 36 and str(num) not in numeros_encontrados:
                                numeros_encontrados.append(str(num))
                except Exception as e:
                    logging.debug(f"Erro ao buscar draws gerais: {e}")
            
            # Terceiro: buscar qualquer span que pareça número de roleta
            if len(numeros_encontrados) < 3:
                try:
                    todos_spans = self.driver.find_elements("css selector", "span")
                    logging.info(f"Analisando {len(todos_spans)} spans...")
                    for span in todos_spans[:50]:  # Limitar busca
                        texto = span.text.strip()
                        if texto and len(texto) <= 2 and texto.isdigit():
                            num = int(texto)
                            if 0 <= num <= 36 and str(num) not in numeros_encontrados:
                                numeros_encontrados.append(str(num))
                                if len(numeros_encontrados) >= 5:
                                    break
                except Exception as e:
                    logging.debug(f"Erro ao buscar spans gerais: {e}")
                    
            if len(numeros_encontrados) > 0:
                while len(numeros_encontrados) < 5:
                    numeros_encontrados.append('0')
                logging.info(f"Captura alternativa encontrou: {numeros_encontrados}")
                return numeros_encontrados[:5]
            else:
                logging.warning("Nenhum número encontrado na captura alternativa")
                return ['0', '0', '0', '0', '0']
                
        except Exception as e:
            logging.error(f"Erro na captura alternativa: {e}")
            return ['0', '0', '0', '0', '0']
    
    def enviar_para_api(self, numero):
        """Enviar número para a API"""
        try:
            url = f"{self.api_url}{numero}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Erro API: {e}")
            return False
    
    def executar(self):
        """Loop principal - lógica de assinatura de estado"""
        if not self.iniciar_navegador():
            logging.error("Falha ao iniciar navegador")
            return
            
        logging.info("Monitorando roleta...")
        
        contador_falhas = 0
        max_falhas_consecutivas = 10
        
        try:
            while True:
                try:
                    # Capturar os últimos 5 números
                    ultimos_5 = self.capturar_ultimos_5()
                    
                    # Verificar se a captura está funcionando
                    if ultimos_5 == ['0', '0', '0', '0', '0']:
                        contador_falhas += 1
                        logging.debug(f"Falha na captura #{contador_falhas}")
                        
                        if contador_falhas >= max_falhas_consecutivas:
                            logging.warning(f"Muitas falhas consecutivas na captura ({contador_falhas}). Reiniciando...")
                            
                            # Fechar e reiniciar o navegador
                            if self.driver:
                                self.driver.quit()
                                time.sleep(5)
                            
                            # Tentar reinicializar
                            if self.iniciar_navegador():
                                logging.info("Navegador reiniciado com sucesso")
                                contador_falhas = 0
                                continue
                            else:
                                logging.error("Falha ao reiniciar navegador. Encerrando.")
                                break
                    else:
                        contador_falhas = 0  # Reset contador de falhas
                        logging.debug(f"Captura bem-sucedida: {ultimos_5}")
                    
                    # Criar assinatura do estado atual
                    estado_atual = "-".join(map(str, ultimos_5))
                    
                  
                    
                    # Comparar com estado anterior
                    if estado_atual != self.ultimo_estado:
                        # Estado mudou! Novo sorteio detectado
                        ultimo_numero = ultimos_5[0]
                        
                        # Validar número da roleta (0-36)
                        try:
                            num_int = int(ultimo_numero)
                            if 0 <= num_int <= 36 and num_int != 0:  # Ignorar zeros do fallback
                                print()  # Linha em branco
                                logging.info(f"NOVO NUMERO: {ultimo_numero}")
                                logging.info(f"Estado anterior: {self.ultimo_estado}")
                                logging.info(f"Estado atual: {estado_atual}")
                                
                                # Enviar para API
                                if self.enviar_para_api(ultimo_numero):
                                    self.total_enviados += 1
                                    logging.info(f"Enviado: {ultimo_numero} | Total: {self.total_enviados}")
                                    self.ultimo_estado = estado_atual
                                else:
                                    logging.error(f"Falha ao enviar: {ultimo_numero}")
                            else:
                                if num_int == 0:
                                    logging.debug("Ignorando zero do fallback")
                                else:
                                    logging.warning(f"Número inválido: {ultimo_numero}")
                        except ValueError:
                            logging.warning(f"Número não numérico: {ultimo_numero}")
                    
                    # Aguardar 3 segundos
                    time.sleep(3)
                    
                except Exception as e:
                    logging.error(f"Erro no loop: {e}")
                    contador_falhas += 1
                    if contador_falhas >= max_falhas_consecutivas:
                        logging.error("Muitos erros consecutivos. Tentando reiniciar...")
                        break
                    time.sleep(5)  # Aguardar mais em caso de erro
                
        except KeyboardInterrupt:
            logging.info("Interrompido pelo usuário")
        except Exception as e:
            logging.error(f"Erro crítico: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("Navegador fechado")
                except:
                    pass

def main():
    """Função principal"""
    roleta = RoletaSimples()
    roleta.executar()

if __name__ == "__main__":
    main()
