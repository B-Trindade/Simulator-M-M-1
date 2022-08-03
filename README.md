# Simulator-M-M-1
Projeto final para a disciplina de AD (ICP 515) da UFRJ. Consiste em criar um simulador de fila M/M/1 e realizar diversas análises sobre a mesma

### Como rodar o simulador

Iremos rodar o script `simulator.py`, passando alguns parâmetros:

- Disciplina da fila
- Número de fregueses
- Rho
- Semente [opcional]

Exemplos:

- Disciplina FCFS, com 400 fregueses por batch, rho = 0.6 e seed = 1

```
python3 .\src\simulator.py fcfs 400 0.6 1
```

---

- Disciplina LCFS, com 200 fregueses por batch, rho = 0.2 e seed aleatória

```
python3 .\src\simulator.py lcfs 200 0.2
```

---

### Como rodar a análise das estatísticas geradas

Ao rodar o simulador, será gerado um arquivo com nome equivalente ao seguinte padrão:

1. `results_{disciplina}-{num_fregueses}-{rho}.csv` (caso tenhamos seed aleatória)
2. `results_{disciplina}-{num_fregueses}-{rho}-{seed}.csv` (caso tenhamos seed fixa)

Com isso, podemos rodar o jupyter notebook `data_analytics.ipynb`, bastando mudar o nome do arquivo, presente na variável `FILE_NAME`.
