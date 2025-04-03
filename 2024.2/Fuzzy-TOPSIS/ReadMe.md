# Fuzzy-TOPSIS - T�cnica para Ordena��o de Prefer�ncias por Similaridade com a Solu��o Ideal, a partir da utiliza��o

## Descri��o
Este projeto implementa o m�todo **Fuzzy-TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution), uma t�cnica de an�lise de decis�o multicrit�rio. O objetivo � classificar alternativas com base em m�ltiplos crit�rios, considerando pesos diferentes para cada um. Esse m�todo leva em considera��o
tamb�m uma abordagem de trabalhar com linguagem natural para classifica��o dos pesos, sendo essa linguagem transformada em n�meros fuzzy para execu��o do algoritmo.

## Autores
- **Cau� Marinho**
- **Matheus Nepomuceno**

## Como Usar

### Entrada de Dados
O c�digo recebe uma entrada no formato JSON contendo:
- **method**: Nome do m�todo ("Fuzzy_TOPSIS").
- **parameters**: Um dicion�rio contendo:
  - **alternatives**: Lista das alternativas.
  - **criteria**: Lista dos crit�rios.
  - **performance_matrix**: Matriz correspondente as alternativas e suas classifica��es em rela��o a cada crit�rio em n�meros fuzzy.
  - **criteria_types**: Especifica��o se o crit�rio � de **custo (min)** ou **benef�cio (max)**.
  - **weights**: Pesos de cada crit�rio.

#### Exemplo de Entrada:
```json
{
  "method": "Fuzzy_TOPSIS",
  "parameters": {
    "alternatives": ["F1", "F2", "F3"],
    "criteria": ["C1", "C2", "C3"],
    "performance_matrix": {
      "F1": [[0.6, 0.7, 0.8], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
      "F2": [[0.5, 0.6, 0.7], [0.3, 0.4, 0.5], [0.6, 0.7, 0.8]],
      "F3": [[0.7, 0.8, 0.9], [0.5, 0.6, 0.7], [0.8, 0.9, 1.0]]
    },
    "criteria_types": {
      "C1": "max",
      "C2": "min",
      "C3": "max"
    },
    "weights": {
      "C1": [0.3, 0.4, 0.5],
      "C2": [0.2, 0.3, 0.4],
      "C3": [0.4, 0.5, 0.6]
    }
  }
}
```

### Execu��o do C�digo
Para rodar o c�digo, basta executar:
```python
from main import FuzzyTOPSIS

data = { # Dados no formato json }
result = process_fuzzy_topsis(data)
print(resultado)
```

### Sa�da Esperada
O c�digo retorna um json contendo os resultados, os quais s�o:
- **proximities**: Proximidade das alternativas em rela��o a solu��o ideal positiva.
- **ranking**: Lista das alternativas ordenadas da melhor para pior escolha.
- **best alternative**: Melhor alternativa.
- **distances**: Dicion�rio que cont�m as dist�ncias de cada alternativa para as solu��es ideais positivas e negativas.

#### Exemplo de Sa�da:
```json
{
  "method": "Fuzzy_TOPSIS",
  "results": {
    "proximities": {
      "F1": 0.72,
      "F2": 0.65,
      "F3": 0.80
    },
    "ranking": ["F3", "F1", "F2"],
    "best_alternative": "F3",
    "distances": {
      "F1": {
        "ideal": 0.28,
        "negative_ideal": 0.72
      },
      "F2": {
        "ideal": 0.35,
        "negative_ideal": 0.65
      },
      "F3": {
        "ideal": 0.20,
        "negative_ideal": 0.80
      }
    }
  }
}
```

## Licen�a
Este projeto est� sob a licen�a MIT.