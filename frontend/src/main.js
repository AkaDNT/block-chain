import { createApp } from "vue";
import App from "./App.vue";
import blockchain from "./utils/blockchain.js";
import "./assets/style.css";

const app = createApp(App);
app.config.globalProperties.$blockchain = blockchain;

blockchain.initialize().finally(() => {
  app.mount("#app");
});
