<template>
  <v-app>
    <HeaderComponent :hasBackButton="true"/>

    <v-main>
      <div class="external">
        <div class="container">

          <!-- TEXTO ORIENTATIVO GRANDE, UNIFORME -->
          <p class="instruction">
            Escolha abaixo para qual turma você deseja agendar uma avaliação.
          </p>

          <!-- LISTA DE TURMAS -->
          <div class="card-container">
            <v-card
              v-for="t in turmas"
              :key="t.turma_id"
              class="custom-card"
              elevation="2"
              @click="abrirCalendario(t)"
            >
              <div class="card-content">
                <div>
                  <div class="custom-title-card">{{ t.codigo }}</div>
                  <div class="custom-subtitle-card">{{ t.nome }}</div>

                  <!-- CORREÇÃO: evita erro ao acessar t.cursos -->
                  <div class="custom-description-card">
                    {{ Array.isArray(t.cursos) ? t.cursos.join(', ') : '' }}
                  </div>
                </div>
              </div>
            </v-card>
          </div>

        </div>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import HeaderComponent from '@/components/HeaderComponent.vue'

export default {
  components: { HeaderComponent },

  data() {
    return {
      turmas: []
    };
  },

  async created() {
    const professorId = localStorage.getItem("ID_USUARIO") || 777;

    const resp = await fetch(`http://localhost:3000/api/turmas?professor=${professorId}`);
    this.turmas = await resp.json();
  },

  methods: {
    abrirCalendario(turma) {
      this.$router.push(`/calendario?turma=${turma.turma_id}`);
    }
  }
}
</script>


<style scoped>
/* -----------------------------
   LAYOUT GERAL 
----------------------------- */

html, body {
  background: #F4F7F9 !important;
}

.external {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-top: 7em;
}

.container {
  max-width: 660px;
  width: 100%;
  padding: 0 2rem;
}

/* -----------------------------
   TEXTO PRINCIPAL (GRANDE)
----------------------------- */

.instruction {
  color: #4F5873;
  font-size: 2em;
  font-weight: 400;
  text-align: left;
  margin-bottom: 2rem;
  line-height: 1.3;
}

/* -----------------------------
   CARDS DAS TURMAS
----------------------------- */

.card-container {
  width: 100%;
  text-align: left;
}

.custom-card {
  cursor: pointer;
  background: #F4F7F9 !important;
  border-radius: 10px !important;
  margin-bottom: 20px;
  padding: 1.2rem !important;
  border: 1px solid rgba(0,0,0,0.07);
}

.custom-card:hover {
  background: #eef2f4 !important;
}

.card-content {
  display: flex;
  flex-direction: column;
}

/* TÍTULO (verde) */
.custom-title-card {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  color: #1ED96F;
}

/* SUBTÍTULO (nome da disciplina) */
.custom-subtitle-card {
  font-weight: 700 !important;
  color: #4F5873 !important;
  font-size: 1.3rem !important;
  margin-top: 0.3rem;
}

/* CURSOS (linha inferior) */
.custom-description-card {
  color: #4F5873;
  font-size: 1.1rem;
  margin-top: 0.3rem;
}

@media only screen and (max-width: 600px) {
  .instruction {
    font-size: 1.4em;
  }
  .custom-title-card {
    font-size: 1.3rem !important;
  }
}
</style>