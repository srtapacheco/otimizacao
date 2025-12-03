const express = require("express");
const cors = require("cors");
const { execFile } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json());

const dados = require("./dados_mock.json");

app.get("/api/turmas", (req, res) => {
  res.json(dados.turmas);
});

app.get("/api/avaliacoes", (req, res) => {
  const turmaId = req.query.turma;
  const professorId = req.query.professor;

  const alunosDaTurma = dados.inscricoes
    .filter(i => i.turma_id === turmaId)
    .map(i => i.estudante_id);

  const turmasRelacionadas = new Set(
    dados.inscricoes
      .filter(i => alunosDaTurma.includes(i.estudante_id))
      .map(i => i.turma_id)
  );

  const todas = dados.avaliacoes.filter(a =>
    turmasRelacionadas.has(a.turma)
  );

  const minhas = todas.filter(a => String(a.professor_id) === String(professorId));
  const outras = todas.filter(a => String(a.professor_id) !== String(professorId));

  res.json({ minhas, outras, todas });
});

app.post("/api/criar-avaliacao", (req, res) => {
  const { turma, data, titulo, descricao, professor_id } = req.body;

  const nova = {
    id: dados.avaliacoes.length + 1,
    turma,
    data,
    titulo,
    descricao: descricao || "",
    professor_id
  };

  dados.avaliacoes.push(nova);

  res.json({ ok: true, avaliacao: nova });
});

app.post("/api/sugestoes", (req, res) => {
  const turmaSelecionada = req.body.turma;

  const estudantes_turma = dados.inscricoes
    .filter(i => i.turma_id === turmaSelecionada)
    .map(i => i.estudante_id);

  const turmaInfo = dados.turmas.find(t => t.turma_id === turmaSelecionada);
  const dias_aula = turmaInfo?.dias_aula || ["segunda", "quarta", "sexta"];

  const avaliacoes_relevantes = [];

  dados.avaliacoes.forEach(av => {
    const alunos_da_turma_av = dados.inscricoes
      .filter(i => i.turma_id === av.turma)
      .map(i => i.estudante_id);

    if (alunos_da_turma_av.some(a => estudantes_turma.includes(a))) {
      avaliacoes_relevantes.push(av);
    }
  });

  const payload = {
    turma: turmaSelecionada,
    intervaloInicial: req.body.intervaloInicial,
    intervaloFinal: req.body.intervaloFinal,
    dias_aula,
    avaliacoes_existentes: avaliacoes_relevantes,
    inscricoes: dados.inscricoes,
    estudantes_turma,
    feriados: dados.feriados || [],
    datas_bloqueadas: dados.datas_bloqueadas || [],
    espacamento_minimo_dias: dados.espacamento_minimo_dias || 3
  };

  execFile(
    process.platform === "win32" ? "python" : "python3",
    ["solver.py", JSON.stringify(payload)],
    (err, stdout) => {
      if (err) {
        console.error("Erro ao executar solver:", err);
        return res.status(500).json({ error: "erro solver" });
      }

      try {
        const out = JSON.parse(stdout);
        res.json(out);
      } catch (e) {
        console.error("Erro ao interpretar saída:", stdout);
        res.status(500).json({ error: "erro parse" });
      }
    }
  );
});

app.listen(3000, () => {
  console.log("Servidor rodando em: http://localhost:3000");
});