# Guia de Contribuição para Scryll

Obrigado por considerar contribuir para o Scryll! 🎉

## Como Contribuir

### Reportando Bugs

- Use o GitHub Issues
- Descreva o comportamento esperado vs atual
- Inclua logs relevantes (remova dados sensíveis)
- Especifique: OS, versão Python, site afetado

### Sugerindo Features

- Abra uma Issue com tag `enhancement`
- Explique o caso de uso
- Descreva a solução proposta

### Pull Requests

1. Fork o repositório
2. Crie uma branch descritiva: `git checkout -b feature/minha-feature`
3. Faça commits claros e concisos
4. Adicione testes para novas funcionalidades
5. Garanta que os testes passam: `pytest tests/ -v`
6. Atualize documentação se necessário
7. Submeta o PR com descrição detalhada

### Adicionando Novos Scrapers

Para adicionar suporte a um novo site:

1. Crie arquivo em `scrapers/novo_site.py`
2. Implemente função `fetch_chapters(manga_url: str) -> list[Chapter]`
3. Use decoradores e utilitários existentes:
   ```python
   from core.retry import retry_with_backoff, rate_limiter
   from core.exceptions import NetworkException, ParsingException
   
   @retry_with_backoff()
   def fetch_chapters(manga_url: str) -> list[Chapter]:
       rate_limiter.wait_if_needed("novo_site")
       # Sua implementação
   ```
4. Adicione ao `SCRAPER_MAP` em `main.py`
5. Adicione à lista `SUPPORTED_SITES` em `core/config.py`
6. Adicione testes em `tests/test_novo_site.py`
7. Documente no README.md

### Padrões de Código

- Siga PEP 8
- Use type hints
- Docstrings em funções públicas
- Nomes em português para logs/mensagens de usuário
- Nomes em inglês para código

### Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=core --cov=scrapers --cov-report=html

# Teste específico
pytest tests/test_config.py -v
```

### Commits

Use mensagens claras em português:
- `feat: adiciona scraper para SiteX`
- `fix: corrige parsing de capítulos no ManhuaUS`
- `docs: atualiza README com troubleshooting`
- `test: adiciona testes para retry logic`
- `refactor: simplifica lógica de download`

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque no que é melhor para a comunidade
- Mostre empatia com outros contribuidores

## Dúvidas?

Abra uma Discussion no GitHub ou comente na Issue relevante.

Obrigado! 🙏
