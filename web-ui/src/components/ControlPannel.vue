<template>
  <div class="control-pannel">
    <h1 class="title">控制台</h1>
      <div class="block">
        <button class="button is-primary" v-on:click="start">启动服务器</button>
        <button class="button is-danger" v-on:click="stop">关闭服务器</button>
      </div>
      <div class="notification" v-if="show_start_notification">
        <button class="delete" v-on:click="close_start_notify"></button>
        启动服务器成功
      </div>
      <div class="notification" v-if="show_stop_notification">
        <button class="delete" v-on:click="close_stop_notify"></button>
        关闭服务器成功
      </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      show_start_notification: false,
      show_stop_notification: false
    }
  },
  methods: {
    start () {
      this.$http.get('start')
      .then(response => {
        if (response.body === 'ok') {
          this.show_start_notification = true
        }
      })
    },
    stop () {
      this.$http.get('stop')
      .then(response => {
        if (response.body === 'ok') {
          this.show_stop_notification = true
        }
      })
    },
    close_start_notify () {
      this.show_start_notification = false
    },
    close_stop_notify () {
      this.show_stop_notification = false
    }
  }
}
</script>

<style>
.control-pannel {
  margin-bottom: 1.5rem;
}
</style>
