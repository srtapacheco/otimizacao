import sys
import json
from datetime import datetime, timedelta
from ortools.linear_solver import pywraplp

# ----------------------------------------------------------
# Entrada
# ----------------------------------------------------------
raw = sys.argv[1]
data = json.loads(raw)

turma = data["turma"]
intervaloInicial = data["intervaloInicial"]
intervaloFinal = data["intervaloFinal"]

avaliacoes_existentes = data["avaliacoes_existentes"]
inscricoes = data["inscricoes"]
estudantes_turma = data["estudantes_turma"]

feriados = data.get("feriados", [])
datas_bloqueadas = data.get("datas_bloqueadas", [])
espacamento_minimo_dias = data.get("espacamento_minimo_dias", 0)


# ----------------------------------------------------------
# 1. Dias de aula válidos
# ----------------------------------------------------------
dias_semana_map = {
    "segunda": 0, "terca": 1, "terça": 1,
    "quarta": 2, "quinta": 3, "sexta": 4
}

dias_validos = {dias_semana_map[d.lower()] for d in data["dias_aula"]}


# ----------------------------------------------------------
# 2. Construir datas elegíveis
# ----------------------------------------------------------
dt_i = datetime.fromisoformat(intervaloInicial)
dt_f = datetime.fromisoformat(intervaloFinal)

datas = []
d = dt_i

while d <= dt_f:
    data_str = d.strftime("%Y-%m-%d")

    if d.weekday() >= 5:
        d += timedelta(days=1)
        continue

    if d.weekday() not in dias_validos:
        d += timedelta(days=1)
        continue

    if data_str in feriados:
        d += timedelta(days=1)
        continue

    if data_str in datas_bloqueadas:
        d += timedelta(days=1)
        continue

    datas.append(data_str)
    d += timedelta(days=1)

if not datas:
    print(json.dumps({"melhorData": None, "melhoresAlternativas": []}))
    sys.exit()


# ----------------------------------------------------------
# 3. Carga fixa por dia
# ----------------------------------------------------------
carga_fixa = {s: {d: 0 for d in datas} for s in estudantes_turma}

for av in avaliacoes_existentes:
    dia = av["data"]
    turma_av = av["turma"]
    alunos = [i["estudante_id"] for i in inscricoes if i["turma_id"] == turma_av]

    for s in alunos:
        if s in carga_fixa and dia in carga_fixa[s]:
            carga_fixa[s][dia] += 1


# ----------------------------------------------------------
# 4. Espaçamento
# ----------------------------------------------------------
ultimas_datas = {s: [] for s in estudantes_turma}

for av in avaliacoes_existentes:
    dia = datetime.fromisoformat(av["data"])
    turma_av = av["turma"]
    alunos = [i["estudante_id"] for i in inscricoes if i["turma_id"] == turma_av]

    for s in alunos:
        if s in ultimas_datas:
            ultimas_datas[s].append(dia)

for s in ultimas_datas:
    ultimas_datas[s].sort()


# ----------------------------------------------------------
# 5. Carga semanal existente
# ----------------------------------------------------------
def semana(d):
    return datetime.fromisoformat(d).isocalendar()[1]

carga_existente_semana = {}
for av in avaliacoes_existentes:
    w = datetime.fromisoformat(av["data"]).isocalendar()[1]
    carga_existente_semana[w] = carga_existente_semana.get(w, 0) + 1


# ----------------------------------------------------------
# 6. Solver
# ----------------------------------------------------------
solver = pywraplp.Solver.CreateSolver("CBC")

x = {d: solver.IntVar(0, 1, f"x_{d}") for d in datas}
T = solver.NumVar(0, solver.infinity(), "T")

solver.Add(sum(x[d] for d in datas) == 1)

for s in estudantes_turma:
    for d in datas:
        solver.Add(carga_fixa[s][d] + x[d] <= T)

conflitos = solver.NumVar(0, solver.infinity(), "conflitos")
solver.Add(conflitos == sum(x[d] * sum(carga_fixa[s][d] for s in estudantes_turma)
                            for d in datas))

espacamento_total = solver.NumVar(0, solver.infinity(), "espacamento")
solver.Add(
    espacamento_total ==
    sum(
        x[d] * (
            min(abs((datetime.fromisoformat(d) - dia_ant).days)
                for dia_ant in ultimas_datas[s]) if ultimas_datas[s] else 0
        )
        for s in estudantes_turma for d in datas
    )
)

variabilidade = solver.NumVar(0, solver.infinity(), "variabilidade")
solver.Add(
    variabilidade ==
    sum(x[d] * carga_existente_semana.get(semana(d), 0) for d in datas)
)

alpha = 1.0
beta = 0.1
gamma = 0.05

solver.Minimize(
    T +
    alpha * conflitos -
    beta * espacamento_total +
    gamma * variabilidade
)

status = solver.Solve()

melhor = next(d for d in datas if x[d].solution_value() == 1)


# ----------------------------------------------------------
# 7. RANKING DE ALTERNATIVAS
# ----------------------------------------------------------

def func_objetivo(d):
    # carga do dia
    carga_dia = sum(carga_fixa[s][d] for s in estudantes_turma)

    # espacamento
    if ultimas_datas[s]:
        espac = min(abs((datetime.fromisoformat(d) - dia_ant).days)
                    for s in estudantes_turma
                    for dia_ant in ultimas_datas[s])
    else:
        espac = 0

    # variabilidade semanal
    var = carga_existente_semana.get(semana(d), 0)

    # mesma fórmula do solver
    return (
        carga_dia
        + alpha * carga_dia
        - beta * espac
        + gamma * var
    )

alternativas = sorted(
    [d for d in datas if d != melhor],
    key=lambda d: func_objetivo(d)
)[:5]

print(json.dumps({
    "melhorData": melhor,
    "melhoresAlternativas": alternativas
}))