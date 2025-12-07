<template>
  <HeaderComponent />

  <div class="container">
    <main>
      <h1>Calendário de Avaliações da Turma</h1>

      <div class="filtro">
        <v-icon class="filter-icon icon">mdi-filter-variant</v-icon>

        <div class="toggle-buttons-container green">
          <v-icon class="icon">mdi-calendar-account-outline</v-icon>
          <button class="toggle green selected" @click="toggle('minhas', $event)">
            Agendadas por você
          </button>
        </div>

        <div class="toggle-buttons-container pink">
          <v-icon class="icon">mdi-calendar-blank-outline</v-icon>
          <button class="toggle pink selected" @click="toggle('outras', $event)">
            Agendadas por outros
          </button>
        </div>
      </div>

      <div class="calendar-header">
        <div class="year">{{ currentViewYear }}</div>

        <div class="month">
          <v-icon @click="stepMonth(-1)" class="month-icon">mdi-chevron-left</v-icon>
          <h2>{{ months[currentViewMonth].name }}</h2>
          <v-icon @click="stepMonth(1)" class="month-icon">mdi-chevron-right</v-icon>
        </div>
      </div>

      <div class="calendar-container">
        <div class="week-days" v-for="(w, index) in weekDays" :key="'wd-'+index">
          <p>{{ w.abrev }}</p>
        </div>

        <div
          class="calendar-day"
          v-for="(day, idx) in daysInCalendarView"
          :key="'day-'+idx"
          :class="{ inactive: !day.isCurrentMonth }"
        >
          <p class="day-of-month">{{ day.day }}</p>

          <div class="exams-badges">
            <div
              v-if="avaliacoesFiltradas(day).some(a => a.isMine)"
              class="badge mine"
            >
              {{ avaliacoesFiltradas(day).filter(a => a.isMine).length }}
            </div>

            <div
              v-if="avaliacoesFiltradas(day).some(a => !a.isMine)"
              class="badge other"
            >
              {{ avaliacoesFiltradas(day).filter(a => !a.isMine).length }}
            </div>
          </div>
        </div>
      </div>

      <div class="actions-bar">
        <button class="custom-action-button" @click="openIntervalModal">
          Marcar Avaliação
        </button>
      </div>
    </main>
  </div>

  <!-- Modal Intervalo -->
  <div v-if="showIntervalModal" class="modal-backdrop">
    <div class="modal-card-custom">
      <h3>Selecione o intervalo da avaliação</h3>

      <label class="modal-label">Data inicial:</label>
      <input type="date" v-model="intervaloInicial" />

      <label class="modal-label">Data final:</label>
      <input type="date" v-model="intervaloFinal" />

      <div class="modal-actions-custom">
        <button class="modal-confirm-button" @click="gerarSugestoes">
          Gerar sugestões
        </button>
        <button class="modal-cancel-button" @click="closeIntervalModal">
          Cancelar
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Sugestões -->
  <div v-if="showSugestoesModal" class="modal-backdrop">
    <div class="modal-card-custom">
      <h3>Sugestões do sistema</h3>

      <p class="suggestion-title">Melhor data recomendada:</p>

      <div
        class="suggestion-card best clickable"
        @click="selecionarData(melhorData)"
        :class="{ selected: dataEscolhida === melhorData }"
      >
        {{ melhorData }}
      </div>

      <p class="suggestion-title">Outras boas opções:</p>

      <div
        class="suggestion-card clickable"
        v-for="d in melhoresAlternativas"
        :key="d"
        @click="selecionarData(d)"
        :class="{ selected: dataEscolhida === d }"
      >
        {{ d }}
      </div>

      <div class="modal-actions-custom">
        <button class="modal-confirm-button" @click="goToTitulo">
          Continuar
        </button>
        <button class="modal-cancel-button" @click="closeSugestoesModal">
          Voltar
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Título -->
  <div v-if="showTituloModal" class="modal-backdrop">
    <div class="modal-card-custom">
      <h3>Detalhes da Avaliação</h3>

      <label class="modal-label">Título da avaliação *</label>
      <input type="text" v-model="tituloAvaliacao" />

      <label class="modal-label">Descrição</label>
      <textarea v-model="descricaoAvaliacao"></textarea>

      <div class="modal-actions-custom">
        <button class="modal-confirm-button" @click="confirmarAvaliacao">
          Confirmar Avaliação
        </button>
        <button class="modal-cancel-button" @click="closeTituloModal">
          Voltar
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {
  subDays,
  getDate,
  getDay,
  getYear,
  getMonth,
  getDaysInMonth,
  addMonths
} from "date-fns";

import HeaderComponent from "@/components/HeaderComponent.vue";

export default {
  components: { HeaderComponent },

  data() {
    return {
      professorId: localStorage.getItem("ID_USUARIO") || "666",

      mostrarMinhas: true,
      mostrarOutras: true,

      weekDays: [
        { abrev: "DOM", order: 0 },
        { abrev: "SEG", order: 1 },
        { abrev: "TER", order: 2 },
        { abrev: "QUA", order: 3 },
        { abrev: "QUI", order: 4 },
        { abrev: "SEX", order: 5 },
        { abrev: "SÁB", order: 6 }
      ],

      months: [
        { name: "Janeiro", order: 0 },
        { name: "Fevereiro", order: 1 },
        { name: "Março", order: 2 },
        { name: "Abril", order: 3 },
        { name: "Maio", order: 4 },
        { name: "Junho", order: 5 },
        { name: "Julho", order: 6 },
        { name: "Agosto", order: 7 },
        { name: "Setembro", order: 8 },
        { name: "Outubro", order: 9 },
        { name: "Novembro", order: 10 },
        { name: "Dezembro", order: 11 }
      ],

      currentViewDate: new Date(),
      currentViewMonth: getMonth(new Date()),
      currentViewYear: getYear(new Date()),
      daysInCalendarView: [],

      selectedTurma: "",
      avaliacoes: [],

      showIntervalModal: false,
      showSugestoesModal: false,
      showTituloModal: false,

      intervaloInicial: "",
      intervaloFinal: "",
      melhorData: "",
      melhoresAlternativas: [],
      dataEscolhida: "",
      tituloAvaliacao: "",
      descricaoAvaliacao: ""
    };
  },

  methods: {
    toggle(tipo, event) {
      const isSelected = event.target.classList.contains("selected");
      if (tipo === "minhas") this.mostrarMinhas = !this.mostrarMinhas;
      else this.mostrarOutras = !this.mostrarOutras;
      if (isSelected) event.target.classList.remove("selected");
      else event.target.classList.add("selected");
    },

    async carregarAvaliacoes() {
      if (!this.selectedTurma) return;

      const resp = await fetch(
        `http://localhost:3000/api/avaliacoes?turma=${this.selectedTurma}&professor=${this.professorId}`
      );

      const dados = await resp.json();

      this.avaliacoes = [
        ...dados.minhas.map(a => ({ ...a, isMine: true })),
        ...dados.outras.map(a => ({ ...a, isMine: false }))
      ];
    },

    loadCalendarDaysInMonth(currentMonth1stDay) {
      const daysInCurrentMonth = [];

      for (let i = 1; i <= getDaysInMonth(currentMonth1stDay); i++) {
        daysInCurrentMonth.push({ day: i, isCurrentMonth: true });
      }

      const firstWeekDayInMonth = getDay(
        subDays(currentMonth1stDay, getDate(currentMonth1stDay) - 1)
      );

      const lastDayOfPreviousMonth = getDate(
        subDays(currentMonth1stDay, getDate(currentMonth1stDay))
      );

      if (firstWeekDayInMonth > 0) {
        for (let i = 0; i < firstWeekDayInMonth; i++) {
          daysInCurrentMonth.unshift({
            day: lastDayOfPreviousMonth - i,
            isCurrentMonth: false
          });
        }
      }

      const daysOfNextMonth = 35 - daysInCurrentMonth.length;

      for (let i = 1; i <= daysOfNextMonth; i++) {
        daysInCurrentMonth.push({ day: i, isCurrentMonth: false });
      }

      this.daysInCalendarView = daysInCurrentMonth;
    },

    async stepMonth(step) {
      this.currentViewMonth = (this.currentViewMonth + step + 12) % 12;
      this.currentViewDate = addMonths(this.currentViewDate, step);
      this.currentViewYear = getYear(this.currentViewDate);
      this.loadCalendarDaysInMonth(this.currentViewDate);

      if (this.selectedTurma) {
        await this.carregarAvaliacoes();
      }
    },

    avaliacoesFiltradas(day) {
      const data = `${this.currentViewYear}-${String(
        this.currentViewMonth + 1
      ).padStart(2, "0")}-${String(day.day).padStart(2, "0")}`;

      return this.avaliacoes.filter(a => a.data === data);
    },

    openIntervalModal() {
      this.showIntervalModal = true;
    },

    closeIntervalModal() {
      this.showIntervalModal = false;
    },

    async gerarSugestoes() {
      if (!this.intervaloInicial || !this.intervaloFinal) return;

      const payload = {
        turma: this.selectedTurma,
        intervaloInicial: this.intervaloInicial,
        intervaloFinal: this.intervaloFinal,
        professor: this.professorId
      };

      const resp = await fetch("http://localhost:3000/api/sugestoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const dados = await resp.json();

      this.melhorData = dados.melhorData;
      this.melhoresAlternativas = dados.melhoresAlternativas;

      this.showIntervalModal = false;
      this.showSugestoesModal = true;
    },

    selecionarData(data) {
      this.dataEscolhida = data;
    },

    closeSugestoesModal() {
      this.showSugestoesModal = false;
      this.showIntervalModal = true;
    },

    goToTitulo() {
      if (!this.dataEscolhida) return;
      this.showSugestoesModal = false;
      this.showTituloModal = true;
    },

    closeTituloModal() {
      this.showTituloModal = false;
      this.showSugestoesModal = true;
    },

    async confirmarAvaliacao() {
      const payload = {
        turma: this.selectedTurma,
        data: this.dataEscolhida,
        titulo: this.tituloAvaliacao,
        descricao: this.descricaoAvaliacao,
        professor_id: this.professorId
      };

      await fetch("http://localhost:3000/api/criar-avaliacao", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      this.showTituloModal = false;

      await this.carregarAvaliacoes();
    }
  },

  async mounted() {
    this.loadCalendarDaysInMonth(this.currentViewDate);

    const qTurma = this.$route.query.turma;
    this.selectedTurma = qTurma;

    if (this.selectedTurma) {
      await this.carregarAvaliacoes();
    }
  }
};
</script>


<style scoped>
.container {
  margin: 8rem 0 2rem;
  width: 100%;
  display: flex;
  align-content: center;
  justify-content: center;
}

main {
  max-width: 1080px;
  padding: 1rem 2rem;
}

main h1 {
  margin-bottom: 2rem;
}

.filtro {
  display: flex;
  align-items: center;
  width: 100%;
  padding: .8rem 0;
  border-top: 1px solid var(--light-gray);
  border-bottom: 1px solid var(--light-gray);
}

.filtro .filter-icon {
  color: var(--text-gray);
  margin-right: .3rem;
}

.toggle-buttons-container {
  display: flex;
  align-items: center;
  margin-left: 1rem;
}

.toggle-buttons-container.green .icon {
  color: var(--green-text);
}

.toggle-buttons-container.pink .icon {
  color: var(--negative-text);
}

.toggle {
  display: flex;
  align-items: center;
  margin-left: .5rem;
  padding: .5rem .8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: .3s;
  font-weight: bold;
}

.toggle.pink {
  color: var(--negative-text);
  border: 1px solid var(--negative-color-bg);
}

.toggle.green {
  color: var(--green-text);
  border: 1px solid var(--transparent-green);
}

.toggle.green.selected {
  background-color: var(--transparent-green);
}

.toggle.pink.selected {
  background-color: var(--negative-color-bg);
}

.calendar-header {
  margin-top: 2rem;
}

.year {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  color: var(--light-gray-text);
}

.month {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 100%;
  color: var(--green-text);
}

.month h2 {
  font-weight: 600;
  width: 50%;
  text-align: center;
}

.month .month-icon {
  font-weight: 500;
  font-size: 2.2rem;
}

.calendar-container {
  margin-top: 2rem;
  gap: .25rem;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-days {
  text-align: center;
  margin-bottom: 1rem;
}

.calendar-day {
  width: 100%;
  height: 6rem;
  background-color: var(--transparent-green);
  border-radius: 8px;
  padding: .4rem .6rem;
  position: relative;
}

.calendar-day.inactive {
  background-color: var(--transparent-gray);
}

.day-of-month {
  font-size: 0.9rem;
  font-weight: bold;
}

.exams {
  margin-top: 0.3rem;
}

.exam-pill {
  background-color: var(--green-text);
  color: white;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 0.7rem;
  margin-bottom: 4px;
  width: fit-content;
}

.actions-bar {
  margin: 2rem 0;
  width: 100%;
  display: flex;
  justify-content: center;
}

.custom-action-button {
  background-color: var(--green-text);
  color: white;
  padding: 0.7rem 1.4rem;
  border-radius: 8px;
  border: none;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
}

.custom-action-button:hover {
  opacity: 0.9;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(00, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

/* ============================== */
/*   MODAL INTERVALO DE DATAS     */
/* ============================== */

.modal-card-custom {
  background: white;
  padding: 2rem 2rem 1.5rem;
  border-radius: 12px;
  width: 380px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.25);
}

.modal-card-custom h3 {
  font-size: 1rem;
  text-align: center;
  margin-bottom: 1.6rem;
  font-weight: 600;
}

.modal-label {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  display: block;
  color: #555;
}

/* Inputs alinhados e bonitos */
.modal-card-custom input[type="date"] {
  width: 100%;
  padding: 0.7rem;
  font-size: 0.95rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-bottom: 1rem;
  background: white;
  color: #333;
}

/* ============================== */
/* Botões da modal                */
/* ============================== */

.modal-actions-custom {
  margin-top: 1.2rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.modal-confirm-button {
  flex: 1;
  background-color: #1db954;   /* verde */
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.7rem;
  cursor: pointer;
  font-weight: bold;
}

.modal-cancel-button {
  flex: 1;
  background-color: #e91e63;   /* rosa */
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.7rem;
  cursor: pointer;
  font-weight: bold;
}

.modal-confirm-button:hover,
.modal-cancel-button:hover {
  opacity: 0.9;
}

.modal-actions-custom {
  margin-top: 1.5rem;
  display: flex;
  justify-content: space-between;
}

.modal-confirm-button {
  background-color: var(--green-text);
  color: white;
  padding: .55rem 1rem;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.modal-cancel-button {
  background-color: var(--negative-text);
  color: white;
  padding: .55rem 1rem;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.input-date-custom {
  width: 100%;
  padding: .6rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.input-text-custom {
  width: 100%;
  padding: .6rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

.textarea-custom {
  width: 100%;
  height: 90px;
  padding: .6rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
  resize: none;
}

.suggestion-title {
  margin-top: 1rem;
  font-weight: bold;
}

.suggestion-card {
  background-color: var(--transparent-green);
  padding: .6rem;
  border-radius: 8px;
  margin-top: .5rem;
}

.suggestion-card.best {
  background-color: var(--green-text);
  color: white;
}

@media (max-width: 767px) {
  .container {
    margin: 6rem 0 2rem;
  }

  main {
    padding: 1rem 1rem;
  }

  .toggle {
    font-size: .7rem;
    padding: .5rem;
  }

  .icon {
    font-size: 1rem;
  }

  .toggle-buttons-container {
    margin-left: .5rem;
  }

  .calendar-day {
    height: 4rem;
  }
}

.exams-badges {
  position: absolute;
  bottom: 6px;
  right: 6px;
  display: flex;
  gap: 4px;
}

.badge {
  width: 22px;
  height: 22px;
  font-size: 0.75rem;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.badge.mine {
  background-color: var(--green-text);
}

.badge.other {
  background-color: var(--negative-text);
}


</style>
