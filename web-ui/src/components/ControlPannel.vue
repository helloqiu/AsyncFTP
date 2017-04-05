<template>
  <div class="control-pannel">
    <h1 class="title">控制台</h1>
      <div class="block">
        <button class="button is-primary" v-if="running" disabled>启动服务器</button>
        <button class="button is-primary" v-on:click="start" v-else v-bind:class="{ 'is-loading': starting }">启动服务器</button>
        <button class="button is-danger" v-on:click="stop" v-if="running" v-bind:class="{ 'is-loading': stopping }">关闭服务器</button>
         <button class="button is-danger" v-else disabled>关闭服务器</button>
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
      show_stop_notification: false,
      starting: false,
      stopping: false
    }
  },
  props: [
    'running'
  ],
  methods: {
    start () {
      this.starting = true
      this.$http.get('start')
      .then(response => {
        if (response.body === 'ok') {
          this.show_start_notification = true
          this.starting = false
        }
      })
    },
    stop () {
      this.stopping = true
      this.$http.get('stop')
      .then(response => {
        if (response.body === 'ok') {
          this.show_stop_notification = true
          this.stopping = false
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
