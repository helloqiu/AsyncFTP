<template>
  <div id="index">
    <div class="columns">
      <div class="column is-10-mobile is-offset-1-mobile is-8-tablet is-offset-2-tablet info-container">
        <div class="box info-box index-box">
          <h1 class="title">主机信息</h1>
          <table class="table is-striped">
            <thead>
              <tr>
                <th>项目名</th>
                <th>值</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>主机</td>
                <td>{{ this.info.host }}</td>
              </tr>
              <tr>
                <td>端口</td>
                <td>{{ this.info.port }}</td>
              </tr>
              <tr>
                <td>版本</td>
                <td>{{ this.info.version }}</td>
              </tr>
              <tr>
                <td>运行时间</td>
                <td>{{ this.run_time }}</td>
              </tr>
              <tr>
                <td>主机上传速率</td>
                <td>{{ this.speed_up }}</td>
              </tr>
              <tr>
                <td>主机下载速率</td>
                <td>{{ this.speed_down }}</td>
              </tr>
            </tbody>
          </table>
          <h1 class="title">禁止 IP</h1>
          <table class="table is-striped">
            <thead>
              <tr>
                <th>NO.</th>
                <th>IP</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!this.has_refuse_ip()">
                <th>无</th>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import prettysize from 'prettysize'
export default {
  data () {
    return {
      info: {},
      speed: null,
      up_time: 0
    }
  },
  created () {
    this.$http.get('config')
    .then(response => response.json())
    .then((json) => {
      this.info = json
    })
    this.get_info()
    setInterval(this.get_info, 1000)
  },
  methods: {
    get_info () {
      this.$http.get('info')
      .then(response => response.json())
      .then((json) => {
        this.speed = json.speed
        this.up_time = json.up_time
      })
    },
    has_refuse_ip () {
      if (this.info.refuse_ip) {
        if (this.info.refuse_ip.length > 0) {
          return true
        }
        return false
      } else {
        return false
      }
    }
  },
  computed: {
    speed_up () {
      if (this.speed) {
        const up = prettysize(parseInt(this.speed.up))
        return `${up}/s`
      } else {
        return ''
      }
    },
    speed_down () {
      if (this.speed) {
        const down = prettysize(parseInt(this.speed.down))
        return `${down}/s`
      } else {
        return ''
      }
    },
    run_time () {
      if (this.up_time || this.up_time === 0) {
        let s = parseInt(this.up_time)
        let min = parseInt(s / 60)
        s = s % 60
        let hour = parseInt(min / 60)
        min = min % 60
        /* eslint no-unused-vars: 0 */
        const day = parseInt(hour / 24)
        hour = hour % 24
        return `${day} 天 ${hour} 小时 ${min} 分钟 ${s} 秒`
      } else {
        return ''
      }
    }
  }
}
</script>

<style>
#index {
  padding: 24px 0;
}
.index-box {
  padding: 12px 12px;
}
</style>
