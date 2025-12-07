<template>
  <v-app>
    <HeaderComponent />
    <v-main>
      <div class="external">
        <div class="container">
          <h2>Suas disciplinas</h2>
          <div class="card-container" v-for="turma in turmasInscrito" :key="turma.codigo">
            <v-card elevation="0" class="custom-card" @click="detalhesDisciplina(turma.codigo)">
              <div class="card-content">
                <v-card-title class="custom-title-card">{{ turma.codigo }}</v-card-title>
                <div class="delete-icon-container">
                  <v-icon class="custom-delete-icon" @click.stop="toggleDeleteConfirmation(turma)"
                    :class="{ 'disabled': turma.showDeleteConfirmation }">mdi-trash-can-outline</v-icon>
                </div>
              </div>
              <v-card-subtitle class="custom-subtitle-card">{{ turma.nome }}</v-card-subtitle>
              <v-card-text class="custom-courses-card">{{ turma.courses }}</v-card-text>
            </v-card>
          </div>
        </div>
      </div>
      <ModalConfirmation :show-modal="showModal" @confirm-delete="deleteCardConfirmation()" />
      <v-btn class="add-button" icon>
        <v-icon class="custom-icon-add" @click="addTurma()">mdi-plus</v-icon>
      </v-btn>
    </v-main>
  </v-app>
</template>


<script>
import HeaderComponent from '../../components/HeaderComponent.vue';
import ModalConfirmation from '@/components/ModalConfirmation.vue';

export default {
  components: {
    HeaderComponent,
    ModalConfirmation
  },

  data() {
    return {
      username: window.localStorage.getItem('NOME'),
      perfil: window.localStorage.getItem('PERFIL'),

      // MOCK DAS DISCIPLINAS 
      turmasInscrito: [
      {
        codigo: "COS360-A",
        nome: "Otimização",
        courses: "Engenharia de Computação, Engenharia de Controle e Automação",
        showDeleteConfirmation: false
      },
      {
        codigo: "COS123-A",
        nome: "Estruturas de Dados",
        courses: "Engenharia de Computação",
        showDeleteConfirmation: false
      }
      ],


      drawer: false,
      showModal: false,
      selectedDiscipline: null,
      isModalVisible: false
    };
  },

  created() {
    console.log("Disciplinas mockadas carregadas");
  },

  methods: {
    deleteCard(turma) {
      this.selectedDiscipline = turma;
      this.showModal = true;
    },

    cancelDeleteCard() {
      if (this.selectedDiscipline) {
        this.selectedDiscipline.showDeleteConfirmation = false;
        this.selectedDiscipline = null;
      }
      this.showModal = false;
    },

    toggleDeleteConfirmation(turma) {
      if (!turma.showDeleteConfirmation) {
        turma.showDeleteConfirmation = true;
        this.selectedDiscipline = turma;
        this.showModal = true;
      } else {
        turma.showDeleteConfirmation = false;
        this.cancelDeleteCard();
      }
    },

    deleteCardConfirmation() {
      const index = this.turmasInscrito.findIndex(item => item.codigo === this.selectedDiscipline.codigo);
      if (index !== -1) {
        this.turmasInscrito.splice(index, 1);
      }

      this.showModal = false;
    },

    addTurma() {
      if (this.perfil === "aluno") {
        this.$router.push("/disciplinas/inscricao");
      } else {
        this.$router.push({ name: "Editar Disciplina", params: { codigoTurma: "new" } });
      }
    },

    detalhesDisciplina(codigoTurma) {
      this.$router.push({
        name: "Detalhes Disciplina",
        params: { codigoTurma }
      });
    }
  }
};
</script>


<style src="./style.css" scoped></style>