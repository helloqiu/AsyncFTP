<template>
  <div class="log-pannel">
    <h1 class="title">系统输出</h1>
    <p v-if="log === '无'" class="log-pannel-none">
      无
    </p>
    <table class="table is-striped" v-else>
      <thead>
        <tr>
          <th>NO</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(msg, index) of log">
          <td>{{ index }}</td>
          <td>{{ msg }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: ['log']
}
</script>

<style>
.log-pannel {
  margin-bottom: 1.5rem;
}
.log-pannel-none {
  margin-left: 12px;
}
</style>
