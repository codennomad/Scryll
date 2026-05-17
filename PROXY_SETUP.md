# 🔐 Guia de Configuração de Proxy

## Por que usar proxy?

Quando seu IP é bloqueado pelo Cloudflare (erro 403 persistente), usar um proxy permite:
- ✅ Contornar bloqueio de IP
- ✅ Rotação automática entre múltiplos IPs
- ✅ Bypass de restrições geográficas
- ✅ Maior taxa de sucesso

## 🆓 Opções de Proxy

### 1. **Proxy Gratuito (Não Recomendado para Produção)**
Proxies gratuitos são lentos e instáveis, mas servem para testes.

**Fontes:**
- https://www.proxy-list.download/
- https://free-proxy-list.net/
- https://www.sslproxies.org/

**Exemplo:**
```bash
# Teste um proxy gratuito
curl --proxy http://167.172.173.210:45399 https://manhuaus.com/
```

### 2. **VPN como Proxy (Recomendado para Uso Pessoal)**
Use sua própria VPN como proxy local.

#### ProtonVPN (Gratuito)
```bash
# Arch Linux
sudo pacman -S openvpn
yay -S protonvpn-cli

# Conecte
protonvpn-cli connect --fastest

# Agora todas as requisições do Scryll usarão a VPN
```

#### Configurar VPN + SOCKS5:
```bash
# Instale dante (SOCKS proxy)
sudo pacman -S dante

# Configure /etc/sockd.conf
# Então no .env:
PROXY_HTTP=socks5://127.0.0.1:1080
PROXY_HTTPS=socks5://127.0.0.1:1080
```

### 3. **Proxy Residencial Pago (Melhor para Produção)**
Proxies residenciais são IPs reais de provedores, não detectados como datacenter.

#### Serviços Recomendados:

**Bright Data (ex-Luminati)** - Líder do mercado
- 💰 ~$500/mês plano básico
- ✅ 72M+ IPs residenciais
- ✅ Rotação automática
- 🌐 https://brightdata.com

**Smartproxy**
- 💰 ~$75/mês (5GB)
- ✅ 40M+ IPs residenciais
- ✅ Mais acessível
- 🌐 https://smartproxy.com

**Oxylabs**
- 💰 ~$300/mês
- ✅ 100M+ IPs residenciais
- ✅ Alta qualidade
- 🌐 https://oxylabs.io

**IPRoyal**
- 💰 ~$7/GB (mais barato)
- ✅ Bom custo-benefício
- 🌐 https://iproyal.com

#### Cadastro Típico:
1. Criar conta no serviço
2. Copiar credenciais (host:port, user, pass)
3. Adicionar ao `.env`

### 4. **Proxy Privado / Datacenter** (Intermediário)
Mais barato que residencial, mas pode ser detectado.

**ProxyRack**
- 💰 ~$65/mês (5 proxies)
- 🌐 https://www.proxyrack.com/

## ⚙️ Configuração no Scryll

### Proxy Simples (Sem Autenticação)
```bash
# .env
PROXY_HTTP=http://167.172.173.210:45399
PROXY_HTTPS=http://167.172.173.210:45399
```

### Proxy com Autenticação
```bash
# .env
PROXY_HTTP=http://proxy.exemplo.com:8080
PROXY_HTTPS=http://proxy.exemplo.com:8080
PROXY_USERNAME=seu_usuario
PROXY_PASSWORD=sua_senha
```

### Múltiplos Proxies (Rotação Automática)
```bash
# .env
PROXY_1=http://proxy1.com:8080|https://proxy1.com:8080
PROXY_2=http://proxy2.com:8080|https://proxy2.com:8080|user|pass
PROXY_3=http://proxy3.com:8080|https://proxy3.com:8080
```

O sistema irá rotacionar entre eles automaticamente!

## 🧪 Testando Proxy

### 1. Teste Manual
```bash
# Teste com curl
curl --proxy http://proxy:port https://httpbin.org/ip

# Deve mostrar IP do proxy, não o seu
```

### 2. Teste no Scryll
```bash
cd /home/kaspian/Scryll
./scryllenv/bin/python3 -c "
from core.proxy_manager import proxy_manager

if proxy_manager.has_proxies():
    print('✅ Proxies configurados:', len(proxy_manager.proxies))
    proxy = proxy_manager.get_next_proxy()
    if proxy_manager.test_proxy(proxy):
        print('✅ Proxy funcionando!')
    else:
        print('❌ Proxy não está funcionando')
else:
    print('⚠️  Nenhum proxy configurado')
"
```

## 🚀 Uso no Scryll

Após configurar o proxy no `.env`, o Scryll irá:
1. **Detectar automaticamente** proxies configurados
2. **Usar em todas as requisições** (cloudscraper + Selenium)
3. **Rotacionar entre proxies** se múltiplos configurados
4. **Logar uso** nos logs para debugging

```bash
# Execute normalmente
python3 main.py

# Você verá nos logs:
# 🔄 Usando proxy: http://proxy.com:8080
```

## 📊 Qual Solução Escolher?

| Cenário | Solução Recomendada | Custo |
|---------|---------------------|-------|
| **Teste rápido** | Proxy gratuito | Grátis |
| **Uso pessoal** | ProtonVPN | Grátis |
| **Semi-profissional** | Proxy datacenter | ~$50/mês |
| **Produção** | Proxy residencial | ~$100+/mês |

## 💡 Dicas

### Performance
- Proxies gratuitos: Lentos (~5-10x mais lento)
- Datacenter: Rápidos
- Residencial: Médios mas mais confiáveis

### Para Economizar
1. Use VPN pessoal (sem custo extra)
2. Configure para rodar à noite (Cloudflare menos rigoroso)
3. Aumente delays entre requisições
4. Use proxies apenas quando necessário

### Checklist de Problemas

❌ **Proxy não funciona?**
```bash
# Teste conectividade
curl -v --proxy http://proxy:port https://httpbin.org/ip

# Verifique autenticação
# Verifique firewall
# Teste outro proxy
```

❌ **Ainda recebe 403?**
- Proxy pode estar em blacklist do Cloudflare
- Tente proxy residencial
- Aguarde 1-2 horas (cooldown do IP original)

❌ **Muito lento?**
- Use proxy geograficamente próximo
- Teste velocidade: `curl -w "%{time_total}" --proxy ...`
- Considere proxy datacenter premium

## 🔒 Segurança

**NUNCA commite proxies no git!**
- `.env` está no `.gitignore` ✅
- Nunca compartilhe credenciais
- Rotate senhas periodicamente

## 📝 Exemplos Completos

### ProtonVPN + Scryll
```bash
# 1. Conecte VPN
protonvpn-cli connect --fastest

# 2. Execute Scryll (usará IP da VPN automaticamente)
python3 main.py

# 3. Desconecte depois
protonvpn-cli disconnect
```

### Smartproxy + Scryll
```bash
# 1. Configure .env com credenciais do Smartproxy
PROXY_HTTP=http://gate.smartproxy.com:7000
PROXY_HTTPS=http://gate.smartproxy.com:7000
PROXY_USERNAME=seu_usuario
PROXY_PASSWORD=sua_senha

# 2. Execute
python3 main.py

# Logs mostrarão: 🔄 Usando proxy: http://gate.smartproxy.com:7000
```

### Rotação de 3 Proxies
```bash
# .env
PROXY_1=http://proxy1.example.com:8080|https://proxy1.example.com:8080
PROXY_2=http://proxy2.example.com:8080|https://proxy2.example.com:8080
PROXY_3=http://proxy3.example.com:8080|https://proxy3.example.com:8080

# Execute - sistema rotaciona automaticamente
python3 main.py
```

---

**Recomendação Final:**
- **Teste Rápido**: Use proxy gratuito ou ProtonVPN
- **Longo Prazo**: Invista em Smartproxy (~$75/mês)
- **Crítico**: Bright Data (mais caro mas mais confiável)
