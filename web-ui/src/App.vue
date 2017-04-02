<template>
  <div id="app">
    <nav class="nav has-shadow">
      <div class="nav-left">
        <a href="/" class="nav-item">
          <i class="fa fa-server nav-icon" aria-hidden="true"></i>
          AsyncFTP WEB GUI
        </a>
      </div>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'app'
}
</script>

<style>
  html, body, #app {
    height: 100%;
    width: 100%;
  }
  .nav-icon {
    margin-right: 12px;
  }
</style>
