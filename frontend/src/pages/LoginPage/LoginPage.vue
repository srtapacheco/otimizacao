<template>
  <div class="container">
    <div class="title">
      <i class="fa-solid fa-calendar-check fa calendar-icon"></i>
      <h1> Calendário Unificado</h1>
    </div>

    <div class="login">
      <h2>Login</h2>
      <form @submit.prevent="login">
        <div class="input-container">
          <i class="fa-solid fa-user user-icon"></i>
          <input type="text" v-model="user.username" placeholder="Digite seu usuário" required>
        </div>
        <div class="input-container">
          <i class="fa-solid fa-lock password-icon"></i>
          <input type="password" v-model="user.password" placeholder="Digite sua senha" required>
        </div>
        <div class="login-actions">
          <button type="submit" class="login-button">
            <i class="fas fa-sign-in-alt"></i> Entrar
          </button>
          <a href="#" class="forgot-password">Esqueci minha senha</a>
        </div>
      </form>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: {
        username: "",
        password: ""
      }
    };
  },

  methods: {
    async login() {
      const CPF_CORRETO = "12345678910";
      const SENHA_CORRETA = "12345678910q";

      // valida o login mockado
      if (this.user.username === CPF_CORRETO && this.user.password === SENHA_CORRETA) {

        // usuário fake
        const usuario = {
          username: "Professor Luidi",
          email: "mock@exemplo.com",
          perfil: "aluno"
        };

        const token = "TOKEN_FAKE_123456";

        // salva no localStorage
        window.localStorage.setItem("NOME", usuario.username);
        window.localStorage.setItem("EMAIL", usuario.email);
        window.localStorage.setItem("PERFIL", usuario.perfil);
        window.localStorage.setItem("TOKEN", token);

        // redireciona
        this.$router.push("./home");
      } else {
        alert("CPF ou senha inválidos para teste (use 12345678910 / 12345678910q)");
      }
    }
  }
};
</script>

<style scoped src="./style.css"></style>